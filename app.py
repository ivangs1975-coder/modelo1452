import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

# --- CONFIGURACIÓN DE IDIOMAS ---
languages = {
    "Español": {
        "t1": "1. Datos del perceptor", "t2": "2. Hijos y descendientes", "t3": "3. Ascendientes", 
        "t4": "4. Pensiones", "t5": "5. Vivienda habitual", "t6": "6. Firma",
        "sit_fam": "Situación Familiar",
        "sit1": "1. Soltero/Divorciado con hijos (en exclusiva)",
        "sit2": "2. Casado (cónyuge con rentas < 1.500€)",
        "sit3": "3. Otras situaciones (solteros sin hijos, casados cónyuge trabaja...)",
        "conyuge": "NIF del cónyuge", "hijos_dis": "Hijos con discapacidad",
        "btn": "Generar y Descargar PDF"
    },
    "English": {"t1": "1. Personal Data", "t2": "2. Children", "t3": "3. Ascendants", "t4": "4. Pensions", "t5": "5. Mortgage", "t6": "6. Signature", "sit_fam": "Family Situation", "sit1": "Situation 1", "sit2": "Situation 2", "sit3": "Situation 3", "conyuge": "Spouse NIF", "hijos_dis": "Disabled children", "btn": "Download PDF"},
    "Русский": {"t1": "1. Данные", "t2": "2. Дети", "t3": "3. Предки", "t4": "4. Пенсии", "t5": "5. Жилье", "t6": "6. Подпись", "sit_fam": "Семейное положение", "sit1": "Ситуация 1", "sit2": "Ситуация 2", "sit3": "Ситуация 3", "conyuge": "ИНН супруга", "hijos_dis": "Дети-инвалиды", "btn": "Скачать PDF"},
    "Polski": {"t1": "1. Dane", "t2": "2. Dzieci", "t3": "3. Wstępni", "t4": "4. Emerytury", "t5": "5. Kredyt", "t6": "6. Podpis", "sit_fam": "Sytuacja rodzinna", "sit1": "Sytuacja 1", "sit2": "Sytuacja 2", "sit3": "Sytuacja 3", "conyuge": "NIP małżonka", "hijos_dis": "Dzieci niepełnosprawne", "btn": "Pobierz PDF"},
    "Română": {"t1": "1. Date", "t2": "2. Copii", "t3": "3. Ascendenți", "t4": "4. Pensii", "t5": "5. Locuință", "t6": "6. Semnătura", "sit_fam": "Situația familială", "sit1": "Situația 1", "sit2": "Situația 2", "sit3": "Situația 3", "conyuge": "NIF soț/soție", "hijos_dis": "Copii cu dizabilități", "btn": "Descarcă PDF"},
    "Українська": {"t1": "1. Дані", "t2": "2. Діти", "t3": "3. Предки", "t4": "4. Пенсії", "t5": "5. Житло", "t6": "6. Підпис", "sit_fam": "Сімейний стан", "sit1": "Ситуація 1", "sit2": "Ситуація 2", "sit3": "Ситуація 3", "conyuge": "ІПН чоловіка/дружини", "hijos_dis": "Діти з інвалідністю", "btn": "Завантажити PDF"}
}

sel_lang = st.sidebar.selectbox("Idioma / Language", list(languages.keys()))
t = languages[sel_lang]

st.title("Modelo 145 AEAT")

# --- SECCIÓN 1: DATOS PERSONALES ---
st.header(t["t1"])
col1, col2 = st.columns(2)
with col1:
    nif = st.text_input("NIF")
    nombre = st.text_input("Apellidos y Nombre")
with col2:
    anio = st.number_input("Año de nacimiento", 1930, 2024, 1985)
    discapacidad = st.selectbox("Grado discapacidad perceptor", ["Ninguna", ">= 33% y < 65%", ">= 65%", "Movilidad reducida"])

situacion = st.radio(t["sit_fam"], [t["sit1"], t["sit2"], t["sit3"]])
nif_cony = ""
if situacion == t["sit2"]:
    nif_cony = st.text_input(t["conyuge"])

# --- SECCIÓN 2: HIJOS ---
st.header(t["t2"])
tiene_hijos = st.checkbox("¿Tiene hijos o descendientes menores de 25 años?")
num_hijos = 0
hijos_d = 0
if tiene_hijos:
    num_hijos = st.number_input("Número de hijos", 1, 10)
    hijos_d = st.number_input(t["hijos_dis"], 0, num_hijos)

# --- SECCIÓN 3: ASCENDIENTES ---
st.header(t["t3"])
tiene_asc = st.checkbox("¿Tiene ascendientes mayores de 65 años a su cargo?")
num_asc = 0
if tiene_asc:
    num_asc = st.number_input("Número de ascendientes", 1, 5)

# --- SECCIÓN 4: PENSIONES ---
st.header(t["t4"])
p_comp = st.number_input("Pensión compensatoria cónyuge (anual)", 0.0)
a_alim = st.number_input("Anualidad alimentos hijos (anual)", 0.0)

# --- SECCIÓN 5: VIVIENDA ---
st.header(t["t5"])
vivienda = st.checkbox("Pagos por préstamo vivienda habitual (adquirida antes de 2013)")

# --- SECCIÓN 6: FIRMA ---
st.header(t["t6"])
st.write("Firma aquí:")
canvas_result = st_canvas(stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0", height=150, width=400, key="f_final")

# --- GENERACIÓN ---
if st.button(t["btn"]):
    if nif and nombre:
        try:
            reader = PdfReader("MODELO_145.pdf")
            writer = PdfWriter()
            writer.append_pages_from_reader(reader)
            
            # Mapeo completo de campos
            campos = {
                "NIF": nif, "APELLIDOS": nombre, "ANIO_NAC": str(anio),
                "NIF_CONY": nif_cony, "NUM_HIJOS": str(num_hijos) if num_hijos > 0 else "",
                "HIJOS_DIS": str(hijos_d) if hijos_d > 0 else "",
                "P_COMP": str(p_comp) if p_comp > 0 else "",
                "A_ALIM": str(a_alim) if a_alim > 0 else ""
            }
            # Cruces de situación
            if situacion == t["sit1"]: campos["SIT_1"] = "X"
            elif situacion == t["sit2"]: campos["SIT_2"] = "X"
            else: campos["SIT_3"] = "X"
            if vivienda: campos["VIVIENDA"] = "X"

            writer.update_page_form_field_values(writer.pages[0], campos)

            # Estampar Firma
            if canvas_result.image_data is not None:
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                can.drawInlineImage(img, 385, 140, width=110, height=45) # Coordenadas para Firma del Perceptor
                can.save()
                packet.seek(0)
                writer.pages[0].merge_page(PdfReader(packet).pages[0])

            out = io.BytesIO()
            writer.write(out)
            st.download_button("📥 Descargar PDF Rellenado", out.getvalue(), "modelo145_listo.pdf", "application/pdf")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Completa NIF y Nombre.")
