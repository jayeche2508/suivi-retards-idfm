import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("IDFM_API_KEY")
DB_PASS = os.getenv("DB_PASSWORD")

STATIONS = {
    "Châtelet-Les Halles": "STIF:StopArea:SP:47424:",
    "Garges - Sarcelles": "STIF:StopArea:SP:44464:", 
    "Gare de Lyon": "STIF:StopArea:SP:47415:"
}

LINES = {
    "STIF:Line::C01148:": "RER B",
    "STIF:Line::C01727:": "RER D",
    "STIF:Line::C01742:": "RER A"
}

# --- FONCTIONS ---
def parse_time(t_str):
    if not t_str:
        return None
    return datetime.fromisoformat(t_str.replace('Z', '+00:00'))

def fetch_visits(stop_id):
    url = f"https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef={stop_id}"
    res = requests.get(url, headers={"apiKey": API_KEY, "Accept": "application/json"})
    
    if res.status_code != 200:
        return []
        
    try:
        deliveries = res.json().get('Siri', {}).get('ServiceDelivery', {}).get('StopMonitoringDelivery', [])
        return deliveries[0].get('MonitoredStopVisit', []) if deliveries else []
    except (IndexError, AttributeError):
        return []

def main():
    if not API_KEY or not DB_PASS:
        raise ValueError("Variables d'environnement manquantes (.env).")

    try:
        conn = psycopg2.connect(dbname="idfm_tracker", user="postgres", password=DB_PASS, host="localhost")
        cur = conn.cursor()
    except psycopg2.Error as e:
        raise ConnectionError(f"Échec de connexion PostgreSQL : {e}")

    for name, stop_id in STATIONS.items():
        visits = fetch_visits(stop_id)
        
        if not visits:
            print(f"[{name}] Aucun train prévu.")
            continue

        for v in visits[:3]:
            journey = v.get('MonitoredVehicleJourney', {})
            line_ref = journey.get('LineRef', {}).get('value', '')
            line = LINES.get(line_ref, "Ligne Inconnue")
            dest = journey.get('DestinationName', [{'value': 'Destination Inconnue'}])[0].get('value')
            
            call = journey.get('MonitoredCall', {})
            t_aimed = parse_time(call.get('AimedDepartureTime'))
            t_exp = parse_time(call.get('ExpectedDepartureTime'))

            if not t_aimed or not t_exp:
                continue

            delay = max(0, int((t_exp - t_aimed).total_seconds() // 60))
            
            # Formatage des heures (HH:MM)
            h_prevu = t_aimed.strftime("%H:%M")
            h_estime = t_exp.strftime("%H:%M")
            statut = "A l'heure" if delay == 0 else f"Retard : {delay} min"

            print(f"[{name}] {line} vers {dest} | Prévu : {h_prevu} | Estimé : {h_estime} | {statut}")
            
            cur.execute(
                "INSERT INTO passages (ligne, destination, heure_theorique, heure_estimee, retard_minutes) VALUES (%s, %s, %s, %s, %s)",
                (line, dest, t_aimed, t_exp, delay)
            )

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()