# 🎓 Guía de Presentación - Seminario Ciencia de Datos

## 📋 Checklist Pre-Clase

- [ ] Verificar deploy en Railway (URL pública funcionando).
- [ ] Probar login: admin@bcra-dashboard.com / admin123.
- [ ] Tener el código de `generate_test_data.py` a mano como Plan B.

## 🎯 Estructura de la Presentación

### 1. Introducción (5 min)

**Mensaje clave:** "Construiremos herramientas profesionales para el análisis político".

- Presentación de objetivos.
- **Lección Realista:** Explicar que las APIs del Estado (como el BCRA) pueden fallar o bloquear conexiones internacionales.
- **Redundancia:** Mostrar cómo nuestra App soluciona esto guardando datos localmente o usando generadores sintéticos de respaldo.

### 2. Demostración del Stack (20 min)

- **Frontend:** Dashboard dinámico con paleta institucional (#632024).
- **Backend:** FastAPI + Swagger Docs (`/docs`).
- **Base de Datos:** PostgreSQL en la nube manejando la persistencia.

### 3. Flujo de Datos

- **Captura:** El cliente Python busca los datos (Requests).
- **Almacenamiento:** SQLAlchemy traduce y guarda en SQL.
- **Exposición:** FastAPI entrega JSON validado por Pydantic.
- **Consumo:** El navegador renderiza con Chart.js.

### 4. Cierre

- "Al final del curso, su propio MVP estará deployado y funcionando igual que este".
