import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
import io
from PIL import Image

# 1. Configuración de idiomas
LANGS = {
    "Español": {"t": "Modelo 145 - Registro de Conductores", "p1": "Datos Personales", "p2": "Hijos/Descendientes", "p3": "Ascendientes / Otros", "f": "Firma Digital", "d": "Descargar PDF Relleno"},
    "English": {"t": "Form 145 - Driver Registration", "p1": "Personal Data", "p2": "Children", "p3": "Elders / Other", "f": "Digital Signature", "d": "Download Filled PDF"},
    "Français": {"t": "Modèle 145 - Registre", "p1": "Données", "p2": "Enfants", "p3": "Ascendants", "f": "Signature", "d": "Télécharger"},
    "Deutsch": {"t": "Modell 145 - Fahrer", "p1": "Daten", "p2": "Kinder", "p3": "Vorfahren", "f": "Unterschrift", "d": "Herunterladen"},
    "Русский": {"t": "Модель 145 - Водители", "p1": "Данные", "p2": "Дети", "p3": "Родители", "f": "Подпись", "d": "Скачать"},
    "Polski": {"t": "Model 145 - Kierowcy", "p1": "Dane", "p2": "Dzieci", "p3": "Wstępni", "f": "Podpis", "d": "Pobierz"},
    "Українська": {"t": "Модель 145 - Водії", "p1": "Дані", "p2": "Діти", "p3": "Батьки", "f": "Підпис", "d": "Завантажити"}
}

# 2. Configuración de página y CSS para evitar "Negro sobre Negro"
st.set_page_config(page_title="App Modelo 145", layout="centered")

st.markdown("""
    <style>
    /* Forzar fondo claro y texto oscuro en todo el formulario */
    .stApp {
        background-color: #ffffff;
    }
    label, p, span, h1, h2, h3 {
        color: #1a1a1a !important;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        color: #000000;
        background-color: #f0f2f6;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4b5563;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo e Idioma
idioma = st.sidebar.selectbox("🌐 Seleccione su idioma / Select language", list(LANGS.keys()))
t = LANGS[idioma]

try:
    st.image("logo.png", width=250)
except:
    st.title("🏢") # Icono si no encuentra el logo.png

st.title(t["t"])
st.write("---")

# 4. Formulario con lógica condicional completa
with st.form("form_145_completo"):
    tab1, tab2, tab3 = st.tabs([t["p1"], t["p2"], t["p3"]])
    
    with tab1:
        c1, c2 = st.columns(2)
        nif = c1.text_input("NIF / NIE", placeholder="12345678X")
        nombre = c2.text_input("Apellidos y Nombre")
        
        c3, c4 = st.columns(2)
        nacimiento = c3.text_input("Año de nacimiento (YYYY)", placeholder="1985")
        situacion = st.selectbox("Situación Familiar", 
                                ["3 - Situación general (Soltero/Casado cónyuge >1500€)", 
                                 "1 - Soltero/Divorciado con hijos (Exclusividad)", 
                                 "2 - Casado y cónyuge con ingresos <1500€"])
        
        nif_conyuge = ""
        if "2 -" in situacion:
            nif_conyuge = st.text_input("NIF del Cónyuge")
            
        discapacidad = st.selectbox("Grado de Discapacidad", ["Ninguna", "Entre 33% y 65%", "Más del 65%"])
        movilidad = st.checkbox("Movilidad Geográfica (Aceptación de nuevo puesto)")

    with tab2:
        st.subheader("Hijos y otros descendientes (<25 años)")
        num_hijos = st.number_input("Número total de hijos", 0, 10, 0)
        hijos_discap = st.number_input("De los cuales, ¿cuántos con discapacidad?", 0, 10, 0)
        entero = st.checkbox("¿Computar hijos por entero? (Solo si NO conviven con el otro progenitor)")

    with tab3:
        st.subheader("Ascendientes (>65 años)")
        num_asc = st.number_input("Número de ascendientes a cargo", 0, 5, 0)
        pension = st.number_input("Pensión compensatoria a favor de cónyuge (€/año)", 0.0)
        hipoteca = st.checkbox("Deducción por vivienda habitual (adquirida antes de 2013)")

    st.write(f"### {t['f']}")
    st.caption("Firme dentro del cuadro gris usando su dedo o ratón")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        update_streamlit=True,
        key="canvas",
    )

    submit = st.form_submit_button(t["d"])

# 5. Lógica de Generación del PDF
if submit:
    if not nif or not nombre:
        st.error("Por favor, rellene el NIF y el Nombre.")
    else:
        try:
            # Crear capa de texto
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 10)

            # --- MAPEO DE COORDENADAS ---
            # Bloque 1
            can.drawString(57, 680, nif.upper())
            can.drawString(155, 680, nombre.upper())
            can.drawString(410, 680, nacimiento)
            
            # Situaciones (X)
            if "1 -" in situacion: can.drawString(64, 642, "X")
            if "2 -" in situacion: 
                can.drawString(64, 625, "X")
                can.drawString(205, 625, nif_conyuge.upper())
            if "3 -" in situacion: can.drawString(64, 608, "X")
            
            # Discapacidad
            if "33%" in discapacidad: can.drawString(427, 608, "X")
            if "65%" in discapacidad: can.drawString(500, 608, "X")
            if movilidad: can.drawString(427, 580, "X")

            # Hijos (Bloque 2)
            if num_hijos > 0:
                can.drawString(300, 510, str(num_hijos))
                if entero: can.drawString(355, 510, "X")

            # Ascendientes (Bloque 3)
            if num_asc > 0:
                can.drawString(300, 420, str(num_asc))

            # Vivienda y Pensiones (Bloque 4 y 5)
            if hipoteca: can.drawString(64, 305, "X")
            if pension > 0: can.drawString(400, 345, str(pension))

            # Firma
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                can.drawInlineImage(img, 80, 115, width=120, height=45)

            can.save()
            packet.seek(0)
            
            # Fusión con PDF original
            original = PdfReader(open("modelo145.pdf", "rb"))
            overlay = PdfReader(packet)
            output = PdfWriter()
            
            page = original.pages[0]
            page.merge_page(overlay.pages[0])
            output.add_page(page)
            
            # Añadir páginas restantes
            for i in range(1, len(original.pages)):
                output.add_page(original.pages[i])

            final_buf = io.BytesIO()
            output.write(final_buf)
            
            st.success("✅ ¡PDF Generado correctamente!")
            st.download_button(
                label=t["d"],
                data=final_buf.getvalue(),
                file_name=f"Modelo145_{nif}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Hubo un error al procesar el PDF: {e}")
