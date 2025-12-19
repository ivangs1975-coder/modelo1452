import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

st.set_page_config(page_title="Generador Modelo 145", page_icon="📝")

st.title("📝 Formulario Modelo 145")
st.subheader("Rellena tus datos y descarga el PDF listo")

with st.form("form_145"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre y Apellidos")
        dni = st.text_input("DNI / NIE")
    with col2:
        fecha_nac = st.text_input("Año de nacimiento (ej: 1985)")
    
    situacion = st.radio(
        "Situación Familiar",
        ["1. Soltero/Divorciado con hijos", "2. Casado y cónyuge no gana > 1500€", "3. Otras situaciones (Soltero sin hijos, etc.)"]
    )
    
    discapacidad = st.checkbox("¿Tienes algún grado de discapacidad?")
    
    submitted = st.form_submit_button("Generar PDF")

if submitted:
    try:
        # 1. Leer el PDF original (debe estar en la misma carpeta)
        existing_pdf = PdfReader(open("modelo145.pdf", "rb"))
        output = PdfWriter()
        
        # 2. Crear una "capa" con el texto usando ReportLab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # COORDENADAS (Tendrás que ajustarlas ligeramente según tu PDF)
        # Estas coordenadas son aproximadas para el PDF de la AEAT
        can.setFont("Helvetica", 10)
        can.drawString(100, 655, nombre)  # Nombre
        can.drawString(55, 655, dni)      # DNI
        can.drawString(390, 655, fecha_nac) # Año
        
        # Marcar situación familiar con una 'X'
        if "1." in situacion: can.drawString(55, 615, "X")
        if "2." in situacion: can.drawString(55, 600, "X")
        if "3." in situacion: can.drawString(55, 585, "X")
            
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        
        # 3. Fusionar la capa de texto con la primera página del PDF original
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        # Añadir el resto de páginas sin cambios
        for i in range(1, len(existing_pdf.pages)):
            output.add_page(existing_pdf.pages[i])

        # 4. Preparar descarga
        buf = io.BytesIO()
        output.write(buf)
        byte_im = buf.getvalue()
        
        st.success("¡PDF generado con éxito!")
        st.download_button(
            label="📩 Descargar Modelo 145 Relleno",
            data=byte_im,
            file_name=f"Modelo145_{dni}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"Error: Asegúrate de que el archivo 'modelo145.pdf' está en el repositorio. {e}")