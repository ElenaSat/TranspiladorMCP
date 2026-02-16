# Integración MCP (Model Context Protocol)

## 📋 Descripción General

VB/C# Bridge soporta integración con servidores MCP para mejorar la transpilación mediante IA. El sistema inyecta automáticamente el AST (Abstract Syntax Tree) y árbol semántico al contexto del agente MCP.

## 🔌 ¿Qué es MCP?

Model Context Protocol (MCP) es un protocolo estándar abierto que permite a modelos de IA conectarse universalmente a fuentes de datos externas, herramientas, bases de datos y APIs a través de un protocolo unificado.

**Beneficios:**
- Compatibilidad universal entre diferentes proveedores de IA
- Eliminación de integraciones personalizadas para cada proveedor
- Mejor manejo de contexto y estado en conversaciones
- Soporte para streaming en tiempo real

## 🏗️ Arquitectura de Integración

```
┌─────────────────┐
│   VB/C# Bridge  │
│    Frontend     │
└────────┬────────┘
         │ 1. User submits code
         ▼
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
         │ 2. Parse code → Generate AST
         │ 3. Build semantic tree
         ▼
┌─────────────────┐
│  MCP Injection  │ ◄── Configuration (URL + API Key)
│     Module      │
└────────┬────────┘
         │ 4. Inject context + Send request
         ▼
┌─────────────────┐
│   MCP Server    │
│  (User's own)   │
└────────┬────────┘
         │ 5. AI processes with context
         │ 6. Returns transpiled code
         ▼
┌─────────────────┐
│   Frontend UI   │
│ (Display result)│
└─────────────────┘
```

## 🛠️ Implementación Backend

### Endpoint de Inyección MCP

El backend incluye una función `call_mcp_server` en `server.py`:

```python
async def call_mcp_server(
    server_url: str, 
    api_key: Optional[str], 
    ast_data: Dict, 
    source_code: str, 
    source_lang: str, 
    target_lang: str
) -> Dict:
    """Call MCP server with AST context for AI-powered transpilation"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "context": {
                "ast": ast_data,              # Árbol sintáctico completo
                "source_code": source_code,    # Código fuente original
                "source_language": source_lang,
                "target_language": target_lang
            },
            "task": f"Transpile the provided {source_lang} code to {target_lang}"
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
```

### Formato de Contexto Inyectado

El contexto enviado al servidor MCP incluye:

```json
{
  "context": {
    "ast": {
      "id": "root",
      "type": "compilation_unit",
      "text": "Public Class Calculator...",
      "start_line": 0,
      "end_line": 10,
      "children": [
        {
          "id": "abc123",
          "type": "class_declaration",
          "text": "Public Class Calculator",
          "start_line": 1,
          "end_line": 9,
          "children": [...]
        }
      ]
    },
    "source_code": "Public Class Calculator\n    Public Function Add(...)",
    "source_language": "vbnet",
    "target_language": "csharp"
  },
  "task": "Transpile the provided vbnet code to csharp. Use the AST context provided."
}
```

## 🖥️ Implementación del Servidor MCP

### Ejemplo con FastMCP (Python)

```python
# mcp_transpiler_server.py
from mcp.server.fastmcp import FastMCP
import openai  # o cualquier LLM

mcp = FastMCP("vb-csharp-transpiler")

@mcp.tool()
async def transpile_with_context(context: dict, task: str) -> dict:
    """
    Transpile code using AI with full AST context
    
    Args:
        context: Dictionary containing ast, source_code, source_language, target_language
        task: Description of the transpilation task
    
    Returns:
        Dictionary with transpiled_code
    """
    
    ast = context.get('ast', {})
    source_code = context.get('source_code', '')
    source_lang = context.get('source_language', '')
    target_lang = context.get('target_language', '')
    
    # Construir prompt para LLM con contexto AST
    prompt = f"""
You are an expert code transpiler. You have been provided with:

1. SOURCE CODE ({source_lang}):
```
{source_code}
```

2. ABSTRACT SYNTAX TREE (AST):
```json
{ast}
```

3. TASK: {task}

Using the AST structure to understand the code semantics deeply, transpile the source code 
from {source_lang} to {target_lang}. Ensure:
- Correct syntax conversion
- Type mapping accuracy
- Method signature preservation
- Comment translation
- Idiom adaptation to target language

Provide ONLY the transpiled code without explanations.
"""
    
    # Llamar a LLM (ejemplo con OpenAI)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a code transpiler expert."},
            {"role": "user", "content": prompt}
        ]
    )
    
    transpiled_code = response.choices[0].message.content
    
    return {
        "result": transpiled_code,
        "transpiled_code": transpiled_code,
        "method": "mcp-ai",
        "model_used": "gpt-4"
    }

if __name__ == "__main__":
    # Servidor HTTP en puerto 8080
    mcp.run(transport='http', port=8080, host='0.0.0.0')
```

