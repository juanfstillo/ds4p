#!/bin/bash

echo "======================================"
echo "BCRA Dashboard - Setup Rápido"
echo "======================================"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_step() {
    echo -e "${BLUE}[$1/${2}]${NC} $3"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Paso 1: Verificar Python
print_step "1" "7" "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi
python_version=$(python3 --version)
print_success "Python encontrado: $python_version"
echo ""

# Paso 2: Crear entorno virtual
print_step "2" "7" "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Entorno virtual creado"
else
    print_warning "Entorno virtual ya existe"
fi
echo ""

# Paso 3: Activar entorno virtual
print_step "3" "7" "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"
echo ""

# Paso 4: Instalar dependencias
print_step "4" "7" "Instalando dependencias..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Dependencias instaladas"
echo ""

# Paso 5: Configurar .env
print_step "5" "7" "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Archivo .env creado desde .env.example"
    echo "   Por favor, edita .env con tus credenciales de PostgreSQL"
else
    print_success ".env ya existe"
fi
echo ""

# Paso 6: Inicializar base de datos
print_step "6" "7" "¿Quieres inicializar la base de datos ahora? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "Poblando base de datos (esto puede tardar unos minutos)..."
    python -m app.populate_db
    echo ""
    echo "Creando usuario administrador..."
    python -m app.create_admin
    print_success "Base de datos inicializada"
else
    print_warning "Saltando inicialización de BD"
    echo "   Recuerda ejecutar: python -m app.populate_db"
    echo "   Y luego: python -m app.create_admin"
fi
echo ""

# Paso 7: Finalizar
print_step "7" "7" "Setup completado"
echo ""
echo "======================================"
echo "🎉 Todo listo para empezar!"
echo "======================================"
echo ""
echo "Para iniciar el servidor:"
echo "  $ uvicorn app.main:app --reload"
echo ""
echo "Luego visita:"
echo "  Dashboard: http://localhost:8000/dashboard"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Credenciales de prueba:"
echo "  Email:    admin@bcra-dashboard.com"
echo "  Password: admin123"
echo ""
