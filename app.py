import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
import io
from PIL import Image
from datetime import datetime

# 1. Traducciones y Textos de Situación
LANGS = {
    "Español": {"t": "Modelo 145 - Empresa", "p1": "Datos Personales", "p2": "Hijos/Descendientes", "p3": "Ascendientes", "p4": "Otros Datos", "f": "Firma", "d": "Descargar PDF"},
    "English": {"t": "Form 145 - Company", "p1": "Personal Data", "p2": "Children", "p3": "Elders", "p4": "Other", "f": "Signature", "d": "Download PDF"},
    "Polski": {"t": "Model 145", "p1": "Dane osobowe", "p2": "Dzieci", "p3": "Wstępni", "p4": "Inne", "f": "Podpis", "d": "Pobierz PDF"},
    "Українська": {"t": "Модель 145", "p1": "Особисті дані", "p2": "Діти", "p3": "Батьки", "p4": "Інше", "f": "Підпис", "d": "Завантажити"}
}

st.set_page_config(page_title="App Modelo 145", layout="centered")

# 2. CSS para arreglar colores (Botones azules, Pestañas visibles)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, label, span { color: #000000 !important; }
    
    /* Arreglar Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #000000 !important; font-weight: bold; }
    
    /* Arreglar Botón de descarga */
    .stButton>button {
        background-color: #1e3a8a !important;
        color: white !important;
        border-radius: 5px;
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stDownloadButton>button {
        background-color: #059669 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

idioma = st.sidebar.selectbox("🌐 Idioma", list(LANGS.keys()))
t = LANGS[idioma]

try:
    st.image("logo.png", width=220)
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
        
        sit = st.radio("Situación Familiar:", [
            "1. Soltero/Divorciado con hijos (en exclusividad)",
            "2. Casado/a y cónyuge no gana más de 1.500€/año",
            "3. Otras situaciones (Solteros sin hijos, casados con ingresos, etc.)"
        ])
        
        nif_c = ""
        if "2." in sit: nif_c = st.text_input("NIF Cónyuge")
        
        disc = st.selectbox("Discapacidad:", ["No", "Grado >= 33%", "Grado >= 65%"])
        movilidad = st.checkbox("Movilidad Geográfica")

    with tab2:
        hijos = st.number_input("Nº hijos menores de 25 años", 0, 10)
        hijos_disc = st.number_input("De ellos, con discapacidad", 0, 10)
        entero = st.checkbox("Cómputo por entero (solo usted convive con ellos)")

    with tab3:
        asc = st.number_input("Nº ascendientes mayores de 65 años", 0, 5)
        asc_disc = st.number_input("De ellos, con discapacidad", 0, 5)

    with tab4:
        pension = st.number_input("Pensión compensatoria cónyuge (€/año)", 0.0)
        alimentos = st.number_input("Anualidad alimentos hijos (€/año)", 0.0)
        vivienda = st.checkbox("Deducción vivienda habitual (compra antes de 2013)")

    st.write(f"### {t['f']}")
    canvas_result = st_canvas(stroke_width=2, stroke_color="black", background_color="#f0f0f0", height=120, key="canvas")
    
    submit = st.form_submit_button("PREPARAR DOCUMENTO")

# 4. Generación con coordenadas corregidas (Remapeo)
if submit:
    if not nif or not nombre:
        st.error("DNI y Nombre son obligatorios")
    else:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont("Helvetica", 10)

        # BLOQUE 1 (Ajustado: + X para derecha, - Y para bajar)
        can.drawString(60, 672, nif.upper())
        can.drawString(170, 672, nombre.upper())
        can.drawString(415, 672, año)
        
        if "1." in sit: can.drawString(64, 638, "X")
        if "2." in sit: 
            can.drawString(64, 622, "X")
            can.drawString(205, 622, nif_c.upper())
        if "3." in sit: can.drawString(64, 606, "X")
        
        if "33%" in disc: can.drawString(428, 606, "X")
        if "65%" in disc: can.drawString(502, 606, "X")
        if movilidad: can.drawString(428, 578, "X")

        # BLOQUE 2 (Hijos)
        if hijos > 0:
            can.drawString(310, 510, str(hijos))
            if entero: can.drawString(365, 510, "X")
            if hijos_disc > 0: can.drawString(435, 510, str(hijos_disc))

        # BLOQUE 3 (Ascendientes)
        if asc > 0:
            can.drawString(310, 422, str(asc))
            if asc_disc > 0: can.drawString(435, 422, str(asc_disc))

        # BLOQUE 4 y 5
        if pension > 0: can.drawString(410, 348, f"{pension:.2f}")
        if alimentos > 0: can.drawString(410, 335, f"{alimentos:.2f}")
        if vivienda: can.drawString(64, 305, "X")

        # FIRMA Y FECHA
        fecha = datetime.now()
        can.drawString(225, 195, str(fecha.day))
        can.drawString(255, 195, str(fecha.month))
        can.drawString(295, 195, str(fecha.year))

        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            can.drawInlineImage(img, 75, 115, width=110, height=45)

        can.save()
        packet.seek(0)
        
        original = PdfReader(open("modelo145.pdf", "rb"))
        overlay = PdfReader(packet)
        writer = PdfWriter()
        
        page = original.pages[0]
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
        
        for i in range(1, len(original.pages)):
            writer.add_page(original.pages[i])

        buf = io.BytesIO()
        writer.write(buf)
        
        st.success("✅ Documento listo")
        st.download_button(
            label=f"⬇️ {t['d']}",
            data=buf.getvalue(),
            file_name=f"MOD145_{nif.upper()}.pdf",
            mime="application/pdf"
        )
