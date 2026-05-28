import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y TEXTOS
# ==========================================
# st.set_page_config permite cambiar el título de la pestaña del navegador
st.set_page_config(page_title="Mi Primera App", page_icon="📈")

st.title("📊 Explorador de Datos Dinámico")
st.markdown("""
Esta es una aplicación de demostración construida 100% en Python. 
Permite a cualquier usuario explorar un conjunto de datos sin necesidad de ver ni una sola línea de código.
""")

# ==========================================
# 2. GENERACIÓN DE DATOS (Simulación)
# ==========================================
# Generamos un DataFrame de ejemplo simulando métricas de distintas regiones
@st.cache_data # Este decorador memoriza los datos para no recalcularlos en cada clic
def cargar_datos():
    datos = pd.DataFrame({
        'Región': ['Norte', 'Sur', 'Este', 'Oeste', 'Centro'] * 4,
        'Año': np.repeat([2020, 2021, 2022, 2023], 5),
        'Inversión (Millones)': np.random.randint(10, 100, 20),
        'Población Impactada': np.random.randint(5000, 50000, 20)
    })
    return datos

df = cargar_datos()

# ==========================================
# 3. INTERACTIVIDAD (Barra Lateral o Menú)
# ==========================================
st.sidebar.header("⚙️ Filtros de Búsqueda")

# Creamos un menú desplegable para elegir el año
año_seleccionado = st.sidebar.selectbox(
    "Seleccione el Año a analizar:",
    options=df['Año'].unique()
)

# Filtramos nuestro DataFrame original usando Pandas (Lógica tradicional)
df_filtrado = df[df['Año'] == año_seleccionado]

# ==========================================
# 4. VISUALIZACIÓN DE RESULTADOS
# ==========================================
st.subheader(f"Resultados para el año {año_seleccionado}")

# Dividimos la pantalla en dos columnas
col1, col2 = st.columns(2)

with col1:
    # Métrica destacada (KPI)
    total_inversion = df_filtrado['Inversión (Millones)'].sum()
    st.metric(label="Presupuesto Total Ejecutado", value=f"${total_inversion} M")

with col2:
    # Métrica destacada (KPI)
    total_personas = df_filtrado['Población Impactada'].sum()
    st.metric(label="Personas Alcanzadas", value=f"{total_personas:,}")

# Mostramos una tabla interactiva
st.markdown("### 📋 Base de Datos Filtrada")
st.dataframe(df_filtrado, hide_index=True, use_container_width=True)

# Mostramos un gráfico de barras simple
st.markdown("### 📈 Inversión por Región")
st.bar_chart(data=df_filtrado, x='Región', y='Inversión (Millones)', color="#2e86c1")

# st.balloons() # Descomentar esta línea para ver un efecto divertido al cargar