### Ejecutar Servidor MCP

```bash
# Instalar dependencias
pip install fastmcp openai httpx

# Ejecutar servidor
python mcp_transpiler_server.py

# Servidor disponible en: http://localhost:8080
```

### Ejemplo con Express (Node.js/TypeScript)

```typescript
// mcp-server.ts
import express from 'express';
import { Configuration, OpenAIApi } from 'openai';

const app = express();
app.use(express.json());

const openai = new OpenAIApi(
  new Configuration({ apiKey: process.env.OPENAI_API_KEY })
);

app.post('/mcp', async (req, res) => {
  try {
    const { context, task } = req.body;
    const { ast, source_code, source_language, target_language } = context;
    
    const prompt = `
You are an expert code transpiler with AST analysis capabilities.

SOURCE CODE (${source_language}):
\`\`\`
${source_code}
\`\`\`

AST STRUCTURE:
\`\`\`json
${JSON.stringify(ast, null, 2)}
\`\`\`

TASK: ${task}

Transpile to ${target_language} using the AST for semantic understanding.
`;
    
    const response = await openai.createChatCompletion({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a code transpiler expert.' },
        { role: 'user', content: prompt }
      ]
    });
    
    const transpiledCode = response.data.choices[0].message?.content || '';
    
    res.json({
      success: true,
      result: transpiledCode,
      transpiled_code: transpiledCode,
      method: 'mcp-ai'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(8080, () => {
  console.log('MCP Server running on http://localhost:8080');
});
```

## 🔐 Autenticación y Seguridad

### Configuración de API Key

El sistema soporta autenticación mediante Bearer token:

```bash
# En la UI de VB/C# Bridge
Server URL: https://your-mcp-server.com/api
API Key: sk-your-secret-key-here
```

El backend envía:
```http
POST /mcp HTTP/1.1
Host: your-mcp-server.com
Authorization: Bearer sk-your-secret-key-here
Content-Type: application/json
```

### Mejores Prácticas de Seguridad

1. **HTTPS Obligatorio**: Usar siempre HTTPS para servidores MCP en producción
2. **Rate Limiting**: Implementar límites de tasa en el servidor MCP
3. **Validación de Input**: Validar todo el código y contexto recibido
4. **Timeouts**: Configurar timeouts adecuados (30s en VB/C# Bridge)
5. **API Key Rotation**: Rotar API keys periódicamente

## 📊 Flujo de Transpilación con MCP

### 1. Usuario Habilita MCP
```javascript
// Frontend
setMcpEnabled(true);
setMcpConfig({
  server_url: 'https://my-mcp-server.com/api',
  api_key: 'sk-xxxxx'
});
```

### 2. Transpilación con Inyección de Contexto
```javascript
// Request al backend
const response = await axios.post('/api/transpile', {
  code: sourceCode,
  source_lang: 'vbnet',
  target_lang: 'csharp',
  use_mcp: true,  // ← Habilitar MCP
  mcp_config: mcpConfig
});
```

### 3. Backend Parsea y Envía a MCP
```python
# Backend procesa
ast_data = parse_code_to_ast(code, source_lang)
semantic_tree = build_semantic_tree(ast_data)

# Llama a MCP con contexto completo
mcp_response = await call_mcp_server(
    mcp_config['server_url'],
    mcp_config['api_key'],
    ast_data,
    code,
    source_lang,
    target_lang
)
```

### 4. MCP Procesa con IA
```python
# Servidor MCP usa LLM con contexto AST
transpiled = await llm.complete(prompt_with_ast_context)
return {"transpiled_code": transpiled}
```

### 5. Resultado en Frontend
```javascript
// UI muestra código transpilado con badge "mcp-ai"
setTranspiledCode(response.data.transpiled_code);
setTranspileMethod('mcp-ai');
```

## 🧪 Probar Conexión MCP

### Test de Conexión Integrado

La UI incluye un botón "Probar Conexión" que ejecuta:

```javascript
const testMCPConnection = async () => {
  const response = await axios.post('/api/mcp/test', mcpConfig);
  if (response.data.success) {
    toast.success('Conexión MCP exitosa');
  } else {
    toast.error(response.data.message);
  }
};
```

### Test Manual con cURL

```bash
# Test de conexión básico
curl -X GET http://localhost:8080 \
  -H "Authorization: Bearer your-api-key"

# Test de transpilación
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "context": {
      "ast": {"type": "compilation_unit"},
      "source_code": "Public Class Test\nEnd Class",
      "source_language": "vbnet",
      "target_language": "csharp"
    },
    "task": "Transpile VB.NET to C#"
  }'
```

## 🔄 Fallback a Reglas

Si MCP falla, el sistema automáticamente usa transpilación basada en reglas:

```python
try:
    # Intentar MCP primero
    if use_mcp and mcp_config:
        mcp_response = await call_mcp_server(...)
        if mcp_response.get('success'):
            return TranspileResponse(
                success=True,
                transpiled_code=mcp_response.get('transpiled_code'),
                method="mcp-ai"
            )
except Exception as e:
    logger.error(f"MCP failed: {e}")

# Fallback a reglas
transpiled, warnings, errors = transpile_rule_based(...)
return TranspileResponse(
    success=True,
    transpiled_code=transpiled,
    method="rule-based"
)
```

## 📈 Ventajas de MCP vs Solo Reglas

| Aspecto | Solo Reglas | Con MCP + IA |
|---------|-------------|--------------|
| **Cobertura** | Limitada a patrones conocidos | Maneja casos complejos |
| **Contexto** | Sintaxis básica | Comprensión semántica profunda |
| **Idioms** | Conversión literal | Adaptación idiomática |
| **Comentarios** | Sin traducción | Traduce y adapta |
| **Edge Cases** | Puede fallar | Mejor manejo |
| **Precisión** | 60-70% | 85-95% |
| **Latencia** | <100ms | 2-5s |
| **Costo** | Gratis | Uso de API LLM |

## 🚀 Servidores MCP Recomendados

### Opciones Open Source
1. **FastMCP** (Python) - https://github.com/anthropics/fastmcp
2. **MCP TypeScript SDK** - https://github.com/modelcontextprotocol/typescript-sdk
3. **MCP Server Template** - https://github.com/modelcontextprotocol/servers

### Servicios Cloud
1. **Anthropic Claude Code** - Soporte nativo MCP
2. **OpenAI GPT-4** - Vía wrapper MCP
3. **Custom Cloud Functions** - Deploy tu propio servidor

## 🎯 Casos de Uso Ideales para MCP

✅ **Usar MCP cuando:**
- Necesitas alta precisión en conversiones complejas
- Trabajas con código legacy con patrones únicos
- Requieres traducción de comentarios y documentación
- El código tiene lógica de negocio específica del dominio
- Necesitas adaptación idiomática, no solo sintáctica

❌ **Usar solo reglas cuando:**
- El código es simple y directo
- Necesitas latencia mínima
- Trabajas offline sin conexión
- Tienes limitaciones de costo de API
- El código sigue patrones estándar

## 📚 Recursos Adicionales

- [Model Context Protocol Spec](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/anthropics/fastmcp)
- [MCP Best Practices 2026](https://www.cdata.com/blog/mcp-server-best-practices-2026)
- [Tree-sitter Parsers](https://tree-sitter.github.io/tree-sitter/)

---

**Para más información, consulta README.md o contacta al equipo de desarrollo.**
