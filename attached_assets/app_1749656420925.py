import requests
import xml.etree.ElementTree as ET
import sqlite3

# Endpoint SDMX para último dato DTF diario
URL = "https://suameca.banrep.gov.co/sdmx/data/DF_DTF_DAILY_LATEST/.CO.PA.D/all"

# Conexión a SQLite
conn = sqlite3.connect("tasas.db")
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasas_dtf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    tasa REAL
)
""")

# Consumir la API SDMX
response = requests.get(URL)
if response.status_code == 200:
    # Parsear XML
    root = ET.fromstring(response.text)
    # Buscar elementos de observación (OBS)
    ns = {'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'}
    for obs in root.findall(".//generic:Obs", ns):
        fecha = obs.find("./generic:ObsDimension", ns).attrib.get("value")
        tasa = obs.find("./generic:ObsValue", ns).attrib.get("value")
        print(f"Fecha: {fecha}, Tasa: {tasa}")
        # Insertar en BD
        cursor.execute("""
            INSERT INTO tasas_dtf (fecha, tasa)
            VALUES (?, ?)
        """, (fecha, float(tasa)))
    conn.commit()
    print("Datos DTF insertados correctamente en la BD.")
else:
    print(f"Error al consultar SDMX: {response.status_code}")

conn.close()
