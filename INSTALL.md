# Guía de Instalación Local - VB/C# Bridge

## 📦 Descarga e Instalación

Esta guía te ayudará a instalar y ejecutar VB/C# Bridge en tu máquina local.

## Prerequisitos

### Software Necesario

1. **Python 3.11 o superior**
   - Descargar: https://www.python.org/downloads/
   - Verificar: `python --version`

2. **Node.js 18 o superior**
   - Descargar: https://nodejs.org/
   - Verificar: `node --version`

3. **Yarn Package Manager**
   ```bash
   npm install -g yarn
   ```

4. **MongoDB** (opcional para almacenamiento)
   - Descargar: https://www.mongodb.com/try/download/community
   - O usar MongoDB Atlas (cloud)

## Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes git
git clone <repository-url>
cd vb-csharp-bridge

# O descarga el ZIP y extrae
```

### 2. Configurar Backend

```bash
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno Backend

Crea o edita el archivo `backend/.env`:

```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=transpiler_db
CORS_ORIGINS=http://localhost:3000
```

### 4. Configurar Frontend

```bash
# Abrir nueva terminal y navegar a frontend
cd frontend

# Instalar dependencias
yarn install
```

### 5. Configurar Variables de Entorno Frontend

Crea o edita el archivo `frontend/.env`:

```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Ejecutar la Aplicación

### Opción 1: Ejecución Manual (2 terminales)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # o venv\Scripts\activate en Windows
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Opción 2: Script de Inicio Automático

**Windows (start.bat):**
```batch
@echo off
echo Iniciando VB/C# Bridge...

start cmd /k "cd backend && venv\Scripts\activate && uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
start cmd /k "cd frontend && yarn start"

echo Aplicacion iniciada!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8001
```

**Mac/Linux (start.sh):**
```bash
#!/bin/bash
echo "Iniciando VB/C# Bridge..."

# Backend
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &

# Frontend
cd ../frontend
yarn start &

echo "Aplicacion iniciada!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8001"
```

## Configuración de MongoDB (Opcional)

### MongoDB Local

1. Instala MongoDB Community Edition
2. Inicia el servicio:
   ```bash
   # Windows
   net start MongoDB
   
   # Mac
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

### MongoDB Atlas (Cloud)

1. Crea cuenta en https://www.mongodb.com/cloud/atlas
2. Crea un cluster gratuito
3. Obtén la connection string
4. Actualiza `backend/.env`:
   ```bash
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DB_NAME=transpiler_db
   ```

## Configuración MCP (Opcional)

Si deseas usar transpilación con IA:

### 1. Configurar Servidor MCP

Puedes usar cualquier servidor MCP compatible. Ejemplo con FastMCP:

```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("transpiler-agent")

@mcp.tool()
async def transpile_with_ai(context: dict, task: str) -> str:
    """Transpile code using AI with AST context"""
    # Tu lógica de IA aquí
    # Puedes usar OpenAI, Claude, etc.
    return transpiled_code

if __name__ == "__main__":
    mcp.run(transport='http', port=8080)
```

### 2. Ejecutar Servidor MCP

```bash
python mcp_server.py
```

### 3. Configurar en la UI

1. Abre la aplicación
2. Haz clic en el ícono de configuración ⚙️
3. Habilita MCP
4. URL: `http://localhost:8080`
5. Prueba la conexión

## Solución de Problemas

### Backend no inicia

**Error: "ModuleNotFoundError"**
```bash
# Asegúrate de tener el venv activado
pip install -r requirements.txt
```

**Error: "Port 8001 already in use"**
```bash
# Cambiar puerto en comando uvicorn
uvicorn server:app --port 8002
# Y actualizar frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8002
```

### Frontend no inicia

**Error: "Command not found: yarn"**
```bash
npm install -g yarn
```

**Error: "Port 3000 already in use"**
```bash
# Yarn te preguntará si quieres usar otro puerto
# O configurar en package.json:
"start": "PORT=3001 craco start"
```

### MongoDB no conecta

**Solución 1: Usar sin MongoDB**
```bash
# El transpilador funciona sin base de datos
# Solo omite las colecciones de MongoDB
```

**Solución 2: Verificar servicio**
```bash
# Verificar si MongoDB está corriendo
# Windows
sc query MongoDB

# Mac/Linux
sudo systemctl status mongod
```

### Errores de CORS

Si ves errores de CORS en la consola:

1. Verifica que `backend/.env` tenga:
   ```bash
   CORS_ORIGINS=http://localhost:3000
   ```

2. Reinicia el backend

## Actualización

Para actualizar a una nueva versión:

```bash
# Backend
cd backend
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
yarn upgrade
```

## Desinstalación

```bash
# Eliminar entorno virtual
rm -rf backend/venv

# Eliminar node_modules
rm -rf frontend/node_modules

# Eliminar carpeta completa
cd ..
rm -rf vb-csharp-bridge
```

## Recursos Adicionales

- **Documentación API**: http://localhost:8001/docs (cuando el backend esté corriendo)
- **README Principal**: Ver README.md para características completas
- **Issues**: Reportar problemas en el repositorio

## Contacto y Soporte

Para preguntas o problemas:
1. Revisa esta guía de instalación
2. Consulta el README.md
3. Verifica los logs del backend y frontend
4. Contacta al equipo de desarrollo

---

**¡Listo para transpilar código! 🚀**