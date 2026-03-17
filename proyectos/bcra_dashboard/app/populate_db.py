"""
Script para poblar la base de datos con datos del BCRA
Se ejecuta para hacer la carga inicial de datos
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Variable, DatoBCRA
from app.bcra_client import BCRAClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crear_variables_catalogo(db: Session):
    """
    Crea el catálogo de variables en la base de datos
    """
    logger.info("Creando catálogo de variables...")
    
    variables_catalogo = [
        {
            "nombre": "reservas",
            "descripcion": "Reservas Internacionales del BCRA",
            "variable_id_bcra": 1,
            "unidad": "Millones USD"
        },
        {
            "nombre": "tipo_cambio_oficial",
            "descripcion": "Tipo de Cambio de Referencia USD/ARS",
            "variable_id_bcra": 4,
            "unidad": "ARS"
        },
        {
            "nombre": "inflacion_mensual",
            "descripcion": "Variación Mensual del IPC",
            "variable_id_bcra": 31,
            "unidad": "%"
        },
        {
            "nombre": "inflacion_anual",
            "descripcion": "Variación Interanual del IPC",
            "variable_id_bcra": 32,
            "unidad": "%"
        },
        {
            "nombre": "badlar",
            "descripcion": "Tasa BADLAR en pesos de bancos privados",
            "variable_id_bcra": 7,
            "unidad": "% anual"
        },
        {
            "nombre": "plazo_fijo",
            "descripcion": "Tasa de interés por depósitos a plazo fijo",
            "variable_id_bcra": 10,
            "unidad": "% anual"
        },
        {
            "nombre": "leliq",
            "descripcion": "Tasa de política monetaria (LELIQ)",
            "variable_id_bcra": 6,
            "unidad": "% anual"
        },
    ]
    
    variables_creadas = []
    
    for var_data in variables_catalogo:
        # Verificar si ya existe
        var_existente = db.query(Variable).filter(
            Variable.nombre == var_data["nombre"]
        ).first()
        
        if var_existente:
            logger.info(f"Variable '{var_data['nombre']}' ya existe, saltando...")
            variables_creadas.append(var_existente)
            continue
        
        # Crear nueva variable
        variable = Variable(**var_data)
        db.add(variable)
        variables_creadas.append(variable)
        logger.info(f"✅ Variable creada: {var_data['nombre']}")
    
    db.commit()
    logger.info(f"Catálogo creado: {len(variables_creadas)} variables")
    
    return variables_creadas


def cargar_datos_historicos(db: Session, dias_atras: int = 90):
    """
    Carga datos históricos de todas las variables
    
    Args:
        db: Sesión de base de datos
        dias_atras: Cantidad de días hacia atrás para cargar datos
    """
    logger.info(f"Cargando datos históricos de los últimos {dias_atras} días...")
    
    client = BCRAClient()
    
    # Obtener todas las variables del catálogo
    variables = db.query(Variable).all()
    
    if not variables:
        logger.error("No hay variables en el catálogo. Ejecutar crear_variables_catalogo() primero.")
        return
    
    # Calcular rango de fechas
    hasta = datetime.now().strftime("%Y-%m-%d")
    desde = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
    
    total_registros = 0
    
    for variable in variables:
        logger.info(f"Procesando variable: {variable.nombre}")
        
        # Obtener datos de la API del BCRA
        datos_api = client.get_datos_variable(
            variable_id=variable.variable_id_bcra,
            desde=desde,
            hasta=hasta
        )
        
        if not datos_api:
            logger.warning(f"No se obtuvieron datos para {variable.nombre}")
            continue
        
        # Insertar datos en la base de datos
        registros_insertados = 0
        
        for dato in datos_api:
            # Verificar si el dato ya existe
            fecha_dato = datetime.strptime(dato['fecha'], "%Y-%m-%d").date()
            
            dato_existente = db.query(DatoBCRA).filter(
                DatoBCRA.variable_id == variable.id,
                DatoBCRA.fecha == fecha_dato
            ).first()
            
            if dato_existente:
                # Actualizar valor si cambió
                if dato_existente.valor != dato['valor']:
                    dato_existente.valor = dato['valor']
                    registros_insertados += 1
                continue
            
            # Crear nuevo registro
            nuevo_dato = DatoBCRA(
                variable_id=variable.id,
                fecha=fecha_dato,
                valor=dato['valor']
            )
            db.add(nuevo_dato)
            registros_insertados += 1
        
        db.commit()
        total_registros += registros_insertados
        logger.info(f"  ✅ {registros_insertados} registros para {variable.nombre}")
    
    logger.info(f"\n🎉 Carga completa: {total_registros} registros totales insertados/actualizados")


def actualizar_datos_recientes(db: Session, dias: int = 7):
    """
    Actualiza solo los datos de los últimos días
    Útil para ejecutar periódicamente
    
    Args:
        db: Sesión de base de datos
        dias: Cantidad de días recientes para actualizar
    """
    logger.info(f"Actualizando datos de los últimos {dias} días...")
    cargar_datos_historicos(db, dias_atras=dias)


def main():
    """
    Script principal para poblar la base de datos
    """
    print("=" * 60)
    print("SCRIPT DE POBLACIÓN DE BASE DE DATOS - BCRA Dashboard")
    print("=" * 60)
    
    # Inicializar la base de datos (crear tablas)
    print("\n1️⃣  Inicializando base de datos...")
    init_db()
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Crear catálogo de variables
        print("\n2️⃣  Creando catálogo de variables...")
        crear_variables_catalogo(db)
        
        # Cargar datos históricos (últimos 90 días)
        print("\n3️⃣  Cargando datos históricos (últimos 90 días)...")
        print("⏳ Esto puede tomar unos minutos...\n")
        cargar_datos_historicos(db, dias_atras=90)
        
        # Mostrar estadísticas
        print("\n" + "=" * 60)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("=" * 60)
        
        total_variables = db.query(Variable).count()
        total_datos = db.query(DatoBCRA).count()
        
        print(f"\nTotal de variables: {total_variables}")
        print(f"Total de registros: {total_datos}")
        
        print("\nVariables cargadas:")
        variables = db.query(Variable).all()
        for var in variables:
            count = db.query(DatoBCRA).filter(DatoBCRA.variable_id == var.id).count()
            print(f"  • {var.nombre:25} - {count:4} registros")
        
        print("\n✅ Base de datos poblada exitosamente!")
        
    except Exception as e:
        logger.error(f"Error durante la población: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
