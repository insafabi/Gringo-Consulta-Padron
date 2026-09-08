import base64
import glob
import os
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Consulta Padrón - Seccional 43",
    page_icon="🔴",
    layout="centered",
)


# Función para el fondo en base64
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

# Estilos CSS generales para la tarjeta translúcida y el fondo móvil
css_movil = (
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
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.2);
        pointer-events: none;
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 3.5rem;
        padding-bottom: 3rem;
        max-width: 420px;
    }}
    
    /* Contenedor translúcido principal */
    .element-container {{
        position: relative;
        z-index: 1;
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


# --- CARGA DEL EXCEL (36 TABLAS) ---
@st.cache_data
def cargar_padron():
  archivos_excel = glob.glob("*.xlsx") + glob.glob("*.XLSX")
  lista_df = []

  for archivo in archivos_excel:
    try:
      excel_file = pd.ExcelFile(archivo)
      for hoja in excel_file.sheet_names:
        df_hoja = pd.read_excel(archivo, sheet_name=hoja)
        df_hoja.columns = df_hoja.columns.astype(str).str.strip()
        lista_df.append(df_hoja)
    except Exception:
      pass

  if lista_df:
    df_consolidado = pd.concat(lista_df, ignore_index=True)

    if "Nº de Documento" in df_consolidado.columns:
      df_consolidado = df_consolidado.rename(
          columns={"Nº de Documento": "cedula"}
      )
    elif "N° de Documento" in df_consolidado.columns:
      df_consolidado = df_consolidado.rename(
          columns={"N° de Documento": "cedula"}
      )

    if "cedula" in df_consolidado.columns:
      df_consolidado["cedula_limpia"] = (
          df_consolidado["cedula"].astype(str).str.replace(".", "").str.strip()
      )
      return df_consolidado

  return pd.DataFrame()


try:
  df = cargar_padron()

  if not df.empty:
    if "resultado_persona" not in st.session_state:
      st.session_state.resultado_persona = None

    # Contenedor visual translúcido usando st.container
    with st.container():
      if st.session_state.resultado_persona is None:
        # --- PANTALLA DE BÚSQUEDA ---
        st.markdown(
            "<h3"
            ' style="color: #111; text-align: center; margin-top: 0;'
            ' margin-bottom: 12px; font-size: 1.1rem; font-weight:'
            ' 800;">Número de cédula</h3>',
            unsafe_allow_html=True,
        )

        cedula_input = st.text_input(
            "Número de cédula",
            placeholder="Ej: 2908339",
            label_visibility="collapsed",
        )

        buscar_clic = st.button("Consultar")

        if buscar_clic:
          if cedula_input:
            clean_input = (
                cedula_input.replace(".", "").replace("-", "").strip()
            )
            resultado = df[df["cedula_limpia"] == clean_input]

            if not resultado.empty:
              st.session_state.resultado_persona = resultado.iloc[0].to_dict()
              st.rerun()
            else:
              st.warning("No se encontró esa cédula en el padrón.")
          else:
            st.warning("Por favor, ingresa un número de cédula.")

      else:
        # --- PANTALLA DE RESULTADOS (DISEÑO LIMPIO NATIVO) ---
        p = st.session_state.resultado_persona

        nombre_completo = (
            f"{p.get('NOMBRE', '')} {p.get('APELLIDO', '')}".strip()
        )
        desc_local = str(p.get("DESC_LOCAL", p.get("local", "")))
        mesa = str(p.get("mesa", "-"))
        orden = str(p.get("orden", "-"))
        cedula_str = f"{int(p['cedula']):,}".replace(",", ".")

        st.markdown(
            "<h3"
            ' style="color: #111; text-align: center; margin-top: 0;'
            ' margin-bottom: 15px; font-size: 1.15rem; font-weight:'
            ' 800;">Datos del elector</h3>',
            unsafe_allow_html=True,
        )

        # Usando campos limpios de Streamlit
        st.markdown(
            '<p style="font-size: 0.72rem; font-weight: 700; color: #e53935;'
            ' text-transform: uppercase; margin-bottom: -10px;">👤 Nombre y'
            " Apellido</p>",
            unsafe_allow_html=True,
        )
        st.info(nombre_completo)

        st.markdown(
            '<p style="font-size: 0.72rem; font-weight: 700; color: #e53935;'
            ' text-transform: uppercase; margin-bottom: -10px;">🆔 Cédula de'
            " Identidad</p>",
            unsafe_allow_html=True,
        )
        st.info(cedula_str)

        st.markdown(
            '<p style="font-size: 0.72rem; font-weight: 700; color: #e53935;'
            ' text-transform: uppercase; margin-bottom: -10px;">📍 Local de'
            " Votación</p>",
            unsafe_allow_html=True,
        )
        st.info(desc_local)

        col1, col2 = st.columns(2)
        with col1:
          st.markdown(
              '<p style="font-size: 0.72rem; font-weight: 700; color: #e53935;'
              ' text-transform: uppercase; margin-bottom: -10px;">🗳️'
              " Mesa</p>",
              unsafe_allow_html=True,
          )
          st.info(mesa)
        with col2:
          st.markdown(
              '<p style="font-size: 0.72rem; font-weight: 700; color: #e53935;'
              ' text-transform: uppercase; margin-bottom: -10px;">📋'
              " Orden</p>",
              unsafe_allow_html=True,
          )
          st.info(orden)

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        if st.button("VOLVER"):
          st.session_state.resultado_persona = None
          st.rerun()

  else:
    st.error(
        "⚠️ No se detectó el archivo Excel o la columna de cédula requerida."
    )

except Exception as e:
  st.error(f"Error al procesar la información: {e}")
