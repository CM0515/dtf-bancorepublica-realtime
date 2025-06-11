import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from openai import OpenAI
from models import TasaDTF
from app import app
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class DTFAnalyzer:
    """AI-powered analyzer for DTF rates and trends"""
    
    def __init__(self):
        self.model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    
    def analyze_dtf_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze DTF trends using AI"""
        with app.app_context():
            try:
                # Get recent DTF data
                rates = TasaDTF.get_latest(days)
                if not rates:
                    return {"error": "No DTF data available for analysis"}
                
                # Prepare data for analysis
                rate_data = [{"fecha": rate.fecha, "tasa": rate.tasa} for rate in rates]
                
                # Create analysis prompt
                prompt = f"""
                Analiza las siguientes tasas DTF (Depósito a Término Fijo) de Colombia de los últimos {days} días:
                
                {json.dumps(rate_data, ensure_ascii=False, indent=2)}
                
                Proporciona un análisis completo que incluya:
                1. Tendencia general (alcista, bajista, estable)
                2. Volatilidad observada
                3. Puntos de cambio significativos
                4. Comparación con niveles históricos típicos (DTF suele estar entre 8-15%)
                5. Factores económicos que podrían estar influyendo
                6. Predicción de corto plazo (próximos 7-14 días)
                7. Recomendaciones para inversionistas
                
                Responde en formato JSON con la siguiente estructura:
                {{
                    "tendencia_general": "string",
                    "volatilidad": "alta|media|baja",
                    "tasa_actual": number,
                    "cambio_periodo": number,
                    "puntos_clave": ["string"],
                    "factores_economicos": ["string"],
                    "prediccion_corto_plazo": "string",
                    "recomendaciones": ["string"],
                    "resumen": "string"
                }}
                """
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un analista financiero experto en mercados colombianos y tasas de interés. Proporciona análisis precisos y profesionales."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                
                analysis = json.loads(response.choices[0].message.content)
                analysis["fecha_analisis"] = datetime.now().isoformat()
                analysis["periodo_analizado"] = f"Últimos {days} días"
                
                return analysis
                
            except Exception as e:
                logger.error(f"Error analyzing DTF trends: {e}")
                return {"error": f"Error en el análisis: {str(e)}"}
    
    def generate_market_summary(self) -> Dict[str, Any]:
        """Generate a market summary using AI"""
        with app.app_context():
            try:
                # Get recent data for context
                rates = TasaDTF.get_latest(7)
                if not rates:
                    return {"error": "No hay datos suficientes para el resumen"}
                
                latest_rate = rates[0].tasa
                week_ago_rate = rates[-1].tasa if len(rates) > 6 else latest_rate
                change = latest_rate - week_ago_rate
                
                prompt = f"""
                Genera un resumen ejecutivo del mercado DTF colombiano basado en:
                - Tasa actual: {latest_rate}%
                - Cambio semanal: {change:+.4f} puntos básicos
                - Fecha: {rates[0].fecha}
                
                El resumen debe ser conciso (máximo 3 párrafos) y dirigido a inversionistas institucionales.
                Incluye contexto macroeconómico relevante para Colombia.
                
                Responde en formato JSON:
                {{
                    "titulo": "string",
                    "resumen_ejecutivo": "string",
                    "contexto_macroeconomico": "string",
                    "outlook": "string"
                }}
                """
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un analista senior de mercados financieros colombianos. Escribe de manera profesional y concisa."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.4
                )
                
                summary = json.loads(response.choices[0].message.content)
                summary["fecha_generacion"] = datetime.now().isoformat()
                
                return summary
                
            except Exception as e:
                logger.error(f"Error generating market summary: {e}")
                return {"error": f"Error generando resumen: {str(e)}"}
    
    def predict_rate_movement(self, horizon_days: int = 14) -> Dict[str, Any]:
        """Predict DTF rate movement using AI"""
        with app.app_context():
            try:
                # Get historical data for prediction
                rates = TasaDTF.get_latest(60)
                if len(rates) < 30:
                    return {"error": "Datos insuficientes para predicción"}
                
                # Prepare data
                rate_values = [rate.tasa for rate in rates]
                recent_trend = rate_values[:14]  # Last 2 weeks
                
                prompt = f"""
                Basándote en estos datos históricos de DTF de los últimos 60 días:
                Tasas recientes (últimas 2 semanas): {recent_trend}
                Rango completo: {min(rate_values):.4f}% - {max(rate_values):.4f}%
                
                Predice el movimiento probable de la tasa DTF para los próximos {horizon_days} días.
                
                Considera:
                - Patrones estacionales típicos en Colombia
                - Política monetaria del Banco de la República
                - Contexto económico actual
                
                Responde en formato JSON:
                {{
                    "prediccion_direccion": "alcista|bajista|estable",
                    "probabilidad_direccion": number,
                    "rango_esperado_min": number,
                    "rango_esperado_max": number,
                    "confianza_prediccion": "alta|media|baja",
                    "factores_clave": ["string"],
                    "escenarios": {{
                        "optimista": "string",
                        "base": "string", 
                        "pesimista": "string"
                    }}
                }}
                """
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un analista cuantitativo especializado en predicción de tasas de interés en mercados emergentes."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                
                prediction = json.loads(response.choices[0].message.content)
                prediction["horizonte_dias"] = horizon_days
                prediction["fecha_prediccion"] = datetime.now().isoformat()
                
                return prediction
                
            except Exception as e:
                logger.error(f"Error predicting rate movement: {e}")
                return {"error": f"Error en predicción: {str(e)}"}
    
    def analyze_volatility(self) -> Dict[str, Any]:
        """Analyze DTF volatility patterns"""
        with app.app_context():
            try:
                rates = TasaDTF.get_latest(90)
                if len(rates) < 30:
                    return {"error": "Datos insuficientes para análisis de volatilidad"}
                
                # Calculate basic volatility metrics
                rate_values = [rate.tasa for rate in rates]
                mean_rate = sum(rate_values) / len(rate_values)
                variance = sum((x - mean_rate) ** 2 for x in rate_values) / len(rate_values)
                std_dev = variance ** 0.5
                
                # Daily changes
                daily_changes = [rate_values[i] - rate_values[i+1] for i in range(len(rate_values)-1)]
                abs_changes = [abs(change) for change in daily_changes]
                avg_daily_change = sum(abs_changes) / len(abs_changes) if abs_changes else 0
                
                prompt = f"""
                Analiza la volatilidad de las tasas DTF basándote en estos datos:
                - Desviación estándar: {std_dev:.6f}
                - Cambio diario promedio: {avg_daily_change:.6f} puntos básicos
                - Rango en el período: {min(rate_values):.4f}% - {max(rate_values):.4f}%
                - Número de observaciones: {len(rate_values)}
                
                Proporciona un análisis de volatilidad comparado con estándares del mercado colombiano.
                
                Responde en formato JSON:
                {{
                    "nivel_volatilidad": "muy_alta|alta|normal|baja|muy_baja",
                    "score_volatilidad": number,
                    "interpretacion": "string",
                    "comparacion_historica": "string",
                    "implicaciones_inversion": "string"
                }}
                """
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un especialista en análisis de riesgo y volatilidad de mercados financieros."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                
                volatility_analysis = json.loads(response.choices[0].message.content)
                volatility_analysis["metricas_calculadas"] = {
                    "desviacion_estandar": std_dev,
                    "cambio_diario_promedio": avg_daily_change,
                    "rango_periodo": {
                        "min": min(rate_values),
                        "max": max(rate_values)
                    }
                }
                
                return volatility_analysis
                
            except Exception as e:
                logger.error(f"Error analyzing volatility: {e}")
                return {"error": f"Error en análisis de volatilidad: {str(e)}"}

# Global instance
dtf_analyzer = DTFAnalyzer()