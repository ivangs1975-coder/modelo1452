import streamlit as st

# 1. CONFIGURACIÓN DE IDIOMAS
languages = {
    "Español": {
        "titulo": "Modelo 145 - Retenciones sobre rendimientos del trabajo",
        "pensiones": "4. Pensiones compensatorias y anualidades por alimentos",
        "firma": "6. Fecha y firma de la comunicación",
        "hijos": "2. Hijos y otros descendientes",
        "datos_pers": "1. Datos personales y situación familiar",
        "ayuda_chk": "Marque las casillas según corresponda:"
    },
    "English": {
        "titulo": "Form 145 - Withholding on earned income",
        "pensiones": "4. Compensatory pensions and alimony annuities",
        "firma": "6. Date and signature of the communication",
        "hijos": "2. Children and other descendants",
        "datos_pers": "1. Personal data and family status",
        "ayuda_chk": "Check the boxes as appropriate:"
    },
    "Русский": {
        "titulo": "Форма 145 - Удержания из трудовых доходов",
        "pensiones": "4. Компенсационные выплаты и алименты",
        "firma": "6. Дата и подпись",
        "hijos": "2. Дети и другие потомки",
        "datos_pers": "1. Личные данные и семейное положение",
        "ayuda_chk": "Отметьте соответствующие поля:"
    },
    "Polski": {
        "titulo": "Formularz 145 - Zaliczki na podatek od dochodów z pracy",
        "pensiones": "4. Renty wyrównawcze i alimenty",
        "firma": "6. Data i podpis",
        "hijos": "2. Dzieci i inni zstępni",
        "datos_pers": "1. Dane osobowe i sytuacja rodzinna",
        "ayuda_chk": "Zaznacz odpowiednie pola:"
    },
    "Română": {
        "titulo": "Formularul 145 - Rețineri din veniturile din muncă",
        "pensiones": "4. Pensii compensatorii și anuități pentru alimente",
        "firma": "6. Data și semnătura",
        "hijos": "2. Copii și alți descendenți",
        "datos_pers": "1. Date personale și starea civilă",
        "ayuda_chk": "Bifați căsuțele corespunzătoare:"
    },
    "Українська": {
        "titulo": "Форма 145 - Утримання з доходів від праці",
        "pensiones": "4. Компенсаційні виплати та аліменти",
        "firma": "6. Дата та підпис",
        "hijos": "2. Діти та інші нащадки",
        "datos_pers": "1. Особисті дані та сімейний стан",
        "ayuda_chk": "Поставте галочки у відповідних полях:"
    }
}

# 2. SELECTOR DE IDIOMA (Aparece arriba del todo)
selected_lang = st.sidebar.selectbox("Selecciona tu idioma / Select your language", list(languages.keys()))
t = languages[selected_lang]

# 3. CONTENIDO DE LA APP
st.title(t["titulo"])

# --- SECCIÓN 1: DATOS PERSONALES ---
st.subheader(t["datos_pers"])
nombre = st.text_input("Nombre y Apellidos / Name and Surname")
dni = st.text_input("DNI / NIE")

# --- SECCIÓN 2: CHECKBOXES (Corregidos con 'key' única) ---
st.write(t["ayuda_chk"])
col1, col2 = st.columns(2)
with col1:
    sit_1 = st.checkbox("Situación Familiar 1", key="sit1")
    discapacidad = st.checkbox("Discapacidad >= 33%", key="disc")
with col2:
    sit_2 = st.checkbox("Situación Familiar 2", key="sit2")
    movilidad = st.checkbox("Movilidad reducida", key="mov")

# --- SECCIÓN: HIJOS ---
st.subheader(t["hijos"])
# Aquí irían los inputs para hijos...

# --- SECCIÓN 4: PENSIONES (Aquí estaba tu error de la línea 57) ---
st.subheader(t["pensiones"])
importe_pension = st.number_input("Importe anual / Annual amount", min_value=0.0, step=100.0)

# --- SECCIÓN 6: FIRMA (Bajada con espacio) ---
# Añadimos varios saltos de línea para bajar la firma
st.markdown("<br>" * 8, unsafe_allow_html=True) 

st.divider() # Una línea visual divisoria
st.subheader(t["firma"])
fecha = st.date_input("Fecha / Date")

# Simulación de recuadro de firma
st.markdown("""
    <div style="border: 1px solid #ccc; padding: 50px; text-align: center; border-radius: 10px;">
        Firma del perceptor / Signature
    </div>
""", unsafe_allow_html=True)

# Botón de envío
if st.button("Generar PDF"):
    st.success("Procesando información...")
