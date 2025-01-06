import os
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import docx
import chardet

# Definisci le variabili
WEBDAV_URL =
USERNAME =
PASSWORD =


# Collegati al server Confluence
auth = (USERNAME, PASSWORD)

# Scarica il contenuto della pagina web
response = requests.get(WEBDAV_URL, auth=auth)
html = response.content

# Determina la codifica del contenuto
encoding = chardet.detect(html)['encoding']

# Decodifica il contenuto
html = html.decode(encoding, errors='replace')

# Parsa il contenuto con Beautiful Soup
soup = BeautifulSoup(html, "html.parser")

# Trova i link alle pagine che desideri scaricare
links = soup.find_all("a")


# Definisci la funzione crea_documento_pdf
def crea_documento_pdf(html, path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    soup = BeautifulSoup(html, "html.parser")
    for paragraph in soup.find_all('p'):
        pdf.cell(0, 10, txt=paragraph.text, ln=True, align='L')
    pdf.output(path)


# Definisci la funzione crea_documento_docx
def crea_documento_docx(html, path):
    doc = docx.Document()
    soup = BeautifulSoup(html, "html.parser")
    for paragraph in soup.find_all('p'):
        doc.add_paragraph(paragraph.text)
    doc.save(path)


for link in links:
    url = link.get("href")
    if url.startswith(WEBDAV_URL):
        # Scarica la cartella
        cartella = url.split("/")[-1]
        percorso_cartella = os.path.join("export", cartella)
        if not os.path.exists(percorso_cartella):
            os.makedirs(percorso_cartella)

        # Scarica i file all'interno della cartella
        response = requests.get(url, auth=auth)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        for file in soup.find_all("a"):
            file_url = file.get("href")
            if file_url.startswith(WEBDAV_URL):
                # Scarica il file
                file_response = requests.get(file_url, auth=auth)
                file_html = file_response.content
                file_soup = BeautifulSoup(file_html, "html.parser")
                # Salva il file
                file_name = file_url.split("/")[-1]
                file_path = os.path.join(percorso_cartella, file_name)
                with open(file_path, "wb") as file:
                    file.write(file_html)