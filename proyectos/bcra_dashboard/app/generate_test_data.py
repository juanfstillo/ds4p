"""
Script para poblar la base de datos con datos de prueba
Útil cuando la API del BCRA no está disponible
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Variable, DatoBCRA
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generar_datos_prueba(db: Session, dias_atras: int = 90):
    """
    Genera datos de prueba realistas para todas las variables
    """
    logger.info(f"Generando datos de prueba para los últimos {dias_atras} días...")
    
    # Obtener todas las variables
    variables = db.query(Variable).all()
    
    if not variables:
        logger.error("No hay variables en el catálogo.")
        return
    
    # Configuración de valores base y volatilidad por variable
    config_variables = {
        'reservas': {
            'base': 25000,  # Millones USD
            'volatilidad': 1000,
            'tendencia': -50  # Tendencia descendente
        },
        'tipo_cambio_oficial': {
            'base': 1050,  # ARS por USD
            'volatilidad': 15,
            'tendencia': 2  # Tendencia alcista
        },
        'inflacion_mensual': {
            'base': 12.5,  # %
            'volatilidad': 2.5,
            'tendencia': -0.2  # Tendencia a la baja
        },
        'inflacion_anual': {
            'base': 185,  # %
            'volatilidad': 15,
            'tendencia': 1  # Tendencia alcista
        },
        'badlar': {
            'base': 75,  # % anual
            'volatilidad': 5,
            'tendencia': 0.3
        },
        'plazo_fijo': {
            'base': 70,  # % anual
            'volatilidad': 4,
            'tendencia': 0.2
        },
        'leliq': {
            'base': 80,  # % anual
            'volatilidad': 6,
            'tendencia': 0.5
        }
    }
    
    total_registros = 0
    
    for variable in variables:
        logger.info(f"Generando datos para: {variable.nombre}")
        
        config = config_variables.get(variable.nombre)
        if not config:
            logger.warning(f"No hay configuración para {variable.nombre}, saltando...")
            continue
        
        # Generar datos día por día
        registros_insertados = 0
        valor_actual = config['base']
        
        for i in range(dias_atras, -1, -1):
            fecha = (datetime.now() - timedelta(days=i)).date()
            
            # Verificar si ya existe el dato
            dato_existente = db.query(DatoBCRA).filter(
                DatoBCRA.variable_id == variable.id,
                DatoBCRA.fecha == fecha
            ).first()
            
            if dato_existente:
                continue
            
            # Generar valor con tendencia y volatilidad
            cambio = random.uniform(-config['volatilidad'], config['volatilidad'])
            valor_actual += cambio + config['tendencia']
            
            # Asegurar que el valor no sea negativo
            valor_actual = max(0, valor_actual)
            
            # Crear registro
            nuevo_dato = DatoBCRA(
                variable_id=variable.id,
                fecha=fecha,
                valor=round(valor_actual, 2)
            )
            db.add(nuevo_dato)
            registros_insertados += 1
        
        db.commit()
        total_registros += registros_insertados
        logger.info(f"  ✅ {registros_insertados} registros generados para {variable.nombre}")
    
    logger.info(f"\n🎉 Generación completa: {total_registros} registros de prueba creados")


def main():
    """
    Script principal
    """
    print("=" * 60)
    print("GENERACIÓN DE DATOS DE PRUEBA - BCRA Dashboard")
    print("=" * 60)
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Verificar que las tablas existen
        total_variables = db.query(Variable).count()
        
        if total_variables == 0:
            print("\n⚠️  No hay variables en la base de datos.")
            print("   Ejecuta primero: python -m app.populate_db")
            return
        
        print(f"\n✅ Base de datos lista ({total_variables} variables encontradas)")
        print("\n🔧 Generando datos de prueba realistas...")
        print("   (Esto es más rápido que descargar de la API real)\n")
        
        # Generar datos de prueba
        generar_datos_prueba(db, dias_atras=90)
        
        # Mostrar estadísticas
        print("\n" + "=" * 60)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("=" * 60)
        
        total_variables = db.query(Variable).count()
        total_datos = db.query(DatoBCRA).count()
        
        print(f"\nTotal de variables: {total_variables}")
        print(f"Total de registros: {total_datos}")
        
        print("\nVariables con datos:")
        variables = db.query(Variable).all()
        for var in variables:
            count = db.query(DatoBCRA).filter(DatoBCRA.variable_id == var.id).count()
            print(f"  • {var.nombre:25} - {count:4} registros")
        
        print("\n✅ Datos de prueba generados exitosamente!")
        print("\n💡 Nota: Estos son datos sintéticos para demostración.")
        print("   Cuando la API del BCRA esté disponible, ejecuta:")
        print("   python -m app.populate_db")
        
    except Exception as e:
        logger.error(f"Error durante la generación: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
