import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import datetime

# --- CONFIGURACIÓN E IDIOMAS ---
languages = {
    "Español": {"tit": "Modelo 145 - AEAT", "btn": "Generar y Descargar PDF", "lugar": "Ciudad:"},
    "English": {"tit": "Form 145", "btn": "Generate PDF", "lugar": "City:"},
    "Русский": {"tit": "Модель 145", "btn": "Скачать", "lugar": "Город:"},
    "Polski": {"tit": "Model 145", "btn": "Pobierz", "lugar": "Miasto:"},
    "Română": {"tit": "Model 145", "btn": "Descarcă", "lugar": "Oraș:"},
    "Українська": {"tit": "Модель 145", "btn": "Завантажити", "lugar": "Місто:"}
}
sel_lang = st.sidebar.selectbox("Idioma", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- ENTRADA DE DATOS ---
st.header("1. Datos Personales")
col1, col2 = st.columns(2)
with col1:
    nif = st.text_input("NIF", key="nif")
    nombre = st.text_input("Apellidos y Nombre", key="nombre")
with col2:
    anio = st.number_input("Año de nacimiento", 1930, 2024, 1980)
    sit_fam = st.radio("Situación Familiar", ["1", "2", "3"], horizontal=True)

st.header("6. Lugar, Fecha y Firma")
c_lug, c_fec = st.columns(2)
with c_lug:
    lugar_input = st.text_input(t["lugar"], value="Madrid")
with c_fec:
    fecha_input = st.date_input("Fecha", datetime.date.today())

st.write("Firma:")
canvas_result = st_canvas(stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0", height=120, width=400, key="canvas")

# --- PROCESO DE GENERACIÓN CON MAPEO CORREGIDO ---
if st.button(t["btn"]):
    if nif and nombre:
        try:
            reader = PdfReader("MODELO_145.pdf")
            writer = PdfWriter()
            page = reader.pages[0]
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 10)

            # --- NUEVO MAPEO DE COORDENADAS (AJUSTADO AL MODELO 145) ---
            
            # SECCIÓN 1: Datos Personales (X, Y)
            # El NIF suele estar arriba a la izquierda
            can.drawString(55, 685, nif.upper())
            # Apellidos y nombre
            can.drawString(160, 685, nombre.upper())
            # Año nacimiento
            can.drawString(485, 685, str(anio))
            
            # CASILLAS DE SITUACIÓN FAMILIAR (Cruces 'X')
            # Coordenadas estimadas para los cuadraditos de situación
            if sit_fam == "1":
                can.drawString(45, 638, "X")
            elif sit_fam == "2":
                can.drawString(45, 595, "X")
            elif sit_fam == "3":
                can.drawString(45, 545, "X")

            # SECCIÓN 6: Lugar y Fecha (Línea de puntos al final)
            # En el snippet se ve: En [Lugar] a [Día] de [Mes] de [Año]
            can.drawString(255, 275, lugar_input) # "En..."
            can.drawString(342, 275, str(fecha_input.day)) # "a..."
            can.drawString(385, 275, str(fecha_input.month)) # "de..."
            can.drawString(450, 275, str(fecha_input.year)) # "de..."

            # FIRMA DIGITAL
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                # Posición del cuadro "Firma del perceptor"
                can.drawInlineImage(img, 385, 145, width=110, height=45)
            
            can.save()
            packet.seek(0)
            
            # Combinar capas
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

            out = io.BytesIO()
            writer.write(out)
            st.success("¡PDF generado!")
            st.download_button("📥 DESCARGAR", out.getvalue(), "modelo145_firmado.pdf", "application/pdf")

        except Exception as e:
            st.error(f"Error: {e}")
