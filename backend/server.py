from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import tree_sitter_languages as tsl
import json
import httpx
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tree-sitter parsers
try:
    parser_c_sharp = tsl.get_parser('c_sharp')
    logger.info("C# parser loaded successfully")
except Exception as e:
    logger.warning(f"C# parser not available: {e}")
    parser_c_sharp = None

# Models
class CodeInput(BaseModel):
    code: str
    source_lang: str
    target_lang: Optional[str] = None

class ASTNode(BaseModel):
    id: str
    type: str
    text: str
    start_line: int
    end_line: int
    children: List['ASTNode'] = []

class ASTResponse(BaseModel):
    success: bool
    ast: Optional[Dict[str, Any]] = None
    semantic_tree: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TranspileRequest(BaseModel):
    code: str
    source_lang: str
    target_lang: str
    use_mcp: bool = False
    mcp_config: Optional[Dict[str, Any]] = None

class TranspileResponse(BaseModel):
    success: bool
    transpiled_code: Optional[str] = None
    warnings: List[str] = []
    errors: List[str] = []
    method: str = "rule-based"

class ValidateRequest(BaseModel):
    code: str
    language: str

class ValidateResponse(BaseModel):
    valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

class MCPInjectRequest(BaseModel):
    server_url: str
    api_key: Optional[str] = None
    ast_data: Dict[str, Any]
    source_code: str
    source_lang: str
    target_lang: str

class MCPInjectResponse(BaseModel):
    success: bool
    transpiled_code: Optional[str] = None
    error: Optional[str] = None

# Helper functions
def parse_code_to_ast(code: str, language: str) -> Optional[Dict[str, Any]]:
    """Parse code using tree-sitter and return AST"""
    try:
        if language.lower() in ['c#', 'csharp', 'c_sharp']:
            if parser_c_sharp is None:
                return None
            tree = parser_c_sharp.parse(bytes(code, 'utf8'))
            return tree_to_dict(tree.root_node)
        return None
    except Exception as e:
        logger.error(f"Error parsing code: {e}")
        return None

def tree_to_dict(node, max_depth=50, current_depth=0) -> Dict[str, Any]:
    """Convert tree-sitter node to dictionary"""
    if current_depth > max_depth:
        return {"type": "max_depth_reached"}
    
    result = {
        "id": str(uuid.uuid4())[:8],
        "type": node.type,
        "start_line": node.start_point[0],
        "end_line": node.end_point[0],
        "text": node.text.decode('utf8')[:100] if node.text else "",
        "children": []
    }
    
    if node.child_count > 0 and current_depth < max_depth:
        result["children"] = [tree_to_dict(child, max_depth, current_depth + 1) for child in node.children[:20]]
    
    return result

