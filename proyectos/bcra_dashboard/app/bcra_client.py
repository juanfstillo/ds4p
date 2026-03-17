"""
Cliente para consumir la API del Banco Central de la República Argentina (BCRA)
Optimizado con headers de navegación real para evitar bloqueos.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BCRAClient:
    """Cliente para interactuar con la API del BCRA"""
    
    BASE_URL = "https://api.bcra.gob.ar"
    
    VARIABLES = {
        "reservas": 1,
        "tipo_cambio_oficial": 4,
        "inflacion_mensual": 31,
        "inflacion_anual": 32,
        "badlar": 7,
        "plazo_fijo": 10,
        "leliq": 6,
    }
    
    def __init__(self):
        self.session = requests.Session()
        # Headers que imitan a un navegador Chrome real en Windows 
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Referer': 'https://www.bcra.gob.ar/',
            'Origin': 'https://www.bcra.gob.ar',
            'Connection': 'keep-alive'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar API del BCRA: {e}")
            return None
    
    def get_datos_variable(self, variable_id: int, desde: Optional[str] = None, hasta: Optional[str] = None) -> List[Dict]:
        if not hasta:
            hasta = datetime.now().strftime("%Y-%m-%d")
        if not desde:
            desde = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        endpoint = f"estadisticas/v1/DatosVariable/{variable_id}/{desde}/{hasta}"
        data = self._make_request(endpoint)
        
        if data and 'results' in data:
            return data['results']
        return []

    def get_tipo_cambio(self, desde: str = None, hasta: str = None):
        return self.get_datos_variable(self.VARIABLES['tipo_cambio_oficial'], desde, hasta)

    def get_ultimos_valores(self) -> Dict:
        desde = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        hasta = datetime.now().strftime("%Y-%m-%d")
        resultado = {}
        for nombre, variable_id in self.VARIABLES.items():
            datos = self.get_datos_variable(variable_id, desde, hasta)
            if datos:
                resultado[nombre] = {"valor": datos[-1].get("valor"), "fecha": datos[-1].get("fecha")}
        return resultado