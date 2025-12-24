import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import datetime

# --- IDIOMAS ---
languages = {
    "Español": {"tit": "Modelo 145", "btn": "Generar PDF", "lugar": "En:", "fecha": "Fecha:"},
    "English": {"tit": "Form 145", "btn": "Generate PDF", "lugar": "At:", "fecha": "Date:"},
    "Русский": {"tit": "Модель 145", "btn": "Скачать", "lugar": "В:", "fecha": "Дата:"},
    "Polski": {"tit": "Model 145", "btn": "Pobierz", "lugar": "W:", "fecha": "Data:"},
    "Română": {"tit": "Model 145", "btn": "Descarcă", "lugar": "În:", "fecha": "Data:"},
    "Українська": {"tit": "Модель 145", "btn": "Завантажити", "lugar": "В:", "fecha": "Дата:"}
}
sel_lang = st.sidebar.selectbox("Idioma", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- TODOS LOS CAMPOS QUE YA FUNCIONABAN ---
st.header("1. Datos Personales")
col1, col2 = st.columns(2)
with col1:
    nif = st.text_input("NIF", key="nif")
    nombre = st.text_input("Apellidos y Nombre", key="nombre")
with col2:
    anio = st.number_input("Año de nacimiento", 1930, 2024, 1980)
    sit_fam = st.radio("Situación Familiar", ["1", "2", "3"], horizontal=True)

st.header("2. Hijos / 4. Pensiones / 5. Vivienda")
c3, c4, c5 = st.columns(3)
with c3:
    num_hijos = st.number_input("Nº Hijos", 0, 10)
with c4:
    p_comp = st.number_input("Pensión Comp.", 0.0)
with c5:
    vivienda = st.checkbox("Deducción Vivienda")

# --- LUGAR, FECHA Y FIRMA ---
st.header("6. Lugar, Fecha y Firma")
c_lug, c_fec = st.columns(2)
with c_lug:
    lugar_input = st.text_input(t["lugar"], value="Madrid")
with c_fec:
    fecha_input = st.date_input(t["fecha"], datetime.date.today())

st.write("Firma del perceptor:")
canvas_result = st_canvas(stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0", height=120, width=400, key="canvas")

# --- PROCESO DE GENERACIÓN POR COORDENADAS (EVITA EL ERROR ACROFORM) ---
if st.button(t["btn"]):
    if nif and nombre:
        try:
            reader = PdfReader("MODELO_145.pdf")
            writer = PdfWriter()
            page = reader.pages[0]
            
            # Capa para escribir encima
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 10)

            # --- COORDENADAS PARA EL MODELO 145 (Ajustadas a tu PDF) ---
            # SECCIÓN 1
            can.drawString(75, 688, nif.upper())
            can.drawString(165, 688, nombre.upper())
            can.drawString(485, 688, str(anio))
            
            # Situación Familiar (X en la casilla correspondiente)
            if sit_fam == "1": can.drawString(67, 628, "X")
            elif sit_fam == "2": can.drawString(67, 588, "X")
            else: can.drawString(67, 540, "X")

            # SECCIÓN 4 (Pensiones)
            if p_comp > 0: can.drawString(410, 395, str(p_comp))
            # SECCIÓN 5 (Vivienda)
            if vivienda: can.drawString(500, 315, "X")

            # SECCIÓN 6 (Lugar y Fecha)
            # En el snippet dice: "En... dia... de... de..."
            can.drawString(255, 267, lugar_input) # Lugar
            can.drawString(342, 267, str(fecha_input.day)) # Día
            can.drawString(380, 267, str(fecha_input.month)) # Mes
            can.drawString(445, 267, str(fecha_input.year)) # Año

            # FIRMA
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                # Dibujamos la firma en el espacio "Firma del perceptor"
                can.drawInlineImage(img, 385, 135, width=105, height=45)
            
            can.save()
            packet.seek(0)
            
            # Mezclar la capa de datos con la página original
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

            # Descarga
            out = io.BytesIO()
            writer.write(out)
            st.success("¡PDF generado correctamente!")
            st.download_button("📥 DESCARGAR", out.getvalue(), "modelo145_firmado.pdf", "application/pdf")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Completa NIF y Nombre")
