import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import datetime

# --- CONFIGURACIÓN E IDIOMAS (Sin cambios para no perder nada) ---
languages = {
    "Español": {
        "tit": "Modelo 145 - Comunicación de Datos",
        "s1": "1. Datos del perceptor", "s2": "2. Hijos y descendientes", 
        "s3": "3. Ascendientes", "s4": "4. Pensiones", "s5": "5. Vivienda", "s6": "6. Firma",
        "sit1": "1. Soltero, viudo, divorciado o separado legalmente con hijos",
        "sit2": "2. Casado y no separado cuyo cónyuge no obtiene rentas > 1.500€",
        "sit3": "3. Situación familiar distinta de las anteriores",
        "lugar": "En (Lugar):", "btn": "Generar y Descargar PDF"
    },
    "English": {"tit": "Form 145", "s1": "1. Personal Data", "s6": "6. Signature", "lugar": "In:", "btn": "Download PDF"},
    "Русский": {"tit": "Модель 145", "s1": "Данные", "s6": "Подпись", "lugar": "В:", "btn": "Скачать"},
    "Polski": {"tit": "Model 145", "s1": "Dane", "s6": "Podpis", "lugar": "W:", "btn": "Pobierz"},
    "Română": {"tit": "Model 145", "s1": "Date", "s6": "Semnătura", "lugar": "În:", "btn": "Descarcă"},
    "Українська": {"tit": "Модель 145", "s1": "Дані", "s6": "Підпис", "lugar": "В:", "btn": "Завантажити"}
}

sel_lang = st.sidebar.selectbox("Idioma / Language", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- ENTRADA DE DATOS (Mantenemos todos los campos) ---
st.header(t["s1"])
col1, col2 = st.columns(2)
with col1:
    nif = st.text_input("NIF")
    nombre = st.text_input("Apellidos y Nombre")
with col2:
    anio_nac = st.number_input("Año de nacimiento", 1930, 2024, 1985)
    discapacidad = st.selectbox("Discapacidad", ["No", ">=33% e <65%", ">=65%", "Movilidad reducida"])

situacion = st.radio("Situación Familiar:", [t["sit1"], t["sit2"], t["sit3"]])
nif_conyuge = ""
if situacion == t["sit2"]:
    nif_conyuge = st.text_input("NIF del cónyuge")

st.header(t["s4"])
pension = st.number_input("Pensión compensatoria cónyuge", 0.0)
alimentos = st.number_input("Anualidad alimentos hijos", 0.0)

st.header(t["s5"])
vivienda = st.checkbox("Pagos por adquisición vivienda habitual (antes de 2013)")

st.header(t["s6"])
c_l, c_f = st.columns(2)
with c_l:
    lugar = st.text_input(t["lugar"], value="Madrid")
with c_f:
    fecha = st.date_input("Fecha", datetime.date.today())

canvas_result = st_canvas(stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0", height=120, width=400, key="canvas")

# --- PROCESAMIENTO CON COORDENADAS CORREGIDAS ---
if st.button(t["btn"]):
    if nif and nombre:
        try:
            reader = PdfReader("MODELO_145.pdf")
            writer = PdfWriter()
            page = reader.pages[0]
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 9)

            # --- SECCIÓN 1: Datos Perceptor ---
            can.drawString(55, 688, nif.upper())               
            can.drawString(160, 688, nombre.upper())           
            can.drawString(482, 688, str(anio_nac))            
            
            if situacion == t["sit1"]:
                can.drawString(45, 642, "X")                   
            elif situacion == t["sit2"]:
                can.drawString(45, 595, "X")                   
                can.drawString(150, 580, nif_conyuge.upper())  
            else:
                can.drawString(45, 545, "X")                   

            # --- SECCIÓN 4 & 5 ---
            if pension > 0: can.drawString(420, 400, f"{pension:.2f}")
            if alimentos > 0: can.drawString(420, 385, f"{alimentos:.2f}")
            if vivienda: can.drawString(500, 320, "X")

            # --- SECCIÓN 6: Lugar y Fecha (Corregido para no irse a la derecha) ---
            can.drawString(55, 271, lugar)                     # "En..." [cite: 103]
            can.drawString(125, 271, str(fecha.day))           # "día..." [cite: 92]
            can.drawString(155, 271, str(fecha.month))         # "de..." [cite: 93]
            can.drawString(210, 271, str(fecha.year))          # "de..." [cite: 94]

            # --- FIRMA (Corregida: más abajo y más a la izquierda) ---
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                # Bajamos Y a 120 y X a 330 para centrarla en "Firma del perceptor" 
                can.drawInlineImage(img, 330, 120, width=110, height=45)
            
            can.save()
            packet.seek(0)
            
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)
            
            output = io.BytesIO()
            writer.write(output)
            st.download_button("📥 DESCARGAR PDF", output.getvalue(), "modelo145.pdf", "application/pdf")

        except Exception as e:
            st.error(f"Error: {e}")
