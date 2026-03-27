import streamlit as st
import os
from google import genai
from fpdf import FPDF
from dotenv import load_dotenv
from PIL import Image
import io

# Chargement des variables d'environnement (GEMINI_API_KEY)
load_dotenv()

# Configuration de la page pour le mobile
st.set_page_config(page_title="Audit Énergétique Pro", page_icon="⚡", layout="centered")

# Initialisation du client Gemini
# Assure-toi que la variable GEMINI_API_KEY est dans ton fichier .env
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("Veuillez configurer GEMINI_API_KEY dans votre fichier .env")

def generate_pdf(client_name, surface, analysis_text):
    """Génère un rapport PDF avec fpdf2 (équivalent de jspdf)"""
    pdf = FPDF()
    pdf.add_page()
    
    # Titre
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Rapport d'Audit Énergétique Pro", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # Informations Client
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Client : {client_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Surface : {surface} m²", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Analyse de l'IA
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Analyse Technique (Générée par IA) :", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.multi_cell(0, 8, analysis_text)
    
    return pdf.output(dest="S")

# --- INTERFACE UTILISATEUR ---

st.title("⚡ Audit Énergétique Pro")
st.write("Application mobile pour visites techniques et calculs automatiques.")

with st.form("audit_form"):
    st.subheader("Informations générales")
    client_name = st.text_input("Nom du client ou référence de l'audit")
    surface = st.number_input("Surface à auditer (m²)", min_value=1, value=100)
    
    st.subheader("Visite Technique")
    st.info("Prenez une photo de l'installation (chaudière, isolation, fenêtres...)")
    # L'équivalent de la permission "camera" demandée dans metadata.json
    camera_image = st.camera_input("Prendre une photo")
    
    submit_button = st.form_submit_button("Générer le rapport automatique", type="primary")

# --- LOGIQUE DE TRAITEMENT ---

if submit_button:
    if not camera_image:
        st.warning("Veuillez prendre une photo pour lancer l'analyse.")
    elif not api_key:
        st.error("Clé API Gemini introuvable.")
    else:
        with st.spinner("Analyse de l'image par Gemini IA..."):
            try:
                # Préparation de l'image pour Gemini
                img = Image.open(camera_image)
                
                # Prompt pour l'IA
                prompt = (
                    "Tu es un expert en rénovation énergétique. "
                    "Analyse cette image prise lors d'un audit technique. "
                    "Identifie l'équipement ou le matériau, note les défauts visibles (déperdition thermique, "
                    "vétusté) et suggère 2 recommandations de travaux d'amélioration énergétique."
                )
                
                # Appel à l'API Gemini 
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[img, prompt]
                )
                
                analysis_result = response.text
                
                st.success("Analyse terminée avec succès !")
                st.subheader("Diagnostic de l'IA")
                st.write(analysis_result)
                
                # Génération du PDF
                pdf_bytes = generate_pdf(client_name, surface, analysis_result)
                
                # Bouton de téléchargement
                st.download_button(
                    label="📄 Télécharger le Rapport PDF",
                    data=pdf_bytes,
                    file_name=f"audit_{client_name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'analyse : {e}")