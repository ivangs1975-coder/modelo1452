import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
import io
from PIL import Image
from datetime import datetime

# 1. Configuración de idiomas
LANGS = {
    "Español": {"t": "Modelo 145 - Empresa", "p1": "Datos Personales", "p2": "Hijos", "p3": "Ascendientes", "p4": "Otros", "f": "Firma", "d": "Descargar PDF"},
    "English": {"t": "Form 145 - Company", "p1": "Personal Data", "p2": "Children", "p3": "Elders", "p4": "Other", "f": "Signature", "d": "Download PDF"},
    "Polski": {"t": "Model 145", "p1": "Dane osobowe", "p2": "Dzieci", "p3": "Wstępni", "p4": "Inne", "f": "Podpis", "d": "Pobierz PDF"},
    "Українська": {"t": "Модель 145", "p1": "Особисті дані", "p2": "Діти", "p3": "Батьки", "p4": "Інше", "f": "Підпис", "d": "Завантажити"}
}

st.set_page_config(page_title="App Modelo 145", layout="centered")

# CSS para forzar colores claros y visibilidad de pestañas/botones
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, label, span { color: #000000 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #eeeeee; border-radius: 5px; }
    .stTabs [data-baseweb="tab"] { color: #000000 !important; }
    .stButton>button { background-color: #1e3a8a !important; color: white !important; }
    .stDownloadButton>button { background-color: #059669 !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

idioma = st.sidebar.selectbox("🌐 Idioma", list(LANGS.keys()))
t = LANGS[idioma]

try:
    st.image("logo.png", width=200)
except:
    st.title("🏢 Gestión Modelo 145")

# 3. Formulario
with st.form("main_form"):
    tab1, tab2, tab3, tab4 = st.tabs([t["p1"], t["p2"], t["p3"], t["p4"]])
    
    with tab1:
        c1, c2 = st.columns(2)
        nif = c1.text_input("NIF / NIE")
        nombre = c2.text_input("Apellidos y Nombre")
        año = st.text_input("Año Nacimiento (YYYY)")
        sit = st.radio("Situación Familiar:", ["1", "2", "3"], help="1: Soltero con hijos, 2: Casado cónyuge <1500€, 3: Otros")
        nif_c = st.text_input("NIF Cónyuge (si es sit. 2)")
        disc = st.selectbox("Discapacidad:", ["No", "33-65", "65", "Movilidad"])

    with tab2:
        hijos = st.number_input("Nº hijos", 0, 10)
        hijos_disc = st.number_input("Hijos con discapacidad", 0, 10)
        entero = st.checkbox("Cómputo por entero")

    with tab3:
        asc = st.number_input("Nº ascendientes", 0, 5)
        asc_disc = st.number_input("Ascendientes con discapacidad", 0, 5)

    with tab4:
        pension = st.number_input("Pensión compensatoria (€/año)", 0.0)
        alimentos = st.number_input("Anualidad alimentos (€/año)", 0.0)
        vivienda = st.checkbox("Hipotecas < 2013")

    st.write(f"### {t['f']}")
    canvas_result = st_canvas(stroke_width=2, stroke_color="black", background_color="#f0f0f0", height=120, key="canvas")
    submit = st.form_submit_button("PREPARAR DOCUMENTO")

# 4. Generación con coordenadas RE-CALIBRADAS
if submit:
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 9)

    # AJUSTE QUIRÚRGICO (Basado en el PDF desplazado enviado por el usuario)
    # He bajado la Y (segundo número) unos 30-40 puntos y movido la X a la derecha.
    
    # BLOQUE 1: Datos personales
    can.drawString(55, 650, nif.upper())          # NIF
    can.drawString(170, 650, nombre.upper())      # Nombre
    can.drawString(415, 650, año)                 # Año Nac
    
    if sit == "1": can.drawString(64, 616, "X")
    if sit == "2": 
        can.drawString(64, 600, "X")
        can.drawString(205, 600, nif_c.upper())
    if sit == "3": can.drawString(64, 584, "X")
    
    if "33" in disc: can.drawString(428, 584, "X")
    if "65" in disc: can.drawString(502, 584, "X")
    if "Mov" in disc: can.drawString(428, 556, "X")

    # BLOQUE 2: Hijos
    if hijos > 0:
        can.drawString(310, 488, str(hijos))
        if entero: can.drawString(365, 488, "X")
        if hijos_disc > 0: can.drawString(435, 488, str(hijos_disc))

    # BLOQUE 3: Ascendientes
    if asc > 0:
        can.drawString(310, 400, str(asc))
        if asc_disc > 0: can.drawString(435, 400, str(asc_disc))

    # BLOQUE 4 y 5
    if pension > 0: can.drawString(400, 326, f"{pension:.2f}")
    if alimentos > 0: can.drawString(400, 313, f"{alimentos:.2f}")
    if vivienda: can.drawString(64, 283, "X")

    # FIRMA Y FECHA
    hoy = datetime.now()
    can.drawString(215, 173, str(hoy.day))
    can.drawString(245, 173, str(hoy.month))
    can.drawString(285, 173, str(hoy.year))

    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        # Firma centrada en el recuadro del perceptor
        can.drawInlineImage(img, 70, 93, width=110, height=45)

    can.save()
    packet.seek(0)
    
    original = PdfReader(open("modelo145.pdf", "rb"))
    overlay = PdfReader(packet)
    writer = PdfWriter()
    page = original.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)
    for i in range(1, len(original.pages)): writer.add_page(original.pages[i])

    buf = io.BytesIO()
    writer.write(buf)
    
    st.success("✅ Documento listo")
    st.download_button(
        label=f"⬇️ {t['d']}",
        data=buf.getvalue(),
        file_name=f"MOD145_{nif.upper()}.pdf",
        mime="application/pdf"
    )
