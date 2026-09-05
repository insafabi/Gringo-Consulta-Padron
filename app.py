import glob
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Consulta de Padron Electoral", page_icon="🗳️", layout="centered"
)

st.title("🗳️ Consulta de Lugar de Votación")
st.markdown("### Seccional N° 43")


@st.cache_data
def cargar_todos_los_padrones():
  # Busca todos los archivos excel (.xlsx) en la misma carpeta
  archivos_excel = glob.glob("*.xlsx")

  lista_df = []
  for archivo in archivos_excel:
    try:
      df_temp = pd.read_excel(archivo)
      # Limpiar nombres de columnas eliminando espacios
      df_temp.columns = df_temp.columns.astype(str).str.strip()
      lista_df.append(df_temp)
    except Exception as e:
      st.warning(f"No se pudo leer el archivo: {archivo}")

  if lista_df:
    df_consolidado = pd.concat(lista_df, ignore_index=True)
    # Limpiar columna cedula
    df_consolidado['cedula_limpia'] = (
        df_consolidado['cedula'].astype(str).str.replace('.', '').str.strip()
    )
    return df_consolidado
  else:
    return pd.DataFrame()


try:
  df = cargar_todos_los_padrones()

  if not df.empty:
    st.info(
        f"📊 Base de datos cargada: **{len(df):,}** electores registrados."
        .replace(',', '.')
    )

    cedula_input = st.text_input(
        "Ingresa tu número de Cédula (sin puntos ni espacios):",
        placeholder="Ejemplo: 4187526",
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

          # Si tiene afiliación, se puede mostrar de forma limpia
          if 'PARTIDO' in persona and pd.notna(persona['PARTIDO']):
            st.markdown(f"**Afiliación:** {persona['PARTIDO']}")
        else:
          st.error(
              "No se encontró ninguna persona registrada con ese número de"
              " cédula en estos locales."
          )
      else:
        st.warning("Por favor, ingresa un número de cédula para consultar.")
  else:
    st.error("No se encontraron archivos Excel (.xlsx) en el repositorio.")

except Exception as e:
  st.error("Ocurrió un error al procesar la búsqueda.")
