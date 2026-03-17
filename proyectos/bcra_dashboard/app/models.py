"""
Modelos de base de datos usando SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Usuario(Base):
    """
    Modelo de Usuario para autenticación
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Usuario {self.email}>"


class Variable(Base):
    """
    Catálogo de variables económicas del BCRA
    """
    __tablename__ = "variables"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String)
    variable_id_bcra = Column(Integer, unique=True, nullable=False)  # ID en API del BCRA
    unidad = Column(String)  # USD, %, Millones USD, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación uno-a-muchos con DatoBCRA
    datos = relationship("DatoBCRA", back_populates="variable", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Variable {self.nombre}>"


class DatoBCRA(Base):
    """
    Datos históricos de variables del BCRA
    """
    __tablename__ = "datos_bcra"
    
    id = Column(Integer, primary_key=True, index=True)
    variable_id = Column(Integer, ForeignKey("variables.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    valor = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con Variable
    variable = relationship("Variable", back_populates="datos")
    
    # Constraint único: una variable solo puede tener un valor por fecha
    __table_args__ = (
        {'schema': None, 'extend_existing': True},
    )
    
    def __repr__(self):
        return f"<DatoBCRA variable_id={self.variable_id} fecha={self.fecha} valor={self.valor}>"


# Índices compuestos para optimizar queries
from sqlalchemy import Index

# Índice compuesto para búsquedas frecuentes por variable y rango de fechas
Index('idx_variable_fecha', DatoBCRA.variable_id, DatoBCRA.fecha)