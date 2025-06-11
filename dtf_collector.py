import requests
import xml.etree.ElementTree as ET
import logging
from app import app, db
from models import TasaDTF
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

# Endpoint SDMX para último dato DTF diario
URL = "https://suameca.banrep.gov.co/sdmx/data/DF_DTF_DAILY_LATEST/.CO.PA.D/all"

def collect_dtf_data():
    """
    Collect DTF data from Banco de la República SDMX API
    """
    with app.app_context():
        try:
            logger.info("Starting DTF data collection...")
            
            # Make request to SDMX API
            response = requests.get(URL, timeout=30)
            response.raise_for_status()
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)
                
                # Define namespace for SDMX XML
                ns = {'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'}
                
                # Counter for new records
                new_records = 0
                updated_records = 0
                
                # Find observation elements
                observations = root.findall(".//generic:Obs", ns)
                
                if not observations:
                    logger.warning("No observations found in SDMX response")
                    return False
                
                for obs in observations:
                    try:
                        # Extract date and rate
                        fecha_elem = obs.find("./generic:ObsDimension", ns)
                        tasa_elem = obs.find("./generic:ObsValue", ns)
                        
                        if fecha_elem is None or tasa_elem is None:
                            logger.warning("Missing date or rate information in observation")
                            continue
                            
                        fecha = fecha_elem.attrib.get("value")
                        tasa_str = tasa_elem.attrib.get("value")
                        
                        if not fecha or not tasa_str:
                            logger.warning("Empty date or rate value in observation")
                            continue
                        
                        try:
                            tasa = float(tasa_str)
                        except ValueError:
                            logger.error(f"Invalid rate value: {tasa_str}")
                            continue
                        
                        # Check if record already exists
                        existing_record = TasaDTF.query.filter_by(fecha=fecha).first()
                        
                        if existing_record:
                            # Update existing record if rate is different
                            if existing_record.tasa != tasa:
                                existing_record.tasa = tasa
                                updated_records += 1
                                logger.info(f"Updated DTF rate for {fecha}: {tasa}%")
                        else:
                            # Create new record
                            new_dtf = TasaDTF(fecha=fecha, tasa=tasa)
                            db.session.add(new_dtf)
                            new_records += 1
                            logger.info(f"Added new DTF rate for {fecha}: {tasa}%")
                    
                    except Exception as e:
                        logger.error(f"Error processing observation: {e}")
                        continue
                
                # Commit all changes
                try:
                    db.session.commit()
                    logger.info(f"DTF data collection completed. New records: {new_records}, Updated records: {updated_records}")
                    return True
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error committing DTF data to database: {e}")
                    return False
            
            else:
                logger.error(f"Failed to fetch DTF data. HTTP Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching DTF data: {e}")
            return False
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during DTF data collection: {e}")
            return False

def get_collection_status():
    """
    Get status information about the DTF data collection
    """
    with app.app_context():
        try:
            total_records = TasaDTF.query.count()
            latest_record = TasaDTF.query.order_by(TasaDTF.fecha.desc()).first()
            
            return {
                'total_records': total_records,
                'latest_date': latest_record.fecha if latest_record else None,
                'latest_rate': latest_record.tasa if latest_record else None,
                'last_updated': latest_record.created_at if latest_record else None
            }
        except Exception as e:
            logger.error(f"Error getting collection status: {e}")
            return {
                'total_records': 0,
                'latest_date': None,
                'latest_rate': None,
                'last_updated': None,
                'error': str(e)
            }
