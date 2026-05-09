#Para que funcion debo instalar las dependencias
#python -m pip install fastapi uvicorn

#Luego levantar el servidor 
#python -m uvicorn main:app --reload

from fastapi import FastAPI

# 1. Instanciamos la aplicación (Acá es donde nace 'app')
app = FastAPI(title="Sistema de Fiscalización Estatal")

# 2. Nuestra base de datos simulada
zonas_data = [
    {"nombre": "Zona A", "riesgo": 0.8, "poblacion": 10000, "costo": 50},
    {"nombre": "Zona B", "riesgo": 0.5, "poblacion": 20000, "costo": 30},
    {"nombre": "Zona C", "riesgo": 0.9, "poblacion": 5000, "costo": 20}
]

# 3. Endpoint Raíz
@app.get("/")
def leer_raiz():
    return {"mensaje": "Bienvenido al Sistema Central de Fiscalización"}

# 4. Endpoint de Zonas
@app.get("/zonas")
def obtener_zonas():
    return {"total_zonas": len(zonas_data), "datos": zonas_data}