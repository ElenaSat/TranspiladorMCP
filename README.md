# VB/C# Bridge - Transpilador de Código

## 🎯 Descripción

VB/C# Bridge es un transpilador de código híbrido que permite convertir código entre Visual Basic 6, VB.NET y C#. El sistema combina reglas de transpilación tradicionales con capacidades de IA mediante integración MCP (Model Context Protocol).

## ✨ Características Principales

### 🔄 Transpilación Multi-Direccional
- **VB6 → VB.NET**: Moderniza código Visual Basic clásico
- **VB.NET → C#**: Convierte aplicaciones .NET a C#
- **C# → VB.NET**: Transpilación inversa para equipos VB.NET
- **VB6 → C#**: Conversión directa en dos pasos

### 🌲 Análisis de Código Avanzado
- **Árbol Sintáctico (AST)**: Visualización interactiva del AST generado por Tree-sitter
- **Árbol Semántico**: Análisis estructural de clases, métodos y propiedades
- **Validación en Tiempo Real**: Detección de errores mientras escribes (500ms debounce)

### 🤖 Integración MCP (Model Context Protocol)
- Conecta tu propio servidor MCP para transpilación mejorada con IA
- Inyección automática de contexto (AST + código fuente)
- Configuración flexible con autenticación opcional
- Prueba de conexión integrada

### 💻 Editor de Código Profesional
- Monaco Editor con resaltado de sintaxis
- Numeración de líneas y temas personalizados
- Fuente monoespaciada (JetBrains Mono)
- Vista comparativa lado a lado

### 📥 Funcionalidades Adicionales
- Descarga de código transpilado (.cs, .vb)
- Indicador de método de transpilación (rule-based / mcp-ai)
- Sistema de warnings y errores detallados
- Notificaciones toast para feedback inmediato

## 🏗️ Arquitectura

### Backend (FastAPI)
```
/app/backend/
├── server.py           # API principal con endpoints de transpilación
├── requirements.txt    # Dependencias Python
└── .env               # Variables de entorno
```

**Tecnologías:**
- FastAPI para API REST
- Tree-sitter para parsing de código
- Motor asyncio para llamadas MCP
- MongoDB para almacenamiento opcional

### Frontend (React)
```
/app/frontend/src/
├── App.js                          # Componente principal
├── components/
│   ├── TranspilerWorkspace.jsx    # Workspace principal
│   ├── CodeEditor.jsx             # Editor Monaco
│   └── ASTViewer.jsx              # Visualizador de árboles
└── App.css                        # Estilos globales
```

**Tecnologías:**
- React 19 con hooks
- Monaco Editor para edición de código
- ReactFlow para visualización de árboles
- Shadcn/UI para componentes
- Tailwind CSS para estilos

## 🚀 Uso

### 1. Transpilación Básica

