import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

# --- 1. DICCIONARIO MULTILENGUAJE ---
languages = {
    "Español": {"tit": "Modelo 145", "btn": "Generar PDF", "f_label": "Firma del perceptor:", "c_nif": "NIF del cónyuge"},
    "English": {"tit": "Form 145", "btn": "Generate PDF", "f_label": "Recipient's signature:", "c_nif": "Spouse's NIF"},
    "Русский": {"tit": "Модель 145", "btn": "Создать PDF", "f_label": "Подпись получателя:", "c_nif": "ИНН супруга"},
    "Polski": {"tit": "Model 145", "btn": "Generuj PDF", "f_label": "Podpis odbiorcy:", "c_nif": "NIP małżonka"},
    "Română": {"tit": "Model 145", "btn": "Generați PDF", "f_label": "Semnătura destinatarului:", "c_nif": "NIF soț/soție"},
    "Українська": {"tit": "Модель 145", "btn": "Згенерувати PDF", "f_label": "Підпис одержувача:", "c_nif": "ІПН чоловіка/дружини"}
}

sel_lang = st.sidebar.selectbox("Idioma / Language", list(languages.keys()))
t = languages[sel_lang]

st.title(t["tit"])

# --- 2. CAMPOS DEL PERCEPTOR ---
st.subheader("1. Datos personales")
col1, col2 = st.columns(2)
with col1:
    nif = st.text_input("NIF")
    apellidos_nombre = st.text_input("Apellidos y Nombre")
with col2:
    anio_nac = st.number_input("Año de nacimiento", 1930, 2024, 1985)
    sit_fam = st.radio("Situación familiar", ["1", "2", "3"], horizontal=True)

# Campo dependiente: NIF Cónyuge (Solo si es situación 2)
nif_conyuge = ""
if sit_fam == "2":
    nif_conyuge = st.text_input(t["c_nif"])

# --- 3. HIJOS Y PENSIONES (Lo que ya tenías) ---
st.subheader("2. Hijos y 4. Pensiones")
num_hijos = st.number_input("Nº de hijos", 0, 10)
p_comp = st.number_input("Pensión compensatoria", 0.0)
a_alim = st.number_input("Anualidad alimentos", 0.0)

# --- 4. FIRMA (LO QUE NO FUNCIONABA) ---
st.markdown("---")
st.subheader(t["f_label"])
canvas_result = st_canvas(
    stroke_width=2, stroke_color="#0000ff", background_color="#f0f0f0",
    height=120, width=350, drawing_mode="freedraw", key="firma_final"
)

# --- 5. GENERACIÓN DEL PDF ---
if st.button(t["btn"]):
    try:
        reader = PdfReader("MODELO_145.pdf")
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        
        # Mapeo de datos (Ajusta los nombres si tu PDF usa otros IDs)
        datos = {
            "NIF": nif,
            "APELLIDOS_NOMBRE": apellidos_nombre,
            "ANIO_NAC": str(anio_nac),
            "SIT_FAM": sit_fam,
            "NIF_CONY": nif_conyuge,
            "P_COMP": str(p_comp) if p_comp > 0 else "",
            "A_ALIM": str(a_alim) if a_alim > 0 else ""
        }
        
        writer.update_page_form_field_values(writer.pages[0], datos)

        # Proceso de Estampado de la Firma (Imagen sobre PDF)
        if canvas_result.image_data is not None:
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            
            # Estas coordenadas (375, 155) sitúan la firma en el hueco del Modelo 145
            can.drawInlineImage(img, 375, 155, width=100, height=40)
            can.save()
            packet.seek(0)
            writer.pages[0].merge_page(PdfReader(packet).pages[0])

        # Descarga final
        output = io.BytesIO()
        writer.write(output)
        st.success("PDF procesado.")
        st.download_button("📥 Descargar Modelo 145 Firmado", output.getvalue(), "modelo_145_final.pdf", "application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")