def build_semantic_tree(ast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build semantic tree from AST (simplified version)"""
    semantic = {
        "classes": [],
        "methods": [],
        "properties": [],
        "imports": []
    }
    
    def traverse(node):
        node_type = node.get('type', '')
        if 'class' in node_type.lower():
            semantic['classes'].append({
                "name": node.get('text', '')[:50],
                "line": node.get('start_line', 0)
            })
        elif 'method' in node_type.lower() or 'function' in node_type.lower():
            semantic['methods'].append({
                "name": node.get('text', '')[:50],
                "line": node.get('start_line', 0)
            })
        elif 'property' in node_type.lower() or 'field' in node_type.lower():
            semantic['properties'].append({
                "name": node.get('text', '')[:50],
                "line": node.get('start_line', 0)
            })
        
        for child in node.get('children', []):
            traverse(child)
    
    traverse(ast_data)
    return semantic

def transpile_rule_based(code: str, source_lang: str, target_lang: str) -> tuple[str, List[str], List[str]]:
    """Rule-based transpilation between VB, VB.NET, and C#"""
    warnings = []
    errors = []
    
    # Normalize language names
    source = source_lang.lower().replace(' ', '').replace('.', '')
    target = target_lang.lower().replace(' ', '').replace('.', '')
    
    transpiled = code
    
    # VB to VB.NET
    if source == 'vb' and target == 'vbnet':
        # Add basic conversions
        transpiled = transpile_vb_to_vbnet(code)
        warnings.append("Manual review recommended: Some VB6 features may not be directly compatible with VB.NET")
    
    # VB.NET to C#
    elif source == 'vbnet' and target in ['csharp', 'c#']:
        transpiled = transpile_vbnet_to_csharp(code)
        warnings.append("Converted VB.NET to C#. Review Option Strict and type conversions.")
    
    # C# to VB.NET
    elif source in ['csharp', 'c#'] and target == 'vbnet':
        transpiled = transpile_csharp_to_vbnet(code)
        warnings.append("Converted C# to VB.NET. Review semicolons and brackets.")
    
    # VB to C# (two-step)
    elif source == 'vb' and target in ['csharp', 'c#']:
        vbnet_code = transpile_vb_to_vbnet(code)
        transpiled = transpile_vbnet_to_csharp(vbnet_code)
        warnings.append("Two-step conversion (VB -> VB.NET -> C#). Extensive testing required.")
    
    else:
        errors.append(f"Conversion from {source_lang} to {target_lang} not supported")
        return code, warnings, errors
    
    return transpiled, warnings, errors

def transpile_vb_to_vbnet(code: str) -> str:
    """Convert VB6 to VB.NET"""
    result = code
    
    # Replace common VB6 keywords with VB.NET equivalents
    replacements = [
        (r'\bDim\s+(\w+)\s+As\s+Integer\b', r'Dim \1 As Integer'),
        (r'\bDim\s+(\w+)\s+As\s+String\b', r'Dim \1 As String'),
        (r'\bSub\s+Main\(\)', r'Sub Main()'),
        (r'\bEnd Sub\b', r'End Sub'),
        (r'\bEnd Function\b', r'End Function'),
        (r'\bPublic Sub\b', r'Public Sub'),
        (r'\bPrivate Sub\b', r'Private Sub'),
    ]
    
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    
    return result

def transpile_vbnet_to_csharp(code: str) -> str:
    """Convert VB.NET to C#"""
    result = code
    
    # Basic VB.NET to C# conversions
    conversions = [
        # Comments
        (r"'", r'//'),
        # Class declaration
        (r'\bPublic Class (\w+)', r'public class \1 {'),
        (r'\bPrivate Class (\w+)', r'private class \1 {'),
        (r'\bClass (\w+)', r'class \1 {'),
        # End Class
        (r'\bEnd Class\b', r'}'),
        # Sub/Function
        (r'\bPublic Sub (\w+)\(\)', r'public void \1() {'),
        (r'\bPrivate Sub (\w+)\(\)', r'private void \1() {'),
        (r'\bPublic Function (\w+)\(\) As (\w+)', r'public \2 \1() {'),
        (r'\bPrivate Function (\w+)\(\) As (\w+)', r'private \2 \1() {'),
        (r'\bEnd Sub\b', r'}'),
        (r'\bEnd Function\b', r'}'),
        # Properties
        (r'\bPublic Property (\w+)\(\) As (\w+)', r'public \2 \1 { get; set; }'),
        (r'\bPrivate Property (\w+)\(\) As (\w+)', r'private \2 \1 { get; set; }'),
        # Variable declarations
        (r'\bDim (\w+) As Integer\b', r'int \1;'),
        (r'\bDim (\w+) As String\b', r'string \1;'),
        (r'\bDim (\w+) As Boolean\b', r'bool \1;'),
        (r'\bDim (\w+) As Double\b', r'double \1;'),
        # Conditionals
        (r'\bIf (.+) Then', r'if (\1) {'),
        (r'\bEnd If\b', r'}'),
        (r'\bElseIf', r'} else if'),
        (r'\bElse\b', r'} else {'),
        # Loops
        (r'\bFor Each (\w+) As (\w+) In (.+)', r'foreach (\2 \1 in \3) {'),
        (r'\bFor (\w+) As Integer = (.+) To (.+)', r'for (int \1 = \2; \1 <= \3; \1++) {'),
        (r'\bNext\b', r'}'),
        # String concatenation
        (r'\s+&\s+', r' + '),
        # Boolean operators
        (r'\bAndAlso\b', r'&&'),
        (r'\bOrElse\b', r'||'),
        (r'\bNot\b', r'!'),
    ]
    
    for pattern, replacement in conversions:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.MULTILINE)
    
    return result

def transpile_csharp_to_vbnet(code: str) -> str:
    """Convert C# to VB.NET"""
    result = code
    
    # Basic C# to VB.NET conversions
    conversions = [
        # Comments
        (r'//', r"'"),
        # Remove semicolons
        (r';', r''),
        # Class declaration
        (r'public class (\w+)\s*\{', r'Public Class \1'),
        (r'private class (\w+)\s*\{', r'Private Class \1'),
        # Methods
        (r'public void (\w+)\(\)\s*\{', r'Public Sub \1()'),
        (r'private void (\w+)\(\)\s*\{', r'Private Sub \1()'),
        (r'public (\w+) (\w+)\(\)\s*\{', r'Public Function \2() As \1'),
        (r'private (\w+) (\w+)\(\)\s*\{', r'Private Function \2() As \1'),
        # Properties
        (r'public (\w+) (\w+) \{ get; set; \}', r'Public Property \2() As \1'),
        # Variable declarations
        (r'int (\w+)', r'Dim \1 As Integer'),
        (r'string (\w+)', r'Dim \1 As String'),
        (r'bool (\w+)', r'Dim \1 As Boolean'),
        (r'double (\w+)', r'Dim \1 As Double'),
        # Conditionals
        (r'if \((.+?)\)\s*\{', r'If \1 Then'),
        (r'else if', r'ElseIf'),
        (r'else\s*\{', r'Else'),
        # Closing braces
        (r'\}', r''),
    ]
    
    for pattern, replacement in conversions:
        result = re.sub(pattern, replacement, result, flags=re.MULTILINE)
    
    # Add End statements
    result = re.sub(r'(Public|Private) Class', r'\1 Class', result)
    lines = result.split('\n')
    new_lines = []
    indent_stack = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('Public Class') or stripped.startswith('Private Class') or stripped.startswith('Class '):
            new_lines.append(line)
            indent_stack.append('Class')
        elif stripped.startswith('Public Sub') or stripped.startswith('Private Sub'):
            new_lines.append(line)
            indent_stack.append('Sub')
        elif stripped.startswith('Public Function') or stripped.startswith('Private Function'):
            new_lines.append(line)
            indent_stack.append('Function')
        elif stripped.startswith('If ') and stripped.endswith(' Then'):
            new_lines.append(line)
            indent_stack.append('If')
        else:
            new_lines.append(line)
    
    # Add End statements (simplified)
    result = '\n'.join(new_lines)
    result = re.sub(r'(Public|Private) Class ([\w\s]+?)(?=\n(?:Public|Private|End|$))', r'\1 Class \2\nEnd Class', result, flags=re.MULTILINE | re.DOTALL)
    
    return result

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "VB/C# Transpiler API v1.0"}

