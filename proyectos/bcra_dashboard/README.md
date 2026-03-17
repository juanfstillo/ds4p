# 📊 Dashboard BCRA - Indicadores Económicos de Argentina

MVP completo para el **Seminario: Ciencia de Datos para Politólogos/as** - UBA Ciencias Sociales

## 🎯 Descripción

Dashboard web interactivo que consume datos en tiempo real de la API del Banco Central de la República Argentina (BCRA), los almacena en una base de datos PostgreSQL, los expone mediante una API REST con FastAPI, y los visualiza con un frontend moderno usando Bootstrap y Chart.js.

## 🚀 Stack Tecnológico

- **Backend:** FastAPI (Python 3.10+)
- **Base de Datos:** PostgreSQL
- **ORM:** SQLAlchemy
- **Autenticación:** JWT (JSON Web Tokens)
- **Frontend:** HTML5 + Bootstrap 5 + Chart.js
- **Deployment:** Railway / Render / Heroku

## 📦 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd bcra-dashboard
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/bcra_dashboard

# Seguridad
SECRET_KEY=tu-secret-key-super-segura-cambiala
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración
DEBUG=True
```

### 5. Crear base de datos PostgreSQL

```bash
# Desde psql o pgAdmin
CREATE DATABASE bcra_dashboard;
```

### 6. Poblar la base de datos

```bash
# Inicializar tablas y cargar datos del BCRA
python -m app.populate_db
```

Este script:
- Crea todas las tablas necesarias
- Carga el catálogo de variables del BCRA
- Descarga datos históricos de los últimos 90 días

### 7. Crear usuario administrador

```bash
python -m app.create_admin
```

Credenciales por defecto:
- **Email:** admin@bcra-dashboard.com
- **Password:** admin123

### 8. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

La aplicación estará disponible en:
- Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api

## 📊 Funcionalidades

### API REST (FastAPI)

#### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Login (retorna JWT token)
- `GET /api/auth/me` - Información del usuario actual

#### Variables
- `GET /api/variables` - Listar todas las variables
- `GET /api/variables/{id}` - Obtener variable específica

#### Datos
- `GET /api/datos/variable/{nombre}` - Serie histórica de una variable
- `GET /api/datos/ultimos-valores` - Últimos valores de todas las variables
- `GET /api/dashboard` - Datos completos para el dashboard

#### Estadísticas
- `GET /api/stats` - Estadísticas del sistema

### Dashboard Web

- **Cards interactivas** con últimos valores de cada indicador
- **Gráficos dinámicos** con Chart.js:
  - Tipo de cambio USD/ARS
  - Reservas internacionales
  - Inflación mensual
  - Tasas de interés (BADLAR, Plazo Fijo, LELIQ)
- **Tabla detallada** con todos los datos
- **Actualización automática** cada 5 minutos
- **Diseño responsive** con Bootstrap 5

## 📚 Estructura del Proyecto

```
bcra-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── database.py          # Configuración SQLAlchemy
│   ├── models.py            # Modelos de base de datos
│   ├── schemas.py           # Schemas Pydantic
│   ├── auth.py              # Autenticación JWT
│   ├── bcra_client.py       # Cliente API del BCRA
│   ├── populate_db.py       # Script de población
│   └── create_admin.py      # Script crear admin
├── static/
│   ├── index.html           # Dashboard HTML
│   ├── style.css            # Estilos personalizados
│   └── app.js               # JavaScript del dashboard
├── requirements.txt         # Dependencias Python
├── .env.example             # Ejemplo de variables de entorno
├── Procfile                 # Configuración Heroku
├── railway.json             # Configuración Railway
└── README.md                # Este archivo
```

## 🌐 Deployment

### Railway (Recomendado)

1. Crear cuenta en [Railway.app](https://railway.app)
2. Crear nuevo proyecto
3. Agregar PostgreSQL database
4. Agregar servicio desde GitHub
5. Configurar variables de entorno en Railway:
   ```
   DATABASE_URL=postgresql://...  (auto-generado por Railway)
   SECRET_KEY=tu-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
6. Deploy automático desde GitHub

### Render

1. Crear cuenta en [Render.com](https://render.com)
2. Crear PostgreSQL database
3. Crear Web Service desde GitHub
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Configurar variables de entorno

### Post-Deployment

Después del primer deploy, ejecutar manualmente:

```bash
# Poblar base de datos (una sola vez)
python -m app.populate_db

# Crear usuario admin (una sola vez)
python -m app.create_admin
```

## 🔄 Actualización de Datos

Para actualizar los datos del BCRA:

```bash
# Actualizar últimos 7 días
python -m app.populate_db
```

Se puede automatizar con un cron job o tarea programada.

## 📖 Variables Disponibles

1. **Tipo de Cambio USD/ARS** - Tipo de cambio oficial
2. **Reservas Internacionales** - En millones de USD
3. **Inflación Mensual** - Variación mensual del IPC
4. **Inflación Anual** - Variación interanual del IPC
5. **BADLAR** - Tasa BADLAR en pesos
6. **Plazo Fijo** - Tasa de interés de plazo fijo
7. **LELIQ** - Tasa de política monetaria

## 🛠️ Desarrollo

### Agregar nueva variable del BCRA

1. Consultar IDs disponibles en [API BCRA](https://www.bcra.gob.ar/apis-banco-central/)
2. Agregar a `bcra_client.py`:
   ```python
   VARIABLES = {
       "nueva_variable": ID_DEL_BCRA,
       ...
   }
   ```
3. Agregar al catálogo en `populate_db.py`
4. Re-ejecutar `python -m app.populate_db`

### Testing

```bash
# Probar cliente del BCRA
python app/bcra_client.py

# Testing manual con requests
curl http://localhost:8000/api/stats
```

## 📝 Notas Pedagógicas

Este proyecto demuestra:

✅ **Patrón Repository** - Abstracción de acceso a datos
✅ **DTO Pattern** - Schemas Pydantic para validación
✅ **RESTful API** - Endpoints siguiendo convenciones REST
✅ **JWT Authentication** - Autenticación stateless
✅ **CRUD Operations** - Operaciones completas con SQLAlchemy
✅ **ORM Usage** - SQLAlchemy como puente Python-SQL
✅ **API Consumption** - Cliente para API externa
✅ **Frontend-Backend Integration** - Fetch API y rendering dinámico
✅ **Responsive Design** - Bootstrap 5 con mobile-first
✅ **Data Visualization** - Chart.js para gráficos interactivos

## 🎓 Créditos

Desarrollado para el **Seminario: Ciencia de Datos para Politólogos/as**
Universidad de Buenos Aires - Facultad de Ciencias Sociales

Datos provistos por: [Banco Central de la República Argentina](https://www.bcra.gob.ar/)

## 📄 Licencia

MIT License - Proyecto educativo
