import base64
import glob
import os
import pandas as pd
import streamlit as st

# Configuración de la página optimizada para móvil
st.set_page_config(
    page_title="Consulta Padrón - Seccional 43",
    page_icon="🔴",
    layout="centered",
)


# Función para convertir la imagen local a base64 para el fondo exacto
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

# Estilos CSS con fondo de pantalla completo y tarjetas flotantes translúcidas estilo app
css_movil = (
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Fondo de pantalla adaptado a móviles con la imagen institucional */
    .stApp {{
        background-image: url("{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Capa oscura sutil opcional para mejorar la lectura sobre el fondo */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.25);
        pointer-events: none;
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 440px;
    }}
    
    /* Tarjeta flotante translúcida para el buscador */
    .floating-card {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 22px 20px;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3);
        margin-top: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
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
        box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.4);
        transition: all 0.2s ease;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #c62828 !important;
    }}

    /* Tarjeta de resultados flotante con el mismo estilo translúcido */
    .result-box {{
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 20px 18px;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3);
        margin-top: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        color: #212529;
    }}

    .field-label {{
        font-size: 0.75rem;
        font-weight: 700;
        color: #e53935;
        text-transform: uppercase;
        margin-bottom: 2px;
        letter-spacing: 0.5px;
    }}

    .field-value {{
        background: rgba(255, 255, 255, 0.95);
        padding: 10px 14px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #111;
        margin-bottom: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: inset 0px 1px 3px rgba(0,0,0,0.05);
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


# --- CARGA AUTOMÁTICA DE LAS 36 HOJAS DEL EXCEL ---
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
    # Si aún no se ha buscado, mostramos la tarjeta de búsqueda
    st.markdown(
        """
        <div class="floating-card">
        <h3 style="color: #111; text-align: center; margin-top: 0; margin-bottom: 12px; font-size: 1.1rem; font-weight: 800;">Número de cédula</h3>
        """,
        unsafe_allow_html=True,
    )

    cedula_input = st.text_input(
        "Número de cédula",
        placeholder="Ej: 4610728",
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

          nombre = str(persona.get("NOMBRE", ""))
          apellido = str(persona.get("APELLIDO", ""))
          nombre_completo = f"{nombre} {apellido}".strip()
          desc_local = str(
              persona.get("DESC_LOCAL", persona.get("local", ""))
          )
          mesa = str(persona.get("mesa", "-"))
          orden = str(persona.get("orden", "-"))

          cedula_str = f"{int(persona['cedula']):,}".replace(",", ".")

          # Se agregó unsafe_allow_html=True para que pinte bien el diseño translúcido
          st.markdown(
              f"""
                <div class="result-box">
                    <h3 style="color: #222; text-align: center; margin-top: 0; margin-bottom: 15px; font-size: 1.1rem; font-weight: 800;">Datos del elector</h3>
                    
                    <div class="field-label">👤 Nombre y Apellido</div>
                    <div class="field-value">{nombre_completo}</div>

                    <div class="field-label">🆔 Cédula de Identidad</div>
                    <div class="field-value">{cedula_str}</div>

                    <div class="field-label">📍 Local de Votación</div>
                    <div class="field-value">{desc_local}</div>

                    <div style="display: flex; gap: 10px;">
                        <div style="flex: 1;">
                            <div class="field-label">🗳️ Mesa</div>
                            <div class="field-value" style="text-align: center;">{mesa}</div>
                        </div>
                        <div style="flex: 1;">
                            <div class="field-label">📋 Orden</div>
                            <div class="field-value" style="text-align: center;">{orden}</div>
                        </div>
                    </div>
                </div>
                """,
              unsafe_allow_html=True,
          )

          if st.button("VOLVER"):
            st.rerun()

        else:
          st.markdown(
              """
                <div class="result-box" style="border-left: 6px solid #f57c00;">
                    <p style="margin:0; color: #d84315; font-weight: bold; text-align: center; font-size: 0.95rem;">No se encontró esa cédula en el padrón.</p>
                </div>
                """,
              unsafe_allow_html=True,
          )
      else:
        st.warning("Por favor, ingresa un número de cédula.")
  else:
    st.error(
        "⚠️ No se detectó el archivo Excel o la columna de cédula requerida."
    )

except Exception as e:
  st.error(f"Error al procesar la información: {e}")
