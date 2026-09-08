import glob
import os
import pandas as pd
import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Consulta de Padrón Electoral",
    page_icon="🗳️",
    layout="centered",
)

# 2. ESTILOS CSS PERSONALIZADOS (UI/UX)
st.markdown(
    """
    <style>
    /* Fondo general claro */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Contenedor principal para mantener todo centrado y limpio */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 650px;
    }
    
    /* Encabezados institucionales */
    h1, h2, h3, h4 {
        color: #d32f2f !important;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    /* Diseño del botón principal de búsqueda */
    div.stButton > button:first-child {
        background-color: #d32f2f !important;
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #b71c1c !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    }
    
    /* Tarjeta de resultados flotante */
    .result-card {
        background-color: #ffffff;
        border-left: 6px solid #d32f2f;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        margin-top: 20px;
    }
    
    .result-card p {
        font-size: 1.05rem;
        margin-bottom: 8px;
        color: #333;
    }
    
    .result-card b {
        color: #212529;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. MOSTRAR PORTADA
if os.path.exists("portada.jpg"):
    st.image("portada.jpg", use_container_width=True)
elif os.path.exists("portada.png"):
    st.image("portada.png", use_container_width=True)

# 4. ENCABEZADO
st.markdown("<h2>CONSULTA DE LUGAR DE VOTACIÓN</h2>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-weight: bold; color: #555;'>Consulta tu local, mesa y orden</p>",
    unsafe_allow_html=True,
)

# 5. CARGA Y PROCESAMIENTO DE DATOS
@st.cache_data
def cargar_datos():
    archivos_excel = glob.glob("*.xlsx")
    
    if not archivos_excel:
        return pd.DataFrame()

    lista_df = []
    for archivo in archivos_excel:
        try:
            df_temp = pd.read_excel(archivo)
            # Estandarizar nombres de columnas a minúsculas y sin espacios
            df_temp.columns = df_temp.columns.astype(str).str.strip().str.lower()
            lista_df.append(df_temp)
        except Exception:
            pass

    if lista_df:
        df_consolidado = pd.concat(lista_df, ignore_index=True)
        
        # Validar que exista la columna cédula antes de limpiar
        if "cedula" in df_consolidado.columns:
            # Limpiar puntos, guiones y espacios
            df_consolidado["cedula_limpia"] = (
                df_consolidado["cedula"]
                .astype(str)
                .str.replace(r"[\.\-\s]", "", regex=True)
            )
        return df_consolidado
    
    return pd.DataFrame()

# 6. LÓGICA PRINCIPAL Y BUSCADOR
try:
    df = cargar_datos()

    if not df.empty and "cedula_limpia" in df.columns:
        
        # Formulario de entrada
        cedula_input = st.text_input(
            "Ingresá tu número de Cédula de Identidad:",
            placeholder="Ej: 4187526",
        )

        if st.button("🔍 CONSULTAR DATOS"):
            if cedula_input:
                # Limpiar el input del usuario de igual manera
                clean_input = cedula_input.replace(".", "").replace("-", "").strip()
                
                # Filtrar el DataFrame
                resultado = df[df["cedula_limpia"] == clean_input]

                if not resultado.empty:
                    persona = resultado.iloc[0]
                    
                    # Manejo de datos nulos o faltantes y formato de separador de miles
                    nombre = persona.get('nombre', '')
                    apellido = persona.get('apellido', '')
                    local = persona.get('local', 'No asignado')
                    mesa = persona.get('mesa', 'No asignada')
                    orden = persona.get('orden', 'No asignado')
                    secc = persona.get('secc', 'No asignada')
                    
                    try:
                        cedula_formateada = f"{int(float(persona['cedula'])):,}".replace(",", ".")
                    except:
                        cedula_formateada = persona.get('cedula', clean_input)

                    # Inyectar resultados en la tarjeta HTML
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <h4 style="color: #d32f2f; margin-top: 0; text-align: left;">¡Votante Habilitado!</h4>
                            <p><b>Nombre Completo:</b> {nombre} {apellido}</p>
                            <p><b>Cédula:</b> {cedula_formateada}</p>
                            <hr style="margin: 10px 0; border-top: 1px solid #eee;">
                            <p><b>Local de Votación:</b> {local}</p>
                            <p><b>Mesa:</b> {mesa}</p>
                            <p><b>Orden:</b> {orden}</p>
                            <p><b>Seccional N°:</b> {secc}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("No se encontró el número de cédula ingresado en el padrón.")
            else:
                st.warning("Por favor, ingresa un número de cédula válido antes de consultar.")
    else:
        st.error("El sistema no detectó archivos .xlsx válidos en el directorio o no tienen la columna 'cedula'.")

except Exception as e:
    st.error(f"Error interno al procesar la base de datos: {e}")
