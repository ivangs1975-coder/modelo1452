import streamlit as st
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, DictionaryObject
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import datetime

# --- CONFIGURACIÓN E IDIOMAS (Mantenemos tus 6 idiomas) ---
languages = {
    "Español": {"tit": "Modelo 145 - AEAT", "lugar": "En:", "dia": "a día:", "mes": "de:", "año": "de:", "btn": "Generar PDF"},
    "English": {"tit": "Form 145", "lugar": "In:", "dia": "day:", "mes": "month:", "año": "year:", "btn": "Generate PDF"},
    "Русский": {"tit": "Модель 145", "lugar": "В:", "dia": "день:", "mes": "месяц:", "año": "год:", "btn": "Скачать"},
    "Polski": {"tit": "Model 145", "lugar": "W:", "dia": "dzień:", "mes": "miesiąc:", "año": "rok:", "btn": "Pobierz"},
    "Română": {"tit": "Model 145", "lugar": "În:", "dia": "ziua:", "mes": "luna:", "año": "anul:", "btn": "Descarcă"},
    "Українська": {"tit": "Модель 145", "lugar": "В:", "dia": "день:", "mes": "місяць:", "año": "рік:", "btn": "Завантажити"}
}
sel_lang = st.sidebar.selectbox("Idioma", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- TODOS LOS CAMPOS QUE YA TENÍAS (Recopilación) ---
st.subheader("1. Datos Personales")
col1, col2 = st.columns(2)
with col1:
    nif = st.text_input("NIF", key="nif")
    nombre = st.text_input("Apellidos y Nombre", key="nombre")
with col2:
    anio = st.number_input("Año de nacimiento", 1930, 2024, 1980)
    sit_fam = st.radio("Situación Familiar", ["1", "2", "3"], horizontal=True)

st.subheader("2. Hijos / 4. Pensiones / 5. Vivienda")
c3, c4, c5 = st.columns(3)
with c3:
    num_hijos = st.number_input("Nº Hijos", 0, 10)
with c4:
    p_comp = st.number_input("Pensión Comp.", 0.0)
with c5:
    vivienda = st.checkbox("Deducción Vivienda")

# --- LUGAR, FECHA Y FIRMA ---
st.subheader("6. Lugar, Fecha y Firma")
c_lug, c_fec = st.columns(2)
with c_lug:
    lugar = st.text_input(t["lugar"], value="Madrid")
with c_fec:
    fecha = st.date_input("Fecha de firma", datetime.date.today())

canvas_result = st_canvas(stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0", height=150, width=400, key="canvas")

# --- PROCESO DE GENERACIÓN CORREGIDO ---
if st.button(t["btn"]):
    if nif and nombre:
        try:
            reader = PdfReader("MODELO_145.pdf")
            writer = PdfWriter()
            
            # Copiar la página
            writer.add_page(reader.pages[0])
            
            # MAPEO DE CAMPOS (Preservamos lo que ya funcionaba)
            # Nota: Si el error de AcroForm persiste, pypdf v3+ usa una forma distinta:
            fields = {
                "NIF": nif,
                "APELLIDOS": nombre,
                "ANIO_NAC": str(anio),
                "P_COMP": str(p_comp) if p_comp > 0 else "",
                "HIJOS": str(num_hijos) if num_hijos > 0 else ""
            }
            # Cruces
            if sit_fam == "1": fields["SIT1"] = "X"
            elif sit_fam == "2": fields["SIT2"] = "X"
            else: fields["SIT3"] = "X"
            if vivienda: fields["VIV"] = "X"

            # Rellenar campos (esto ya no debería dar error con el nuevo writer)
            writer.update_page_form_field_values(writer.pages[0], fields)

            # ESTAMPAR LUGAR, FECHA Y FIRMA (Capa visual)
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 10)
            
            # Coordenadas para el bloque "En... a... de... de..."
            # Ajustadas según el snippet del PDF: dia, mes, año
            can.drawString(250, 267, lugar)
            can.drawString(340, 267, str(fecha.day))
            can.drawString(380, 267, str(fecha.month))
            can.drawString(450, 267, str(fecha.year))

            # Firma
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                can.drawInlineImage(img, 385, 140, width=105, height=45)
            
            can.save()
            packet.seek(0)
            writer.pages[0].merge_page(PdfReader(packet).pages[0])

            # Descarga final
            out = io.BytesIO()
            writer.write(out)
            st.success("PDF generado.")
            st.download_button("📥 Descargar", out.getvalue(), "modelo145_firmado.pdf", "application/pdf")

        except Exception as e:
            st.error(f"Error: {e}")
