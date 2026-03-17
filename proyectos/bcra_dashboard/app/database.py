"""
Configuración de la base de datos con SQLAlchemy
Optimizado para despliegue en Railway.app
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno del archivo .env
load_dotenv()

# 1. Obtener la URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Corrección de protocolo para SQLAlchemy 2.0 (Vital para Railway/Heroku)
# Railway a veces entrega la URL como postgres:// pero SQLAlchemy requiere postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Fallback para desarrollo local si no hay variable de entorno
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bcra_dashboard"

# 4. Crear engine con pool_pre_ping para evitar desconexiones en la nube
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica si la conexión sigue viva antes de usarla
    echo=False           # Cambiar a True solo para debugear SQL en consola
)

# 5. Configuración de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para FastAPI que provee una sesión de base de datos por cada request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en models.py
    """
    from app.models import Variable, DatoBCRA, Usuario  # Importación diferida para evitar ciclos
    
    print(f"Conectando a: {DATABASE_URL.split('@')[-1]}") # Loguea el host para verificar conexión
    print("Creando tablas en la base de datos...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas o verificadas exitosamente!")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")


def drop_db():
    """
    CUIDADO: Elimina todas las tablas de la base de datos.
    Útil para resetear el entorno de desarrollo.
    """
    from app.models import Variable, DatoBCRA, Usuario
    
    print("⚠️  ELIMINANDO todas las tablas...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tablas eliminadas!")