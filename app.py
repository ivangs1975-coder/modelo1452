import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
from datetime import datetime
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Modelo 145", layout="centered")
st.title("📄 Modelo 145 – Comunicación de datos")

# ---------------- FORMULARIO ----------------
with st.form("modelo145"):
    st.subheader("1. Datos personales")

    nif = st.text_input("NIF / NIE *")
    nombre = st.text_input("Apellidos y Nombre *")
    anio = st.text_input("Año de nacimiento")

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

    st.subheader("4. Pensiones")
    pension = st.number_input("Pensión compensatoria anual (€)", 0.0)
    alimentos = st.number_input("Anualidades por alimentos (€)", 0.0)

    st.subheader("6. Firma (dibuje con el dedo)")
    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="black",
        background_color="white",
        height=150,
        key="firma"
    )

    generar = st.form_submit_button("GENERAR PDF")

# ---------------- LÓGICA PDF ----------------
if generar:
    if not nif or not nombre:
        st.error("El NIF y el Nombre son obligatorios.")
    else:
        # ---- 1. Cargar PDF base ----
        reader = PdfReader("modelo145.pdf")
        writer = PdfWriter()
        writer.append(reader)
        page = writer.pages[0]

        # ---- 2. Rellenar campos del PDF ----
        writer.update_page_form_field_values(page, {
            "NIF": nif.upper(),
            "Apellidos y Nombre": nombre.upper(),
            "Año de nacimiento": anio
        })

        if situacion.startswith("1"):
            writer.update_page_form_field_values(page, {"01": "/Yes"})
        elif situacion.startswith("2"):
            writer.update_page_form_field_values(page, {
                "02": "/Yes",
                "NIF del cónyuge": nif_conyuge.upper()
            })
        elif situacion.startswith("3"):
            writer.update_page_form_field_values(page, {"03": "/Yes"})

        if pension > 0:
            writer.update_page_form_field_values(page, {
                "Pensión compensatoria en favor del cónyuge Importe anual que está Vd obligado a satisfacer por resolución judicial":
                f"{pension:.2f}"
            })

        if alimentos > 0:
            writer.update_page_form_field_values(page, {
                "Anualidades por alimentos en favor de los hijos Importe anual que está Vd obligado a satisfacer por resolución judicial":
                f"{alimentos:.2f}"
            })

        hoy = datetime.now()
        writer.update_page_form_field_values(page, {
            "día": str(hoy.day).zfill(2),
            "de": str(hoy.month).zfill(2),
            "de_2": str(hoy.year)
        })

        # ---- 3. Crear overlay SOLO para la firma ----
        if canvas_result.image_data is not None:
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=A4)

            img = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
            # 🔧 COORDENADAS DE LA FIRMA (AJUSTADAS AL MODELO 145)
            c.drawInlineImage(img, x=72, y=115, width=120, height=45)

            c.save()
            packet.seek(0)

            firma_pdf = PdfReader(packet)
            page.merge_page(firma_pdf.pages[0])

        # ---- 4. Guardar PDF final ----
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        st.success("✅ Modelo 145 generado correctamente con firma")
        st.download_button(
            "⬇️ Descargar PDF",
            data=output.getvalue(),
            file_name=f"MOD145_{nif.upper()}.pdf",
            mime="application/pdf"
        )
