import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import axios from 'axios';
import { ArrowRightLeft, Settings, Download, Code2, Eye, AlertCircle, Loader2 } from 'lucide-react';
import CodeEditor from './CodeEditor';
import ASTViewer from './ASTViewer';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LANGUAGES = [
  { value: 'vb', label: 'Visual Basic 6' },
  { value: 'vbnet', label: 'VB.NET' },
  { value: 'csharp', label: 'C#' },
];

const SAMPLE_CODE = {
  vb: `' Visual Basic 6 Sample\nPublic Class Calculator\n    Public Function Add(a As Integer, b As Integer) As Integer\n        Add = a + b\n    End Function\nEnd Class`,
  vbnet: `' VB.NET Sample\nPublic Class Calculator\n    Public Function Add(a As Integer, b As Integer) As Integer\n        Return a + b\n    End Function\nEnd Class`,
  csharp: `// C# Sample\npublic class Calculator\n{\n    public int Add(int a, int b)\n    {\n        return a + b;\n    }\n}`,
};

const TranspilerWorkspace = () => {
  const [sourceCode, setSourceCode] = useState(SAMPLE_CODE.vbnet);
  const [transpiledCode, setTranspiledCode] = useState('');
  const [sourceLang, setSourceLang] = useState('vbnet');
  const [targetLang, setTargetLang] = useState('csharp');
  const [astData, setAstData] = useState(null);
  const [semanticTree, setSemanticTree] = useState(null);
  const [showAST, setShowAST] = useState(false);
  const [isTranspiling, setIsTranspiling] = useState(false);
  const [warnings, setWarnings] = useState([]);
  const [errors, setErrors] = useState([]);
  const [mcpEnabled, setMcpEnabled] = useState(false);
  const [mcpConfig, setMcpConfig] = useState({
    server_url: '',
    api_key: '',
  });
  const [mcpDialogOpen, setMcpDialogOpen] = useState(false);
  const [transpileMethod, setTranspileMethod] = useState('rule-based');

  // Auto-validate on code change
  useEffect(() => {
    const timer = setTimeout(() => {
      if (sourceCode.trim()) {
        validateCode();
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [sourceCode, sourceLang]);

  const validateCode = async () => {
    try {
      const response = await axios.post(`${API}/validate`, {
        code: sourceCode,
        language: sourceLang,
      });
      if (response.data.errors.length > 0) {
        setErrors(response.data.errors);
      } else {
        setErrors([]);
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const handleTranspile = async () => {
    if (!sourceCode.trim()) {
      toast.error('Por favor ingresa código fuente');
      return;
    }

    if (sourceLang === targetLang) {
      toast.warning('El lenguaje origen y destino son iguales');
      return;
    }

    setIsTranspiling(true);
    setWarnings([]);
    setErrors([]);

    try {
      // First, get AST
      const parseResponse = await axios.post(`${API}/parse`, {
        code: sourceCode,
        source_lang: sourceLang,
      });

      if (parseResponse.data.success) {
        setAstData(parseResponse.data.ast);
        setSemanticTree(parseResponse.data.semantic_tree);
      }

      // Then transpile
      const transpileResponse = await axios.post(`${API}/transpile`, {
        code: sourceCode,
        source_lang: sourceLang,
        target_lang: targetLang,
        use_mcp: mcpEnabled,
        mcp_config: mcpEnabled ? mcpConfig : null,
      });

      if (transpileResponse.data.success) {
        setTranspiledCode(transpileResponse.data.transpiled_code || '');
        setTranspileMethod(transpileResponse.data.method);
        setWarnings(transpileResponse.data.warnings || []);
        toast.success(
          `Transpilación completada (${transpileResponse.data.method})`
        );

        if (transpileResponse.data.warnings.length > 0) {
          transpileResponse.data.warnings.forEach((warning) => {
            toast.warning(warning);
          });
        }
      } else {
        setErrors(transpileResponse.data.errors || ['Error desconocido']);
        toast.error('Error en la transpilación');
        transpileResponse.data.errors.forEach((error) => {
          toast.error(error);
        });
      }
    } catch (error) {
      console.error('Transpilation error:', error);
      toast.error('Error al transpilar código');
      setErrors([error.message]);
    } finally {
      setIsTranspiling(false);
    }
  };

  const handleDownload = () => {
    if (!transpiledCode) {
      toast.warning('No hay código transpilado para descargar');
      return;
    }

    const extension = targetLang === 'csharp' ? 'cs' : 'vb';
    const blob = new Blob([transpiledCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transpiled_code.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Código descargado');
  };

  const testMCPConnection = async () => {
    if (!mcpConfig.server_url) {
      toast.error('Por favor ingresa la URL del servidor MCP');
      return;
    }

    try {
      const response = await axios.post(`${API}/mcp/test`, mcpConfig);
      if (response.data.success) {
        toast.success('Conexión MCP exitosa');
      } else {
        toast.error(response.data.message || 'Error de conexión MCP');
      }
    } catch (error) {
      toast.error('No se pudo conectar al servidor MCP');
    }
  };

  const handleSourceLangChange = (value) => {
    setSourceLang(value);
    setSourceCode(SAMPLE_CODE[value] || '');
  };

  return (
    <div className="h-screen w-full flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-16 border-b border-border bg-background/50 backdrop-blur-xl z-50 flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
            <Code2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">VB/C# Bridge</h1>
            <p className="text-xs text-muted-foreground">Transpilador de Código</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Language Selectors */}
          <div className="flex items-center gap-2">
            <Select value={sourceLang} onValueChange={handleSourceLangChange}>
              <SelectTrigger data-testid="source-language-selector" className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <ArrowRightLeft className="w-5 h-5 text-muted-foreground" />

            <Select value={targetLang} onValueChange={setTargetLang}>
              <SelectTrigger data-testid="target-language-selector" className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Transpile Button */}
          <Button
            data-testid="transpile-button"
            onClick={handleTranspile}
            disabled={isTranspiling}
            size="lg"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 transition-all duration-200 hover:scale-105"
          >
            {isTranspiling ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Transpilando...
              </>
            ) : (
              <>
                <ArrowRightLeft className="w-4 h-4 mr-2" />
                Transpilar
              </>
            )}
          </Button>

          {/* Action Buttons */}
          <Button
            data-testid="toggle-ast-button"
            variant="outline"
            size="icon"
            onClick={() => setShowAST(!showAST)}
            className="transition-all duration-200 hover:scale-105"
          >
            <Eye className="w-4 h-4" />
          </Button>

          <Button
            data-testid="download-button"
            variant="outline"
            size="icon"
            onClick={handleDownload}
            disabled={!transpiledCode}
            className="transition-all duration-200 hover:scale-105"
          >
            <Download className="w-4 h-4" />
          </Button>

          <Dialog open={mcpDialogOpen} onOpenChange={setMcpDialogOpen}>
            <DialogTrigger asChild>
              <Button
                data-testid="mcp-config-button"
                variant="outline"
                size="icon"
                className="transition-all duration-200 hover:scale-105"
              >
                <Settings className="w-4 h-4" />
              </Button>
            </DialogTrigger>
            <DialogContent data-testid="mcp-config-modal" className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Configuración MCP</DialogTitle>
                <DialogDescription>
                  Conecta tu agente MCP para transpilación mejorada con IA
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="mcp-enable">Habilitar MCP</Label>
                  <Switch
                    id="mcp-enable"
                    data-testid="mcp-enable-switch"
                    checked={mcpEnabled}
                    onCheckedChange={setMcpEnabled}
                  />
                </div>
                {mcpEnabled && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="server-url">URL del Servidor MCP</Label>
                      <Input
                        id="server-url"
                        data-testid="mcp-server-url-input"
                        placeholder="https://your-mcp-server.com/api"
                        value={mcpConfig.server_url}
                        onChange={(e) =>
                          setMcpConfig({ ...mcpConfig, server_url: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="api-key">API Key (Opcional)</Label>
                      <Input
                        id="api-key"
                        data-testid="mcp-api-key-input"
                        type="password"
                        placeholder="Tu API key"
                        value={mcpConfig.api_key}
                        onChange={(e) =>
                          setMcpConfig({ ...mcpConfig, api_key: e.target.value })
                        }
                      />
                    </div>
                    <Button
                      data-testid="test-mcp-connection-button"
                      variant="outline"
                      onClick={testMCPConnection}
                      className="w-full"
                    >
                      Probar Conexión
                    </Button>
                    <div className="text-xs text-muted-foreground mt-2 p-3 bg-muted/50 rounded-md">
                      <p className="font-semibold mb-1">Inyección de Contexto:</p>
                      <p>
                        El sistema enviará el AST y árbol semántico al servidor MCP junto
                        con el código fuente para una transpilación mejorada con IA.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Source Editor */}
        <div className="flex-1 flex flex-col min-w-[300px] border-r border-border">
          <div className="h-10 bg-card/50 border-b border-border px-4 flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">Código Fuente</span>
            {errors.length > 0 && (
              <Badge variant="destructive" className="text-xs">
                <AlertCircle className="w-3 h-3 mr-1" />
                {errors.length} error(es)
              </Badge>
            )}
          </div>
          <div className="flex-1 overflow-hidden">
            <CodeEditor
              value={sourceCode}
              onChange={setSourceCode}
              language={sourceLang === 'vbnet' ? 'vb' : sourceLang}
              testId="source-code-editor"
            />
          </div>
        </div>

        {/* Target Editor */}
        <div className="flex-1 flex flex-col min-w-[300px]">
          <div className="h-10 bg-card/50 border-b border-border px-4 flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">
              Código Transpilado
            </span>
            {transpileMethod && transpiledCode && (
              <Badge variant="secondary" className="text-xs">
                {transpileMethod}
              </Badge>
            )}
          </div>
          <div className="flex-1 overflow-hidden">
            <CodeEditor
              value={transpiledCode}
              onChange={setTranspiledCode}
              language={targetLang === 'csharp' ? 'csharp' : 'vb'}
              readOnly
              testId="transpiled-code-editor"
            />
          </div>
        </div>
      </div>

      {/* AST Viewer Panel */}
      {showAST && (
        <div className="h-[350px] border-t border-border bg-card/50">
          <div className="h-10 bg-card border-b border-border px-4 flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">
              Visualización de Árboles
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAST(false)}
              className="text-xs"
            >
              Cerrar
            </Button>
          </div>
          <div className="h-[calc(100%-40px)] overflow-hidden">
            <ASTViewer astData={astData} semanticTree={semanticTree} />
          </div>
        </div>
      )}

      {/* Warnings/Errors Bar */}
      {(warnings.length > 0 || errors.length > 0) && (
        <div className="border-t border-border bg-card/30 backdrop-blur-sm">
          <div className="max-h-32 overflow-y-auto p-4 space-y-2">
            {errors.map((error, idx) => (
              <div
                key={`error-${idx}`}
                className="text-xs text-red-400 flex items-start gap-2"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{typeof error === 'string' ? error : error.message}</span>
              </div>
            ))}
            {warnings.map((warning, idx) => (
              <div
                key={`warning-${idx}`}
                className="text-xs text-yellow-400 flex items-start gap-2"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{warning}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TranspilerWorkspace;