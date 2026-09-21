import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GARES_RER_D = {
    "Châtelet": "STIF:StopArea:SP:46050:",
    "Garges": "STIF:StopArea:SP:44464:", 
    "Gare de Lyon": "STIF:StopArea:SP:47415:"
}

TRADUCTION_LIGNES = {
    "STIF:Line::C01148:": "RER B",
    "STIF:Line::C01727:": "RER D",
    "STIF:Line::C01742:": "RER A"
}

API_KEY = os.getenv("IDFM_API_KEY")
DB_PASS = os.getenv("DB_PASSWORD")

if not API_KEY or not DB_PASS:
    print("Erreur : .env manquant")
    exit()

headers = {"apiKey": API_KEY, "Accept": "application/json"}

connexion = psycopg2.connect(
    dbname="idfm_tracker", 
    user="postgres", 
    password=DB_PASS, 
    host="localhost"
)
curseur = connexion.cursor()

for nom_gare, ref_gare in GARES_RER_D.items():
    url = f"https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef={ref_gare}"
    reponse = requests.get(url, headers=headers)
    
    if reponse.status_code == 200:
        data = reponse.json()
        livraisons = data.get('Siri', {}).get('ServiceDelivery', {}).get('StopMonitoringDelivery', [])
        passages = livraisons[0].get('MonitoredStopVisit', []) if livraisons else []
        
        if not passages:
            print(f"{nom_gare} : Aucun train")
            continue
            
        train_valide_trouve = False
        
        for passage in passages[:3]:
            trajet = passage.get('MonitoredVehicleJourney', {})
            code_ligne = trajet.get('LineRef', {}).get('value', '')
            ligne = TRADUCTION_LIGNES.get(code_ligne, "Train")
            destination = trajet.get('DestinationName', [{'value': 'Inconnue'}])[0].get('value')
            
            arret = trajet.get('MonitoredCall', {})
            heure_theorique_str = arret.get('AimedDepartureTime')
            heure_estimee_str = arret.get('ExpectedDepartureTime')
            
            if not heure_theorique_str or not heure_estimee_str:
                continue
                
            h_theo = datetime.fromisoformat(heure_theorique_str.replace('Z', '+00:00'))
            h_est = datetime.fromisoformat(heure_estimee_str.replace('Z', '+00:00'))
            retard = max(0, int((h_est - h_theo).total_seconds() // 60))
            
            print(f"{nom_gare} | {ligne} -> {destination} : {retard} min")
            train_valide_trouve = True
            
            curseur.execute(
                "INSERT INTO passages (ligne, destination, heure_theorique, heure_estimee, retard_minutes) VALUES (%s, %s, %s, %s, %s)",
                (ligne, destination, h_theo, h_est, retard)
            )
            
        if not train_valide_trouve:
            print(f"{nom_gare} : Trains en approche, mais horaires non communiqués")
            
    else:
        print(f"{nom_gare} : Erreur API {reponse.status_code}")

connexion.commit()
curseur.close()
connexion.close()