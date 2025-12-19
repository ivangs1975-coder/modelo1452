import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
import io
from PIL import Image
from datetime import datetime

# 1. Configuración de Estilo y Visibilidad
st.set_page_config(page_title="Modelo 145 Profesional", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: white; }
    label, p, h1, h2, h3, span { color: black !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 5px; }
    .stTabs [data-baseweb="tab"] { color: black !important; font-weight: bold; }
    .stButton>button { background-color: #1e3a8a !important; color: white !important; width: 100%; height: 3em; }
    .stDownloadButton>button { background-color: #059669 !important; color: white !important; width: 100%; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

try:
    st.image("logo.png", width=220)
except:
    st.write("🏢 **Gestión Modelo 145**")

# 2. Formulario Multi-pestaña
with st.form("form_hibrido"):
    tab1, tab2, tab3 = st.tabs(["📋 Datos Personales", "👪 Familia", "🖋️ Otros y Firma"])
    
    with tab1:
        c1, c2 = st.columns(2)
        nif = c1.text_input("NIF / NIE")
        nombre = c2.text_input("Apellidos y Nombre")
        año_nac = st.text_input("Año de nacimiento (YYYY)")
        sit = st.radio("Situación Familiar", ["1", "2", "3"])
        nif_c = st.text_input("NIF Cónyuge (Solo situación 2)")
        
    with tab2:
        hijos = st.number_input("Nº Hijos", 0, 10)
        asc = st.number_input("Nº Ascendientes", 0, 10)
        
    with tab3:
        vivienda = st.checkbox("Deducción Vivienda (Hipotecas < 2013)")
        st.write("### Firma en el recuadro gris")
        canvas_result = st_canvas(stroke_width=2, stroke_color="black", background_color="#f0f0f0", height=130, key="sig")

    submit = st.form_submit_button("GENERAR PDF CON FECHA DE HOY")

# 3. Lógica de Procesamiento
if submit:
    if not nif or not nombre:
        st.error("DNI y Nombre son campos obligatorios")
    else:
        # A. Preparar Escritor con soporte para Formularios (AcroForms)
        reader = PdfReader("modelo145.pdf")
        writer = PdfWriter()
        
        # Copiar metadatos de formulario para que el mapeo funcione
        if "/AcroForm" not in writer.root_object:
            writer.root_object.update({"/AcroForm": reader.trailer["/Root"].get("/AcroForm", {})})

        writer.add_page(reader.pages[0])

        # B. Rellenar campos de texto (Mapeo Automático)
        fields = {
            "F_1": nif.upper(),
            "F_2": nombre.upper(),
            "F_3": año_nac,
            "F_4": "X" if sit == "1" else "",
            "F_5": "X" if sit == "2" else "",
            "F_6": nif_c.upper(),
            "F_7": "X" if sit == "3" else "",
            "F_25": str(hijos) if hijos > 0 else "",
            "F_32": str(asc) if asc > 0 else "",
            "F_43": "X" if vivienda else ""
        }
        writer.update_page_form_field_values(writer.pages[0], fields)

        # C. Capa para Firma y Fecha Automática
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont("Helvetica", 10)
        
        # Lógica de Fecha (Apartado 6)
        hoy = datetime.now()
        can.drawString(223, 195, str(hoy.day).zfill(2))   # Casilla Día
        can.drawString(254, 195, str(hoy.month).zfill(2)) # Casilla Mes
        can.drawString(290, 195, str(hoy.year))           # Casilla Año

        # Firma Táctil
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            # Coordenadas recalibradas para el recuadro "Firma del perceptor"
            can.drawInlineImage(img, 72, 110, width=120, height=50)

        can.save()
        packet.seek(0)
        
        # D. Fusión
        overlay = PdfReader(packet)
        writer.pages[0].merge_page(overlay.pages[0])
        
        # Añadir páginas extra (instrucciones)
        for i in range(1, len(reader.pages)):
            writer.add_page(reader.pages[i])

        buf = io.BytesIO()
        writer.write(buf)
        
        st.success(f"✅ Formulario completado hoy {hoy.strftime('%d/%m/%Y')}")
        st.download_button(
            label="⬇️ DESCARGAR MODELO 145",
            data=buf.getvalue(),
            file_name=f"MOD145_{nif.upper()}.pdf",
            mime="application/pdf"
        )
