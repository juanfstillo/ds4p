"""
Script para crear un usuario administrador inicial
"""

from app.database import SessionLocal
from app.models import Usuario
from app.auth import get_password_hash
import sys


def crear_usuario_admin(email: str, password: str, nombre: str):
    """
    Crea un usuario administrador
    
    Args:
        email: Email del usuario
        password: Contraseña
        nombre: Nombre del usuario
    """
    db = SessionLocal()
    
    try:
        # Verificar si ya existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
        
        if usuario_existente:
            print(f"⚠️  El usuario {email} ya existe")
            return
        
        # Crear nuevo usuario admin
        usuario = Usuario(
            email=email,
            nombre=nombre,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_admin=True
        )
        
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        
        print(f"✅ Usuario administrador creado exitosamente:")
        print(f"   Email: {email}")
        print(f"   Nombre: {nombre}")
        print(f"   Admin: Sí")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        db.rollback()
    
    finally:
        db.close()


def main():
    """
    Script principal
    """
    print("=" * 60)
    print("CREAR USUARIO ADMINISTRADOR")
    print("=" * 60)
    
    # Usuario admin por defecto para el demo
    EMAIL = "admin@bcra-dashboard.com"
    PASSWORD = "admin123"  # CAMBIAR en producción
    NOMBRE = "Administrador"
    
    print(f"\nCreando usuario admin con credenciales de demo:")
    print(f"Email: {EMAIL}")
    print(f"Password: {PASSWORD}")
    print()
    
    crear_usuario_admin(EMAIL, PASSWORD, NOMBRE)
    
    # Crear también un usuario regular para testing
    print("\n" + "-" * 60)
    crear_usuario_admin(
        email="usuario@bcra-dashboard.com",
        password="usuario123",
        nombre="Usuario Demo"
    )
    
    # Actualizar a no-admin
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == "usuario@bcra-dashboard.com").first()
    if usuario:
        usuario.is_admin = False
        db.commit()
        print("   (Usuario regular, no admin)")
    db.close()


if __name__ == "__main__":
    main()
