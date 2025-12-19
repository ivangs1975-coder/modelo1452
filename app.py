import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
import io
from PIL import Image
from datetime import datetime

# 1. Configuración de Estilo y Visibilidad
st.set_page_config(page_title="Modelo 145 - Registro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    label, p, h1, h2, h3, span { color: black !important; font-weight: 500; }
    .stTabs [data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #1e3a8a !important; font-weight: bold; }
    .stButton>button { background-color: #1e3a8a !important; color: white !important; width: 100%; height: 3em; }
    .stDownloadButton>button { background-color: #059669 !important; color: white !important; width: 100%; height: 3.5em; font-weight: bold; font-size: 1.2rem; border: none; }
    /* Estilo para los radio buttons y texto */
    .stRadio [data-testid="stWidgetLabel"] p { font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

try:
    st.image("logo.png", width=250)
except:
    st.title("🏢 GESTIÓN DE PERSONAL")

# 2. Formulario con texto descriptivo
with st.form("form_final_calibrado"):
    tab1, tab2, tab3 = st.tabs(["📋 1. Datos Personales", "👪 2 y 3. Familia", "🖋️ 4 a 6. Otros y Firma"])
    
    with tab1:
        c1, c2 = st.columns(2)
        nif = c1.text_input("NIF / NIE", placeholder="12345678X")
        nombre = c2.text_input("Apellidos y Nombre")
        año_nac = st.text_input("Año de nacimiento (Ej: 1985)")
        
        st.write("**Situación Familiar:**")
        sit_opciones = {
            "1. Soltero/a, viudo/a, divorciado/a con hijos (exclusivamente)": "1",
            "2. Casado/a y cuyo cónyuge no obtiene rentas superiores a 1.500 €": "2",
            "3. Otras situaciones (Soltero sin hijos, casado con cónyuge con ingresos, etc.)": "3"
        }
        sit_seleccion = st.radio("Seleccione su caso:", list(sit_opciones.keys()))
        sit_val = sit_opciones[sit_seleccion]
        
        nif_conyuge = ""
        if sit_val == "2":
            nif_conyuge = st.text_input("NIF del Cónyuge")
            
        discap_perceptor = st.selectbox("Grado de discapacidad del trabajador:", ["Ninguna", "Igual o superior al 33% e inferior al 65%", "Igual o superior al 65%", "Con ayuda de terceros o movilidad reducida"])
        movilidad = st.checkbox("Movilidad geográfica (Aceptación de nuevo puesto que exige traslado)")

    with tab2:
        st.subheader("Hijos y otros descendientes (<25 años)")
        col_h1, col_h2 = st.columns(2)
        num_hijos = col_h1.number_input("Nº total de hijos", 0, 10, 0)
        hijos_entero = col_h2.checkbox("Cómputo por entero (Solo usted convive con ellos)")
        hijos_disc_33 = col_h1.number_input("Hijos con discapacidad >33%", 0, 10, 0)
        hijos_disc_65 = col_h2.number_input("Hijos con discapacidad >65%", 0, 10, 0)
        
        st.write("---")
        st.subheader("Ascendientes (>65 años a su cargo)")
        col_a1, col_a2 = st.columns(2)
        num_asc = col_a1.number_input("Nº total de ascendientes", 0, 10, 0)
        asc_disc_33 = col_a2.number_input("Ascendientes con discapacidad >33%", 0, 10, 0)
        asc_disc_65 = col_a1.number_input("Ascendientes con discapacidad >65%", 0, 10, 0)

    with tab3:
        pension = st.number_input("Pensión compensatoria a favor del cónyuge (€/año)", 0.0)
        alimentos = st.number_input("Anualidad por alimentos a favor de los hijos (€/año)", 0.0)
        vivienda = st.checkbox("Deducción por pago de hipoteca (vivienda comprada antes de 2013)")
        
        st.write("---")
        st.write("### Firma en el recuadro")
        canvas_result = st_canvas(stroke_width=2, stroke_color="black", background_color="#f8f9fa", height=150, key="signature_v4")

    submit = st.form_submit_button("GENERAR DOCUMENTO FINAL")

# 3. Lógica de Estampado (Ajuste milimétrico)
if submit:
    if not nif or not nombre:
        st.error("⚠️ El NIF y el Nombre son obligatorios.")
    else:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont("Helvetica", 9)

        # BLOQUE 1: Datos Personales (Y=672 es la línea de arriba)
        can.drawString(58, 672, nif.upper())
        can.drawString(160, 672, nombre.upper())
        can.drawString(412, 672, año_nac)
        
        # Situaciones familiares (X)
        if sit_val == "1": can.drawString(64, 638, "X")
        if sit_val == "2": 
            can.drawString(64, 622, "X")
            can.drawString(205, 622, nif_conyuge.upper())
        if sit_val == "3": can.drawString(64, 606, "X")
        
        # Discapacidad perceptor
        if "33%" in discap_perceptor: can.drawString(428, 606, "X")
        if "65%" in discap_perceptor: can.drawString(502, 606, "X")
        if "movilidad" in discap_perceptor.lower(): can.drawString(428, 592, "X")
        if movilidad: can.drawString(428, 578, "X")

        # BLOQUE 2: Hijos
        if num_hijos > 0:
            can.drawString(300, 510, str(num_hijos))
            if hijos_entero: can.drawString(355, 510, "X")
            if hijos_disc_33 > 0: can.drawString(428, 510, str(hijos_disc_33))
            if hijos_disc_65 > 0: can.drawString(502, 510, str(hijos_disc_65))

        # BLOQUE 3: Ascendientes
        if num_asc > 0:
            can.drawString(300, 422, str(num_asc))
            if asc_disc_33 > 0: can.drawString(428, 422, str(asc_disc_33))
            if asc_disc_65 > 0: can.drawString(502, 422, str(asc_disc_65))

        # BLOQUE 4 y 5: Pensiones y Vivienda
        if pension > 0: can.drawString(400, 348, f"{pension:.2f}")
        if alimentos > 0: can.drawString(400, 335, f"{alimentos:.2f}")
        if vivienda: can.drawString(64, 305, "X")

        # BLOQUE 6: FECHA DE HOY AUTOMÁTICA
        hoy = datetime.now()
        can.drawString(223, 195, str(hoy.day).zfill(2))
        can.drawString(254, 195, str(hoy.month).zfill(2))
        can.drawString(292, 195, str(hoy.year))

        # FIRMA
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            can.drawInlineImage(img, 72, 115, width=115, height=48)

        can.save()
        packet.seek(0)

        # Fusión final
        original = PdfReader(open("modelo145.pdf", "rb"))
        overlay = PdfReader(packet)
        writer = PdfWriter()
        
        page = original.pages[0]
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
        
        for i in range(1, len(original.pages)):
            writer.add_page(original.pages[i])

        final_buf = io.BytesIO()
        writer.write(final_buf)
        
        st.success(f"✅ Documento generado correctamente hoy {hoy.strftime('%d/%m/%Y')}")
        st.download_button(
            label=f"⬇️ DESCARGAR MOD145_{nif.upper()}.pdf",
            data=final_buf.getvalue(),
            file_name=f"MOD145_{nif.upper()}.pdf",
            mime="application/pdf"
        )
