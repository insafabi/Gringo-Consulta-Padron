import glob
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Consulta de Padrón Electoral", page_icon="🗳️", layout="centered"
)

# --- MOSTRAR PORTADA ---
if os.path.exists("portada.jpg"):
  st.image("portada.jpg", use_container_width=True)
elif os.path.exists("portada.png"):
  st.image("portada.png", use_container_width=True)

st.title("🗳️ Consulta de Lugar de Votación")
st.markdown("### Seccional N° 43")


@st.cache_data
def cargar_datos():
  archivos_excel = glob.glob("*.xlsx")
  lista_df = []
  for archivo in archivos_excel:
    try:
      df_temp = pd.read_excel(archivo)
      df_temp.columns = df_temp.columns.astype(str).str.strip()
      lista_df.append(df_temp)
    except Exception:
      pass

  if lista_df:
    df_consolidado = pd.concat(lista_df, ignore_index=True)
    df_consolidado['cedula_limpia'] = (
        df_consolidado['cedula'].astype(str).str.replace('.', '').str.strip()
    )
    return df_consolidado
  return pd.DataFrame()


try:
  df = cargar_datos()

  if not df.empty:
    st.info(f"📊 Electores cargados: **{len(df):,}**".replace(',', '.'))

    cedula_input = st.text_input(
        "Ingresa tu número de Cédula (sin puntos):", placeholder="Ej: 4187526"
    )

    if st.button("Buscar Votante"):
      if cedula_input:
        clean_input = (
            cedula_input.replace('.', '').replace('-', '').strip()
        )
        resultado = df[df['cedula_limpia'] == clean_input]

        if not resultado.empty:
          persona = resultado.iloc[0]
          st.success("¡Votante encontrado!")

          st.markdown(
              f"**Cédula:** {int(persona['cedula']):,}".replace(',', '.')
          )
          st.markdown(
              f"**Nombre Completo:** {persona['nombre']} {persona['apellido']}"
          )
          st.markdown(f"**Local de Votación:** {persona['local']}")
          st.markdown(f"**Seccional N°:** {persona['secc']}")

          if 'PARTIDO' in persona and pd.notna(persona['PARTIDO']):
            st.markdown(f"**Afiliación:** {persona['PARTIDO']}")
        else:
          st.error("No se encontró esa cédula en la lista.")
      else:
        st.warning("Ingresa un número de cédula.")
  else:
    st.error("No se encontraron archivos de datos (.xlsx) en el repositorio.")

except Exception as e:
  st.error(f"Error al procesar la información: {e}")
