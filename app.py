import base64
import glob
import os
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Consulta de Padrón Electoral - Seccional 43",
    page_icon="🔴",
    layout="centered",
)


# Función para convertir la imagen local a base64 para el fondo
def obtener_imagen_base64():
  for archivo in ["portada.jpg", "portada.png", "portada.JPG", "portada.PNG"]:
    if os.path.exists(archivo):
      with open(archivo, "rb") as f:
        data = f.read()
      ext = archivo.split(".")[-1].lower()
      mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
      return f"data:{mime};base64,{base64.b64encode(data).decode()}"
  return None


img_base64 = obtener_imagen_base64()

# Estilos CSS
css_fondo = (
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    .stApp {{
        background-image: url("{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.35);
        pointer-events: none;
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 3rem;
        max-width: 500px;
    }}
    
    .floating-card {{
        background: rgba(255, 255, 255, 0.90);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 25px 20px;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3);
        margin-top: 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }}
    
    div.stButton > button:first-child {{
        background-color: #e53935 !important;
        color: white !important;
        font-weight: bold;
        font-size: 1.05rem;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1rem;
        width: 100%;
        box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.4);
        transition: all 0.2s ease;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #c62828 !important;
    }}

    .result-box {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        border-left: 6px solid #e53935;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
        margin-top: 20px;
        color: #212529;
    }}
    </style>
    """
    if img_base64
    else """
    <style>
    .stApp { background-color: #f0f2f6; }
    </style>
    """
)

st.markdown(css_fondo, unsafe_allow_html=True)

# --- CARGA INTELIGENTE DE DATOS ---
@st.cache_data
def cargar_datos():
  archivos_excel = glob.glob("*.xlsx") + glob.glob("*.XLSX")
  lista_df = []

  for archivo in archivos_excel:
    try:
      df_temp = pd.read_excel(archivo)
      # Limpiar nombres de columnas (quitar espacios)
      df_temp.columns = df_temp.columns.astype(str).str.strip()
      lista_df.append(df_temp)
    except Exception:
      pass

  if lista_df:
    df_consolidado = pd.concat(lista_df, ignore_index=True)

    # Buscar automáticamente qué columna corresponde a la cédula
    columnas_lower = {col.lower(): col for col in df_consolidado.columns}
    columna_cedula_real = None

    for posible in [
        "cedula",
        "nro_cedula",
        "nro cedula",
        "ci",
        "documento",
        "nro_documento",
    ]:
      if posible in columnas_lower:
        columna_cedula_real = columnas_lower[posible]
        break

    # Si no encuentra coincidencia exacta, busca alguna columna que contenga la palabra 'cedula' o 'ci'
    if not columna_cedula_real:
      for col in df_consolidado.columns:
        if "ced" in col.lower() or col.lower() == "ci":
          columna_cedula_real = col
          break

    if columna_cedula_real:
      # Renombrar estandarizadamente a 'cedula'
      if columna_cedula_real != "cedula":
        df_consolidado = df_consolidado.rename(
            columns={columna_cedula_real: "cedula"}
        )

      df_consolidado["cedula_limpia"] = (
          df_consolidado["cedula"].astype(str).str.replace(".", "").str.strip()
      )
      return df_consolidado

  return pd.DataFrame()


try:
  df = cargar_datos()

  if not df.empty:
    st.markdown(
        """
        <div class="floating-card">
        <h3 style="color: #111; text-align: center; margin-top: 0; margin-bottom: 15px; font-size: 1.2rem; font-weight: 800;">Número de cédula</h3>
        """,
        unsafe_allow_html=True,
    )

    cedula_input = st.text_input(
        "Número de cédula",
        placeholder="Ej: 1234567",
        label_visibility="collapsed",
    )

    buscar_clic = st.button("Consultar")

    st.markdown("</div>", unsafe_allow_html=True)

    if buscar_clic:
      if cedula_input:
        clean_input = (
            cedula_input.replace(".", "").replace("-", "").strip()
        )
        resultado = df[df["cedula_limpia"] == clean_input]

        if not resultado.empty:
          persona = resultado.iloc[0]

          # Intentar mostrar campos de forma flexible por si cambian de nombre
          nombre = persona.get(
              "nombre", persona.get("NOMBRE", persona.get("Nombres", ""))
          )
          apellido = persona.get(
              "apellido", persona.get("APELLIDO", persona.get("Apellidos", ""))
          )
          local = persona.get(
              "local", persona.get("LOCAL", persona.get("Lugar", "No especificado"))
          )
          secc = persona.get("secc", persona.get("SECC", "43"))

          st.markdown(
              f"""
                <div class="result-box">
                    <h4 style="color: #e53935; margin-top: 0; margin-bottom: 10px;">¡Votante Encontrado!</h4>
                    <p style="margin: 4px 0;"><b>Nombre:</b> {nombre} {apellido}</p>
                    <p style="margin: 4px 0;"><b>Cédula:</b> {int(persona['cedula']):,}".replace(',', '.')}</p>
                    <p style="margin: 4px 0;"><b>Local de Votación:</b> {local}</p>
                    <p style="margin: 4px 0;"><b>Seccional N°:</b> {secc}</p>
                </div>
                """,
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              """
                <div class="result-box" style="border-left-color: #f57c00;">
                    <p style="margin:0; color: #d84315; font-weight: bold;">No se encontró esa cédula en la lista de la Seccional 43.</p>
                </div>
                """,
              unsafe_allow_html=True,
          )
      else:
        st.warning("Por favor, ingresa un número de cédula.")
  else:
    st.error(
        "⚠️ No se detectó ningún archivo Excel (.xlsx) con la columna de"
        " cédula en el repositorio. Asegúrate de haber subido tu archivo de"
        " padrón."
    )

except Exception as e:
  st.error(f"Error al procesar la información: {e}")