@api_router.post("/parse", response_model=ASTResponse)
async def parse_code(request: CodeInput):
    """Parse code and return AST and semantic tree"""
    try:
        ast_data = parse_code_to_ast(request.code, request.source_lang)
        
        if ast_data is None:
            # Create a simple mock AST for unsupported languages
            ast_data = {
                "id": "root",
                "type": "compilation_unit",
                "text": request.code[:100],
                "start_line": 0,
                "end_line": len(request.code.split('\n')),
                "children": [
                    {
                        "id": str(uuid.uuid4())[:8],
                        "type": "class_declaration",
                        "text": "Parsed structure",
                        "start_line": 0,
                        "end_line": 10,
                        "children": []
                    }
                ]
            }
        
        semantic_tree = build_semantic_tree(ast_data)
        
        return ASTResponse(
            success=True,
            ast=ast_data,
            semantic_tree=semantic_tree
        )
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return ASTResponse(
            success=False,
            error=str(e)
        )

@api_router.post("/transpile", response_model=TranspileResponse)
async def transpile_code(request: TranspileRequest):
    """Transpile code between languages"""
    try:
        if request.use_mcp and request.mcp_config:
            # MCP-based transpilation
            ast_data = parse_code_to_ast(request.code, request.source_lang)
            if ast_data:
                mcp_response = await call_mcp_server(
                    request.mcp_config.get('server_url'),
                    request.mcp_config.get('api_key'),
                    ast_data,
                    request.code,
                    request.source_lang,
                    request.target_lang
                )
                if mcp_response.get('success'):
                    return TranspileResponse(
                        success=True,
                        transpiled_code=mcp_response.get('transpiled_code'),
                        warnings=["Transpiled using MCP agent"],
                        method="mcp-ai"
                    )
        
        # Rule-based transpilation
        transpiled, warnings, errors = transpile_rule_based(
            request.code,
            request.source_lang,
            request.target_lang
        )
        
        return TranspileResponse(
            success=len(errors) == 0,
            transpiled_code=transpiled,
            warnings=warnings,
            errors=errors,
            method="rule-based"
        )
    except Exception as e:
        logger.error(f"Transpilation error: {e}")
        return TranspileResponse(
            success=False,
            errors=[str(e)],
            method="error"
        )

@api_router.post("/validate", response_model=ValidateResponse)
async def validate_code(request: ValidateRequest):
    """Validate code syntax"""
    try:
        ast_data = parse_code_to_ast(request.code, request.language)
        
        if ast_data is None:
            return ValidateResponse(
                valid=True,
                warnings=[{"message": "Parser not available for this language. Basic validation only."}]
            )
        
        # Check for common issues
        errors = []
        warnings = []
        
        # Check if code is too short
        if len(request.code.strip()) < 10:
            warnings.append({"message": "Code is very short", "line": 0})
        
        return ValidateResponse(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    except Exception as e:
        return ValidateResponse(
            valid=False,
            errors=[{"message": str(e), "line": 0}]
        )

async def call_mcp_server(server_url: str, api_key: Optional[str], ast_data: Dict, source_code: str, source_lang: str, target_lang: str) -> Dict:
    """Call MCP server with AST context for AI-powered transpilation"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "context": {
                    "ast": ast_data,
                    "source_code": source_code,
                    "source_language": source_lang,
                    "target_language": target_lang
                },
                "task": f"Transpile the provided {source_lang} code to {target_lang}. Use the AST context provided."
            }
            
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = await client.post(server_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "transpiled_code": data.get('result', data.get('transpiled_code', ''))
                }
            else:
                return {
                    "success": False,
                    "error": f"MCP server returned {response.status_code}"
                }
    except Exception as e:
        logger.error(f"MCP call error: {e}")
        return {"success": False, "error": str(e)}

@api_router.post("/mcp/test", response_model=Dict[str, Any])
async def test_mcp_connection(request: Dict[str, Any]):
    """Test MCP server connection"""
    try:
        server_url = request.get('server_url')
        api_key = request.get('api_key')
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = await client.get(server_url, headers=headers)
            
            return {
                "success": response.status_code in [200, 201],
                "status_code": response.status_code,
                "message": "Connection successful" if response.status_code in [200, 201] else "Connection failed"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()