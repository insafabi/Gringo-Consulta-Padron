import base64
import glob
import os
import pandas as pd
import streamlit as st

# Configuración de la página optimizada para móvil
st.set_page_config(
    page_title="Consulta de Padrón Electoral - Seccional 43",
    page_icon="🔴",
    layout="centered",
)


# Función para convertir la imagen local a base64
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

# Estilos CSS adaptados para móvil y la imagen con tamaño natural/proporcional
css_movil = (
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Fondo general neutro y limpio para que la tarjeta y la imagen brillen */
    .stApp {{
        background-color: #f4f6f9;
    }}

    /* Contenedor principal ajustado para centrarse perfectamente en móviles */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 480px;
    }}
    
    /* Contenedor de la imagen de portada con tamaño natural/proporcional y bordes redondeados */
    .banner-container {{
        width: 100%;
        text-align: center;
        margin-bottom: 15px;
    }}
    .banner-img {{
        width: 100%;
        max-width: 450px;
        height: auto;
        border-radius: 16px;
        box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.15);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }}

    /* Tarjeta flotante moderna estilo app móvil */
    .floating-card {{
        background: #ffffff;
        padding: 20px 18px;
        border-radius: 18px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.12);
        margin-top: 10px;
        border: 1px solid #eaeaea;
    }}
    
    /* Botón rojo institucional */
    div.stButton > button:first-child {{
        background-color: #e53935 !important;
        color: white !important;
        font-weight: bold;
        font-size: 1.05rem;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1rem;
        width: 100%;
        box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.3);
        transition: all 0.2s ease;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #c62828 !important;
    }}

    /* Tarjeta de resultado */
    .result-box {{
        background: #ffffff;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #e53935;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.1);
        margin-top: 15px;
        color: #212529;
    }}
    </style>
    """
    if img_base64
    else """
    <style>
    .stApp { background-color: #f4f6f9; }
    </style>
    """
)

st.markdown(css_movil, unsafe_allow_html=True)

# Mostrar la imagen como banner superior adaptable (no como fondo gigante de PC)
if img_base64:
  st.markdown(
      f"""
        <div class="banner-container">
            <img src="{img_base64}" class="banner-img">
        </div>
        """,
      unsafe_allow_html=True,
  )


# --- CARGA DE LAS 36 PÁGINAS / HOJAS DEL EXCEL ---
@st.cache_data
def cargar_padron():
  archivos_excel = glob.glob("*.xlsx") + glob.glob("*.XLSX")
  lista_df = []

  for archivo in archivos_excel:
    try:
      # Leer todas las hojas del archivo Excel (del 1 al 36 o las que tenga)
      excel_file = pd.ExcelFile(archivo)
      for hoja in excel_file.sheet_names:
        df_hoja = pd.read_excel(archivo, sheet_name=hoja)
        # Limpiar espacios en los nombres de las columnas
        df_hoja.columns = df_hoja.columns.astype(str).str.strip()
        lista_df.append(df_hoja)
    except Exception:
      pass

  if lista_df:
    df_consolidado = pd.concat(lista_df, ignore_index=True)

    # Buscar la columna exacta o alternativas de documento
    columnas_lower = {col.lower(): col for col in df_consolidado.columns}
    columna_real = None

    for posible in ["nº de documento", "n° de documento", "nro de documento", "cedula", "ci", "documento"]:
      if posible in columnas_lower:
        columna_real = columnas_lower[posible]
        break

    if not columna_real:
      for col in df_consolidado.columns:
        if "documento" in col.lower() or "ced" in col.lower() or col.lower() == "ci":
          columna_real = col
          break

    if columna_real:
      if columna_real != "cedula":
        df_consolidado = df_consolidado.rename(columns={columna_real: "cedula"})

      df_consolidado["cedula_limpia"] = (
          df_consolidado["cedula"].astype(str).str.replace(".", "").str.strip()
      )
      return df_consolidado

  return pd.DataFrame()


try:
  df = cargar_padron()

  if not df.empty:
    st.markdown(
        """
        <div class="floating-card">
        <h3 style="color: #222; text-align: center; margin-top: 0; margin-bottom: 12px; font-size: 1.1rem; font-weight: 700;">Número de cédula</h3>
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

          # Detección flexible de los nombres de columnas para los datos personales
          nombre = persona.get("nombre", persona.get("NOMBRE", persona.get("Nombres", "")))
          apellido = persona.get("apellido", persona.get("APELLIDO", persona.get("Apellidos", "")))
          local = persona.get("local", persona.get("LOCAL", persona.get("Lugar de Votacion", "No especificado")))
          secc = persona.get("secc", persona.get("SECC", persona.get("Seccional", "43")))

          cedula_str = f"{int(persona['cedula']):,}".replace(",", ".")

          st.markdown(
              f"""
                <div class="result-box">
                    <h4 style="color: #e53935; margin-top: 0; margin-bottom: 10px; font-size: 1.1rem;">¡Votante Encontrado!</h4>
                    <p style="margin: 5px 0; font-size: 0.95rem;"><b>Nombre:</b> {nombre} {apellido}</p>
                    <p style="margin: 5px 0; font-size: 0.95rem;"><b>Cédula:</b> {cedula_str}</p>
                    <p style="margin: 5px 0; font-size: 0.95rem;"><b>Local de Votación:</b> {local}</p>
                    <p style="margin: 5px 0; font-size: 0.95rem;"><b>Seccional N°:</b> {secc}</p>
                </div>
                """,
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              """
                <div class="result-box" style="border-left-color: #f57c00;">
                    <p style="margin:0; color: #d84315; font-weight: bold; font-size: 0.95rem;">No se encontró esa cédula en el padrón de la Seccional 43.</p>
                </div>
                """,
              unsafe_allow_html=True,
          )
      else:
        st.warning("Por favor, ingresa un número de cédula.")
  else:
    st.error(
        "⚠️ No se detectó ningún archivo Excel (.xlsx) válido en el repositorio o no contiene la columna 'Nº de Documento'."
    )

except Exception as e:
  st.error(f"Error al procesar la información: {e}")
