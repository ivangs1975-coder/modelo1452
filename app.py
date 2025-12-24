import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import datetime

# --- CONFIGURACIÓN DE IDIOMAS ---
languages = {
    "Español": {
        "tit": "Modelo 145 - Comunicación de Datos",
        "s1": "1. Datos del perceptor",
        "s2": "2. Hijos y descendientes",
        "s3": "3. Ascendientes",
        "s4": "4. Pensiones",
        "s5": "5. Vivienda Habitual",
        "firma": "6. Firma Digital",
        "descargar": "Generar PDF con Firma",
        "sit1": "Situación 1: Soltero/Divorciado con hijos en exclusiva",
        "sit2": "Situación 2: Casado (cónyuge con rentas < 1.500€)",
        "sit3": "Situación 3: Otras situaciones",
    },
    "English": {"tit": "Form 145", "s1": "1. Personal Data", "s2": "2. Children", "s3": "3. Ascendants", "s4": "4. Pensions", "s5": "5. Home Loan", "firma": "6. Digital Signature", "descargar": "Generate Signed PDF", "sit1": "Situation 1", "sit2": "Situation 2", "sit3": "Situation 3"},
    "Русский": {"tit": "Модель 145", "s1": "1. Данные", "s2": "2. Дети", "s3": "3. Предки", "s4": "4. Пенсии", "s5": "5. Жилье", "firma": "6. Подпись", "descargar": "Скачать PDF", "sit1": "Ситуация 1", "sit2": "Ситуация 2", "sit3": "Ситуация 3"},
    "Polski": {"tit": "Model 145", "s1": "1. Dane", "s2": "2. Dzieci", "s3": "3. Wstępni", "s4": "4. Emerytury", "s5": "5. Mieszkanie", "firma": "6. Podpis", "descargar": "Pobierz PDF", "sit1": "Sytuacja 1", "sit2": "Sytuacja 2", "sit3": "Sytuacja 3"},
    "Română": {"tit": "Model 145", "s1": "1. Date", "s2": "2. Copii", "s3": "3. Ascendenți", "s4": "4. Pensii", "s5": "5. Locuință", "firma": "6. Semnătura", "descargar": "Descarcă PDF", "sit1": "Situația 1", "sit2": "Situația 2", "sit3": "Situația 3"},
    "Українська": {"tit": "Модель 145", "s1": "1. Дані", "s2": "2. Діти", "s3": "3. Предки", "s4": "4. Пенсії", "s5": "5. Житло", "firma": "6. Підпис", "descargar": "Завантажити PDF", "sit1": "Ситуація 1", "sit2": "Ситуація 2", "sit3": "Ситуація 3"}
}

sel_lang = st.sidebar.selectbox("Idioma / Language", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- 1. DATOS PERSONALES ---
st.header(t["s1"])
c1, c2 = st.columns(2)
with c1:
    nif = st.text_input("NIF")
    nombre = st.text_input("Apellidos y Nombre")
with c2:
    f_nac = st.number_input("Año de nacimiento", 1930, 2024, 1980)
    discapacidad = st.selectbox("Minusvalía", ["No", ">=33%", ">=65%", "Movilidad"])

sit_familiar = st.radio("Situación Familiar", [t["sit1"], t["sit2"], t["sit3"]])

# --- 2. HIJOS ---
st.header(t["s2"])
num_hijos = st.number_input("Nº Hijos", 0, 10)
if num_hijos > 0:
    hijo_discap = st.checkbox("¿Algún hijo con discapacidad?")

# --- 4. PENSIONES ---
st.header(t["s4"])
p_alim = st.number_input("Anualidades alimentos hijos", 0.0)
p_comp = st.number_input("Pensión compensatoria cónyuge", 0.0)

# --- 5. VIVIENDA ---
st.header(t["s5"])
vivienda = st.checkbox("Deducción por vivienda habitual (adquirida antes de 2013)")

# --- 6. FIRMA ---
st.header(t["firma"])
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="#0000FF", # Azul tipo bolígrafo
    background_color="#FFFFFF",
    height=150, width=400, key="signature",
)

# --- PROCESAMIENTO ---
if st.button(t["descargar"]):
    if canvas_result.image_data is not None:
        # 1. Leer PDF original
        reader = PdfReader("MODELO_145.pdf")
        writer = PdfWriter()
        page = reader.pages[0]
        
        # 2. Rellenar campos de texto
        campos = {
            "NIF": nif,
            "APELLIDOS": nombre,
            "ANIO_NAC": str(f_nac),
        }
        # Marcar situación
        if sit_familiar == t["sit1"]: campos["SIT_1"] = "X"
        elif sit_familiar == t["sit2"]: campos["SIT_2"] = "X"
        else: campos["SIT_3"] = "X"
        
        writer.add_page(page)
        writer.update_page_form_field_values(writer.pages[0], campos)

        # 3. Crear capa de firma con ReportLab
        sig_map = io.BytesIO()
        can = canvas.Canvas(sig_map, pagesize=A4)
        
        # Convertir canvas a imagen PIL
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        
        # Dibujar la firma en coordenadas específicas (ajustar según tu PDF)
        # En el Modelo 145 la firma suele estar abajo a la derecha
        can.drawInlineImage(img, 380, 130, width=120, height=45) 
        can.save()
        
        # 4. Fusionar la firma con el PDF
        sig_map.seek(0)
        signature_pdf = PdfReader(sig_map)
        writer.pages[0].merge_page(signature_pdf.pages[0])

        # 5. Descargar
        output = io.BytesIO()
        writer.write(output)
        st.download_button("📥 Descargar Modelo 145 Firmado", output.getvalue(), "modelo145_final.pdf", "application/pdf")
    else:
        st.warning("Por favor, firma antes de generar el PDF.")
