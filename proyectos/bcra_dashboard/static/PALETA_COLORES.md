# 🎨 Paleta de Colores - Dashboard BCRA

## Color Principal

**#632024** - Rojo Burdeos
- Uso: Color primario del sitio
- Aplicaciones:
  - Navbar
  - Botones principales
  - Headers de cards
  - Links
  - Bordes de cards de indicadores
  - Valores destacados

## Variaciones del Color Principal

### Tonos más Claros
- **#7d2a2e** (`--primary-light`) - Para hovers y estados activos
- **#8f2d32** (`--accent-color`) - Color de acento
- **#9d363b** - Gráficos variante 1
- **#aa4248** - Gráficos variante 2
- **#b74e54** - Gráficos variante 3

### Tonos más Oscuros
- **#4a181b** (`--primary-dark`) - Para footer y estados presionados

## Color Secundario

**#ffffff** - Blanco
- Uso: Fondo de cards, texto en fondos oscuros
- **#f8f9fa** (`--off-white`) - Fondo de página (blanco roto)
- **#e8e8e8** (`--text-light`) - Texto claro sobre fondos oscuros

## Aplicación por Componente

### Navbar
- Fondo: `#632024`
- Texto: Blanco
- Hover: `rgba(255, 255, 255, 0.9)`

### Header Hero
- Gradiente: `#632024` → `#4a181b`
- Texto: Blanco

### Cards de Indicadores
- Fondo: Blanco
- Borde izquierdo: Variaciones de `#632024`
- Valor numérico: `#632024`
- Shadow: `rgba(99, 32, 36, 0.15)`

### Gráficos (Chart.js)
- Tipo de Cambio: `#632024`
- Reservas: `#7d2a2e`
- Inflación: `#4a181b`
- Tasas: `#8f2d32`, `#9d363b`, `#aa4248`

### Tabla
- Header: `#632024` (fondo)
- Hover row: `rgba(99, 32, 36, 0.08)`
- Striped row: `rgba(99, 32, 36, 0.03)`

### Botones
- Normal: `#632024`
- Hover: `#7d2a2e`
- Active: `#4a181b`
- Focus shadow: `rgba(99, 32, 36, 0.25)`

### Footer
- Fondo: `#4a181b`
- Texto: Blanco con opacidad
- Links: `#e8e8e8`

## Accesibilidad

### Contraste de Texto
- ✅ Blanco sobre `#632024`: WCAG AAA (ratio 11.5:1)
- ✅ `#632024` sobre blanco: WCAG AAA (ratio 11.5:1)

### Recomendaciones
- Usar siempre texto blanco sobre `#632024` y variantes
- Usar `#632024` para texto importante sobre fondo blanco
- Mantener bordes sutiles con opacidad baja (0.1-0.15)

## Código CSS

```css
:root {
    --primary-color: #632024;
    --primary-light: #7d2a2e;
    --primary-dark: #4a181b;
    --accent-color: #8f2d32;
    --white: #ffffff;
    --off-white: #f8f9fa;
    --text-light: #e8e8e8;
}
```

## Variaciones con Transparencia

Para overlays y efectos:
- `rgba(99, 32, 36, 0.05)` - Muy sutil
- `rgba(99, 32, 36, 0.1)` - Bordes suaves
- `rgba(99, 32, 36, 0.15)` - Shadows
- `rgba(99, 32, 36, 0.25)` - Focus states
- `rgba(99, 32, 36, 0.9)` - Backgrounds semi-transparentes
