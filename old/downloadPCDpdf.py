import os
import re
import requests
from requests.auth import HTTPBasicAuth

# Configurazione
BASE_URL =
API_USER =
API_PASSWORD =
SPACE_KEY = "PCD"
OUTPUT_DIR = "./confluence_export"

# Creazione directory di output
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Funzione per pulire i nomi delle directory e dei file
def clean_name(name):
    # Sostituzione specifica
    name = name.replace("Promo Collaboration Development", "PCD")
    
    # Sostituzione dei caratteri non validi nei nomi dei file e delle cartelle
    return re.sub(r'[<>:"/\\|?*]', '-', name)

# Funzione per ottenere la lista delle pagine nello spazio con dettagli sugli antenati
def get_pages_with_hierarchy(space_key):
    url = f"{BASE_URL}/rest/api/content"
    params = {
        "spaceKey": space_key,
        "expand": "ancestors",
        "limit": 100
    }
    response = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD), params=params)
    response.raise_for_status()
    return response.json()["results"]

# Funzione per ottenere il percorso della gerarchia
def get_hierarchy_path(page):
    ancestors = page.get("ancestors", [])
    path = []

    # Controllo sicuro per ogni antenato
    for ancestor in ancestors:
        if "title" in ancestor:
            path.append(clean_name(ancestor["title"]))
        else:
            # Se manca il 'title', aggiungi un valore di fallback
            path.append("Unknown_Ancestor")

    # Aggiungi il titolo della pagina attuale
    path.append(clean_name(page["title"]))
    return os.path.join(*path)

# Funzione per esportare la pagina in formato PDF
def export_page_to_pdf(page_id, pdf_path):
    # Costruisci l'URL di esportazione PDF
    url = f"{BASE_URL}/rest/api/content/{page_id}/export/pdf"
    
    try:
        # Aggiungi l'autenticazione tramite API_USER e API_PASSWORD
        response = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD), stream=True)
        
        # Verifica la risposta
        response.raise_for_status()

        # Salva il PDF sul disco
        with open(pdf_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)
                
        print(f"Pagina {page_id} esportata correttamente come PDF.")
    except requests.exceptions.HTTPError as err:
        print(f"Errore nell'esportazione della pagina {page_id} come PDF: {err}")


# Funzione principale per eseguire l'export
def export_space():
    pages = get_pages_with_hierarchy(SPACE_KEY)
    for page in pages:
        page_path = os.path.join(OUTPUT_DIR, get_hierarchy_path(page))
        os.makedirs(page_path, exist_ok=True)

        # Esporta la pagina in PDF
        pdf_path = os.path.join(page_path, f"{clean_name(page['title'])}.pdf")
        export_page_to_pdf(page["id"], pdf_path)

# Esecuzione dello script
if __name__ == "__main__":
    export_space()
