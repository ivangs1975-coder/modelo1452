import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
import io
from PIL import Image
from datetime import datetime

# Traducciones completas
LANGS = {
    "Español": {"t": "Modelo 145", "p1": "1. Datos Personales", "p2": "2. Hijos y Descendientes", "p3": "3. Ascendientes", "p4": "4 y 5. Pensiones y Vivienda", "f": "6. Firma", "d": "Descargar PDF"},
    "English": {"t": "Form 145", "p1": "1. Personal Data", "p2": "2. Children", "p3": "3. Elders", "p4": "4 & 5. Alimony/Mortgage", "f": "6. Signature", "d": "Download PDF"},
    "Polski": {"t": "Model 145", "p1": "1. Dane osobowe", "p2": "2. Dzieci", "p3": "3. Wstępni", "p4": "4 i 5. Alimenty/Kredyt", "f": "6. Podpis", "d": "Pobierz PDF"},
    "Українська": {"t": "Модель 145", "p1": "1. Особисті дані", "p2": "2. Діти", "p3": "3. Батьки", "p4": "4 і 5. Аліменти/Іпотека", "f": "6. Підпис", "d": "Завантажити"}
}

st.set_page_config(page_title="App Modelo 145", layout="wide")

# Forzar visibilidad (Texto negro sobre fondo claro)
st.markdown("""<style> .stApp { background-color: white; } label, p, h1, h2, h3 { color: black !important; } </style>""", unsafe_allow_html=True)

idioma = st.sidebar.selectbox("🌐 Idioma / Language", list(LANGS.keys()))
t = LANGS[idioma]

try:
    st.image("logo.png", width=200)
except:
    st.title("🏢 Empresa Transportes")

st.title(t["t"])

with st.form("form_completo"):
    tab1, tab2, tab3, tab4 = st.tabs([t["p1"], t["p2"], t["p3"], t["p4"]])
    
    with tab1:
        c1, c2 = st.columns(2)
        nif = c1.text_input("NIF / NIE")
        nombre = c2.text_input("Apellidos y Nombre")
        nacimiento = st.text_input("Año de nacimiento (YYYY)")
        situacion = st.radio("Situación Familiar", ["1", "2", "3"], help="1: Soltero con hijos, 2: Casado con cónyuge bajos ingresos, 3: Otros")
        nif_conyuge = st.text_input("NIF Cónyuge (Solo si marcó situación 2)")
        discap = st.selectbox("Discapacidad", ["No", ">=33% y <65%", ">=65%", "Movilidad reducida"])

    with tab2:
        st.write("Hijos o descendientes menores de 25 años:")
        num_hijos = st.number_input("Nº hijos totales", 0, 10)
        hijos_discap_33 = st.number_input("Nº hijos con discapacidad >33%", 0, 10)
        hijos_discap_65 = st.number_input("Nº hijos con discapacidad >65%", 0, 10)
        hijos_entero = st.checkbox("¿Hijos computados por entero? (Solo usted convive con ellos)")

    with tab3:
        st.write("Ascendientes mayores de 65 años a cargo:")
        num_asc = st.number_input("Nº ascendientes totales", 0, 10)
        asc_discap_33 = st.number_input("Nº ascendientes con discapacidad >33%", 0, 10)
        asc_discap_65 = st.number_input("Nº ascendientes con discapacidad >65%", 0, 10)

    with tab4:
        pension = st.number_input("Pensión compensatoria al cónyuge (€/año)", 0.0)
        alimentos = st.number_input("Anualidad alimentos hijos (€/año)", 0.0)
        vivienda = st.checkbox("Pagos por hipoteca vivienda habitual (antes de 2013)")

    st.write(f"### {t['f']}")
    canvas_result = st_canvas(stroke_width=2, stroke_color="black", background_color="#eee", height=120, key="signature")
    
    enviar = st.form_submit_button(t["d"])

if enviar:
    # 1. Crear capa de texto (COORDENADAS MAREADAS SEGÚN EL PDF)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 9)

    # BLOQUE 1: Datos personales
    can.drawString(55, 680, nif.upper())
    can.drawString(155, 680, nombre.upper())
    can.drawString(412, 680, nacimiento)
    if situacion == "1": can.drawString(63, 641, "X")
    if situacion == "2": 
        can.drawString(63, 625, "X")
        can.drawString(205, 625, nif_conyuge.upper())
    if situacion == "3": can.drawString(63, 609, "X")
    if "33%" in discap: can.drawString(428, 609, "X")
    if "65%" in discap: can.drawString(502, 609, "X")

    # BLOQUE 2: Hijos
    if num_hijos > 0:
        can.drawString(300, 510, str(num_hijos))
        if hijos_entero: can.drawString(355, 510, "X")
        if hijos_discap_33 > 0: can.drawString(428, 510, str(hijos_discap_33))
        if hijos_discap_65 > 0: can.drawString(502, 510, str(hijos_discap_65))

    # BLOQUE 3: Ascendientes
    if num_asc > 0:
        can.drawString(300, 420, str(num_asc))
        if asc_discap_33 > 0: can.drawString(428, 420, str(asc_discap_33))
        if asc_discap_65 > 0: can.drawString(502, 420, str(asc_discap_65))

    # BLOQUE 4 y 5: Pensiones y Vivienda
    if pension > 0: can.drawString(400, 348, f"{pension:.2f}")
    if alimentos > 0: can.drawString(400, 335, f"{alimentos:.2f}")
    if vivienda: can.drawString(63, 305, "X")

    # BLOQUE 6: Fecha y Firma
    fecha_hoy = datetime.now().strftime("%d %m %Y")
    can.drawString(100, 195, "Madrid") # Ciudad (puedes hacerla campo de texto)
    can.drawString(215, 195, fecha_hoy.split()[0])
    can.drawString(245, 195, fecha_hoy.split()[1])
    can.drawString(285, 195, fecha_hoy.split()[2])

    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        can.drawInlineImage(img, 70, 115, width=110, height=40)

    can.save()
    packet.seek(0)
    
    # 2. Fusionar
    original = PdfReader(open("modelo145.pdf", "rb"))
    overlay = PdfReader(packet)
    output = PdfWriter()
    
    p = original.pages[0]
    p.merge_page(overlay.pages[0])
    output.add_page(p)
    
    for i in range(1, len(original.pages)):
        output.add_page(original.pages[i])

    res_buf = io.BytesIO()
    output.write(res_buf)
    st.success("PDF Generado")
    st.download_button(t["d"], res_buf.getvalue(), f"145_{nif}.pdf", "application/pdf")
