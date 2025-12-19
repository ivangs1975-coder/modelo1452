import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
from PIL import Image

# Configuración de traducciones
LANGS = {
    "Español": {"t": "Modelo 145 - Comunicación de Datos", "p1": "Datos Personales", "p2": "Hijos/Descendientes", "p3": "Ascendientes", "p4": "Otros Datos", "f": "Firma del Conductor", "d": "Generar y Descargar"},
    "English": {"t": "Form 145 - Personal Data Communication", "p1": "Personal Data", "p2": "Children", "p3": "Elders", "p4": "Other Info", "f": "Driver Signature", "d": "Generate & Download"},
    "Français": {"t": "Modèle 145 - Données Personnelles", "p1": "Données", "p2": "Enfants", "p3": "Ascendants", "p4": "Autres", "f": "Signature", "d": "Générer PDF"},
    "Deutsch": {"t": "Modell 145 - Datenübermittlung", "p1": "Daten", "p2": "Kinder", "p3": "Vorfahren", "p4": "Sonstiges", "f": "Unterschrift", "d": "Herunterladen"},
    "Русский": {"t": "Модель 145 - Личные данные", "p1": "Данные", "p2": "Дети", "p3": "Родители", "p4": "Другое", "f": "Подпись", "d": "Скачать"},
    "Polski": {"t": "Model 145 - Dane osobowe", "p1": "Dane", "p2": "Dzieci", "p3": "Wstępni", "p4": "Inne", "f": "Podpis", "d": "Pobierz"},
    "Українська": {"t": "Модель 145 - Особисті дані", "p1": "Дані", "p2": "Діти", "p3": "Батьки", "p4": "Інше", "f": "Підпис", "d": "Завантажити"}
}

st.set_page_config(page_title="Form 145 Multi-lang", layout="wide")
idioma = st.sidebar.selectbox("🌐 Language", list(LANGS.keys()))
t = LANGS[idioma]

st.title(t["t"])

with st.form("form145"):
    tab1, tab2, tab3, tab4 = st.tabs([t["p1"], t["p2"], t["p3"], t["p4"]])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        nif = col1.text_input("NIF / NIE")
        apellidos_nombre = col2.text_input("Apellidos y Nombre")
        año_nac = col3.number_input("Año de nacimiento", 1940, 2010, 1980)
        
        situacion = st.radio("Situación Familiar", ["1", "2", "3"], help="1: Soltero/Divorciado con hijos. 2: Casado con cónyuge con ingresos bajos. 3: Resto de situaciones.")
        nif_conyuge = ""
        if situacion == "2":
            nif_conyuge = st.text_input("NIF del Cónyuge")
            
        discap = st.selectbox("Grado de discapacidad", ["No", ">=33% y <65%", ">=65%"])
        movilidad = st.checkbox("Movilidad Geográfica (Nuevo puesto tras desempleo)")

    with tab2:
        st.info("Hijos menores de 25 años o mayores con discapacidad")
        num_hijos = st.number_input("Número de hijos", 0, 10)
        hijos_por_entero = st.checkbox("¿Computar hijos por entero? (Solo conviven con usted)")

    with tab3:
        num_ascendientes = st.number_input("Ascendientes >65 años a cargo", 0, 5)

    with tab4:
        pension = st.number_input("Pensión compensatoria cónyuge (€/año)", 0.0)
        alimentos = st.number_input("Anualidades alimentos hijos (€/año)", 0.0)
        hipoteca = st.checkbox("Deducción por vivienda habitual (adquirida antes de 2013)")

    st.markdown(f"### {t['f']}")
    canvas_result = st_canvas(fill_color="white", stroke_width=2, stroke_color="black", background_color="#eee", height=150, key="signature")

    submit = st.form_submit_button(t["d"])

if submit:
    # --- PROCESO DE RELLENADO ---
    reader = PdfReader("modelo145.pdf")
    writer = PdfWriter()
    page = reader.pages[0]
    
    # Mapeo exacto a los campos del PDF oficial
    # Estos nombres corresponden a la estructura interna del modelo AEAT 145
    fields = {
        "F_1": nif,
        "F_2": apellidos_nombre,
        "F_3": str(año_nac),
        "F_4": "X" if situacion == "1" else "",
        "F_5": "X" if situacion == "2" else "",
        "F_6": nif_conyuge,
        "F_7": "X" if situacion == "3" else "",
        "F_8": "X" if discap == ">=33% y <65%" else "",
        "F_9": "X" if discap == ">=65%" else "",
        "F_11": "X" if movilidad else "",
        "F_25": str(num_hijos) if num_hijos > 0 else "",
        "F_26": "X" if hijos_por_entero else "",
        "F_32": str(num_ascendientes) if num_ascendientes > 0 else "",
        "F_41": str(pension) if pension > 0 else "",
        "F_42": str(alimentos) if alimentos > 0 else "",
        "F_43": "X" if hipoteca else ""
    }

    writer.add_page(page)
    writer.update_page_form_field_values(writer.pages[0], fields)

    # --- PROCESO DE FIRMA ---
    if canvas_result.image_data is not None:
        # Convertir canvas a imagen y estampar en PDF
        sig_img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        # Coordenadas ajustadas para el espacio de firma del Modelo 145
        can.drawInlineImage(sig_img, 70, 110, width=120, height=40)
        can.save()
        packet.seek(0)
        
        sig_pdf = PdfReader(packet)
        writer.pages[0].merge_page(sig_pdf.pages[0])

    # --- DESCARGA ---
    output_stream = io.BytesIO()
    writer.write(output_stream)
    st.success("✅ PDF Listo")
    st.download_button(t["d"], output_stream.getvalue(), f"145_{nif}.pdf", "application/pdf")
