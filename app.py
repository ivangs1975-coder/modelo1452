import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Modelo 145", layout="centered")
st.title("📄 Modelo 145 – Comunicación de datos")

# ---------------- FORMULARIO ----------------
with st.form("modelo145"):
    st.subheader("1. Datos personales")
    nif = st.text_input("NIF / NIE *")
    nombre = st.text_input("Apellidos y Nombre *")
    anio = st.text_input("Año de nacimiento")
    
    st.subheader("Lugar y fecha")
    lugar = st.text_input("En (Ciudad)")
    
    st.subheader("Situación familiar")
    situacion = st.radio(
        "Seleccione una opción:",
        (
            "1. Soltero/a, viudo/a o divorciado/a con hijos",
            "2. Casado/a con cónyuge sin rentas > 1.500 €",
            "3. Otras situaciones"
        )
    )
    nif_conyuge = ""
    if situacion.startswith("2"):
        nif_conyuge = st.text_input("NIF del cónyuge")
    
    st.subheader("Discapacidad / movilidad")
    discap_perceptor = st.selectbox(
        "Grado de discapacidad del trabajador:",
        ["Ninguna", "Igual o superior al 33% e inferior al 65%", "Igual o superior al 65%", "Con ayuda de terceros o movilidad reducida"]
    )
    movilidad = st.checkbox("Movilidad geográfica (aceptación de traslado)")
    if movilidad:
        fecha_traslado = st.text_input("Fecha de traslado (dd/mm/aaaa)")
    
    st.subheader("Hijos y otros descendientes (<25 años)")
    num_hijos = st.number_input("Nº total de hijos", 0, 10, 0)
    hijos_entero = st.checkbox("Cómputo por entero (Solo usted convive con ellos)")
    hijos_disc_33 = st.number_input("Hijos con discapacidad >33%", 0, 10, 0)
    hijos_disc_65 = st.number_input("Hijos con discapacidad >65%", 0, 10, 0)

    st.subheader("Ascendientes (>65 años a su cargo)")
    num_asc = st.number_input("Nº total de ascendientes", 0, 10, 0)
    asc_disc_33 = st.number_input("Ascendientes con discapacidad >33%", 0, 10, 0)
    asc_disc_65 = st.number_input("Ascendientes con discapacidad >65%", 0, 10, 0)

    st.subheader("Pensiones
