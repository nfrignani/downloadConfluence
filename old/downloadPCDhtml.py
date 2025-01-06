import os
import requests
from requests.auth import HTTPBasicAuth
import re

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
    # Sostituzione dei caratteri non validi nei nomi dei file e delle cartelle
    return re.sub(r'[<>:"/\\|?*]', '-', name)

# Funzione per ottenere la lista delle pagine nello spazio
def get_pages(space_key):
    url = f"{BASE_URL}/rest/api/content"
    params = {
        "spaceKey": space_key,
        "expand": "ancestors,body.storage",  # Include il corpo della pagina in formato HTML
        "limit": 100  # Modifica se necessario per ottenere più di 100 pagine
    }
    response = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD), params=params)
    response.raise_for_status()
    return response.json()["results"]

# Funzione per ottenere il percorso della gerarchia della pagina
def get_hierarchy_path(page):
    ancestors = page.get("ancestors", [])
    path = [clean_name(ancestor["title"]) for ancestor in ancestors]
    path.append(clean_name(page["title"]))
    return os.path.join(*path)

# Funzione per esportare una pagina in HTML
def export_page_to_html(page_id, page_path):
    # URL per ottenere il contenuto HTML della pagina
    url = f"{BASE_URL}/rest/api/content/{page_id}/body/storage"
    response = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD))
    
    if response.status_code == 200:
        content = response.json()["body"]["storage"]["value"]
        
        # Salva il contenuto HTML come file .html
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Pagina {page_id} esportata correttamente come HTML.")
    else:
        print(f"Errore nell'esportazione della pagina {page_id} come HTML: {response.status_code}")

# Funzione principale per eseguire l'export
def export_space():
    pages = get_pages(SPACE_KEY)
    for page in pages:
        page_path = os.path.join(OUTPUT_DIR, get_hierarchy_path(page) + ".html")
        os.makedirs(os.path.dirname(page_path), exist_ok=True)
        
        # Esporta la pagina come HTML
        export_page_to_html(page["id"], page_path)

# Esecuzione dello script
if __name__ == "__main__":
    export_space()
