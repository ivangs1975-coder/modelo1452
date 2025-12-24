import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import datetime

# --- 1. DICCIONARIO DE IDIOMAS (Interfaz completa) ---
languages = {
    "Español": {
        "tit": "Modelo 145 - Comunicación de Datos",
        "s1": "1. Datos del perceptor", "s2": "2. Hijos y descendientes", 
        "s3": "3. Ascendientes", "s4": "4. Pensiones", "s5": "5. Vivienda",
        "s6": "6. Lugar, Fecha y Firma",
        "sit1": "Situación 1: Soltero/Divorciado con hijos en exclusiva",
        "sit2": "Situación 2: Casado (cónyuge con rentas < 1.500€)",
        "sit3": "Situación 3: Otras situaciones",
        "lugar": "Ciudad/Lugar", "fecha": "Fecha", "btn": "Generar y Descargar PDF"
    },
    "English": {"tit": "Form 145", "s1": "1. Personal Data", "s2": "2. Children", "s3": "3. Ascendants", "s4": "4. Pensions", "s5": "5. Mortgage", "s6": "6. Signature", "sit1": "Situation 1", "sit2": "Situation 2", "sit3": "Situation 3", "lugar": "City", "fecha": "Date", "btn": "Download PDF"},
    "Русский": {"tit": "Модель 145", "s1": "Данные", "s2": "Дети", "s3": "Предки", "s4": "Пенсии", "s5": "Жилье", "s6": "Подпись", "sit1": "Ситуация 1", "sit2": "Ситуация 2", "sit3": "Ситуация 3", "lugar": "Город", "fecha": "Дата", "btn": "Скачать PDF"},
    "Polski": {"tit": "Model 145", "s1": "Dane", "s2": "Dzieci", "s3": "Wstępni", "s4": "Emerytury", "s5": "Mieszkanie", "s6": "Podpis", "sit1": "Sytuacja 1", "sit2": "Sytuacja 2", "sit3": "Sytuacja 3", "lugar": "Miasto", "fecha": "Data", "btn": "Pobierz PDF"},
    "Română": {"tit": "Model 145", "s1": "Date", "s2": "Copii", "s3": "Ascendenți", "s4": "Pensii", "s5": "Locuință", "s6": "Semnătura", "sit1": "Situația 1", "sit2": "Situația 2", "sit3": "Situația 3", "lugar": "Oraș", "fecha": "Data", "btn": "Descarcă PDF"},
    "Українська": {"tit": "Модель 145", "s1": "Дані", "s2": "Діти", "s3": "Предки", "s4": "Пенсії", "s5": "Житло", "s6": "Підпис", "sit1": "Ситуація 1", "sit2": "Ситуація 2", "sit3": "Ситуація 3", "lugar": "Місто", "fecha": "Дата", "btn": "Завантажити PDF"}
}

sel_lang = st.sidebar.selectbox("Idioma / Language", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- 2. RECOPILACIÓN DE DATOS (Preservando estructura de mapeo) ---
st.header(t["s1"])
c1, c2 = st.columns(2)
with c1:
    nif = st.text_input("NIF")
    nombre = st.text_input("Apellidos y Nombre")
with c2:
    anio = st.number_input("Año de nacimiento", 1930, 2024, 1985)
    discapacidad = st.selectbox("Minusvalía", ["No", ">=33% y <65%", ">=65%", "Movilidad reducida"])

# Lógica dependiente: Situación Familiar
sit_fam = st.radio(t["sit1"][:10], [t["sit1"], t["sit2"], t["sit3"]])
nif_conyuge = ""
if sit_fam == t["sit2"]:
    nif_conyuge = st.text_input("NIF del cónyuge")

# Sección 2: Hijos
st.header(t["s2"])
tiene_hijos = st.checkbox("Tengo hijos/descendientes")
num_hijos = st.number_input("Nº Hijos", 0, 10) if tiene_hijos else 0

# Sección 4: Pensiones
st.header(t["s4"])
p_comp = st.number_input("Pensión compensatoria cónyuge", 0.0)
a_alim = st.number_input("Anualidad alimentos hijos", 0.0)

# Sección 5: Vivienda
st.header(t["s5"])
vivienda = st.checkbox("Deducción préstamo vivienda habitual (pre-2013)")

# --- 3. FIRMA, LUGAR Y FECHA ---
st.header(t["s6"])
col_l, col_f = st.columns(2)
with col_l:
    lugar = st.text_input(t["lugar"], value="Madrid")
with col_f:
    fecha = st.date_input(t["fecha"], datetime.date.today())

st.write("Firme en el recuadro:")
canvas_result = st_canvas(
    stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0",
    height=120, width=400, key="f_final"
)

# --- 4. PROCESAMIENTO SIN PÉRDIDA DE DATOS ---
if st.button(t["btn"]):
    if nif and nombre:
        try:
            reader = PdfReader("MODELO_145.pdf")
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            writer.add_form_top_level_objects() # Evita error AcroForm

            # Mapeo de campos (ajustar nombres según tu PDF)
            campos = {
                "NIF": nif, "APELLIDOS": nombre, "ANIO_NAC": str(anio),
                "NIF_CONY": nif_conyuge, "HIJOS": str(num_hijos) if num_hijos > 0 else "",
                "P_COMP": str(p_comp) if p_comp > 0 else "",
                "A_ALIM": str(a_alim) if a_alim > 0 else ""
            }
            # Cruces de situaciones
            if sit_fam == t["sit1"]: campos["SIT_1"] = "X"
            elif sit_fam == t["sit2"]: campos["SIT_2"] = "X"
            else: campos["SIT_3"] = "X"
            if vivienda: campos["VIV_X"] = "X"

            writer.update_page_form_field_values(writer.pages[0], campos)

            # Capa de ReportLab para Lugar, Fecha y Firma
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 10)

            # Coordenadas ajustadas para: En [lugar] a [día] de [mes] de [año]
            can.drawString(245, 267, lugar)
            can.drawString(335, 267, str(fecha.day))
            can.drawString(370, 267, str(fecha.month)) # Puedes usar fecha.strftime("%B")
            can.drawString(440, 267, str(fecha.year))

            # Firma del Canvas
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                can.drawInlineImage(img, 380, 140, width=100, height=40)

            can.save()
            packet.seek(0)
            writer.pages[0].merge_page(PdfReader(packet).pages[0])

            out = io.BytesIO()
            writer.write(out)
            st.success("PDF generado con éxito.")
            st.download_button("📥 Descargar", out.getvalue(), "modelo145_final.pdf", "application/pdf")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Completa NIF y Nombre.")