1. Selecciona el lenguaje **origen** (VB, VB.NET, C#)
2. Selecciona el lenguaje **destino**
3. Escribe o pega tu código en el editor izquierdo
4. Haz clic en **"Transpilar"**
5. El código convertido aparecerá en el editor derecho

### 2. Visualización de Árboles

1. Después de transpilar, haz clic en el ícono de ojo 👁️
2. Se abrirá el panel inferior con dos pestañas:
   - **Árbol Sintáctico (AST)**: Estructura completa del código parseado
   - **Árbol Semántico**: Vista organizada de clases, métodos y propiedades
3. Usa los controles de ReactFlow para navegar (zoom, pan)

### 3. Configuración MCP

1. Haz clic en el ícono de configuración ⚙️
2. Activa el switch **"Habilitar MCP"**
3. Ingresa la URL de tu servidor MCP
4. (Opcional) Ingresa tu API key
5. Haz clic en **"Probar Conexión"** para verificar
6. Las transpilaciones usarán tu agente IA con contexto AST inyectado

### 4. Descargar Código

1. Después de transpilar, haz clic en el ícono de descarga 📥
2. El archivo se descargará con la extensión correcta (.cs o .vb)

## 🔌 API REST

### Endpoints Disponibles

#### `GET /api/`
Health check del API
```json
{ "message": "VB/C# Transpiler API v1.0" }
```

#### `POST /api/parse`
Parsea código y retorna AST
```json
{
  "code": "Public Class Test\n...",
  "source_lang": "vbnet"
}
```

#### `POST /api/transpile`
Transpila código entre lenguajes
```json
{
  "code": "Public Class Test\n...",
  "source_lang": "vbnet",
  "target_lang": "csharp",
  "use_mcp": false,
  "mcp_config": null
}
```

#### `POST /api/validate`
Valida sintaxis de código
```json
{
  "code": "Public Class Test\n...",
  "language": "vbnet"
}
```

#### `POST /api/mcp/test`
Prueba conexión con servidor MCP
```json
{
  "server_url": "https://your-mcp-server.com/api",
  "api_key": "optional-key"
}
```

## 🛠️ Desarrollo Local

### Prerequisitos
- Python 3.11+
- Node.js 18+
- MongoDB (para almacenamiento)

### Instalación Backend
```bash
cd /app/backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Instalación Frontend
```bash
cd /app/frontend
yarn install
yarn start
```

### Variables de Entorno

**Backend (.env)**
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=transpiler_db
CORS_ORIGINS=*
```

**Frontend (.env)**
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 📖 Reglas de Transpilación

### VB.NET → C#

| VB.NET | C# |
|--------|----|
| `Public Class X` | `public class X {` |
| `End Class` | `}` |
| `Public Sub Test()` | `public void Test() {` |
| `Function Test() As Integer` | `int Test() {` |
| `Dim x As Integer` | `int x;` |
| `If ... Then` | `if (...) {` |
| `' comentario` | `// comentario` |
| `&` (concatenación) | `+` |
| `AndAlso / OrElse` | `&& / ||` |

### C# → VB.NET

| C# | VB.NET |
|----|--------|
| `public class X {` | `Public Class X` |
| `}` | `End Class` |
| `public void Test()` | `Public Sub Test()` |
| `int Test()` | `Function Test() As Integer` |
| `int x;` | `Dim x As Integer` |
| `if (...)` | `If ... Then` |
| `// comentario` | `' comentario` |

### VB6 → VB.NET

Mínimos cambios, principalmente actualización de sintaxis obsoleta y compatibilidad de tipos.

## ⚠️ Limitaciones Conocidas

1. **Transpilación Basada en Reglas**: No todos los casos complejos están cubiertos
2. **Parsing Limitado**: Tree-sitter solo tiene parser completo para C#
3. **Conversiones Manuales**: Algunas conversiones requieren ajustes manuales post-transpilación
4. **MCP Externo**: Requiere servidor MCP propio del usuario

## 🎨 Diseño

### Paleta de Colores
- **Background**: `#09090b` (Negro profundo)
- **Foreground**: `#fafafa` (Blanco suave)
- **Primary**: `#3b82f6` (Azul)
- **Border**: `#27272a` (Gris oscuro)
- **Card**: `#18181b` (Negro elevado)

### Tipografía
- **UI**: Inter
- **Headings**: Manrope
- **Code**: JetBrains Mono

### Tema
Diseño oscuro profesional optimizado para desarrolladores con:
- Efecto glassmorphism en modales
- Animaciones suaves en hover
- Contraste alto para legibilidad
- Resaltado de sintaxis personalizado

## 🧪 Testing

El proyecto incluye tests exhaustivos:
- ✅ Todos los endpoints API funcionando
- ✅ Transpilación en todas las direcciones
- ✅ Visualización AST y árboles semánticos
- ✅ Configuración MCP y pruebas de conexión
- ✅ Descarga de archivos
- ✅ Validación en tiempo real

## 🤝 Contribución

Para contribuir al proyecto:
1. Agrega nuevas reglas de transpilación en `server.py`
2. Mejora los parsers para VB/VB.NET
3. Expande la visualización del AST
4. Optimiza el rendimiento para archivos grandes

## 📄 Licencia

Este proyecto fue creado con Emergent Agent.

## 🔗 Enlaces Útiles

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Tree-sitter Documentation](https://tree-sitter.github.io)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [ReactFlow](https://reactflow.dev)

---

**Desarrollado con ❤️ usando Emergent AI**