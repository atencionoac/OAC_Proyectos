import pandas as pd
import streamlit as st
import io

def cargar_y_unir():
    # Cargamos los archivos (puedes añadir un spinner para archivos grandes)
    with st.spinner('Procesando 66,000 registros...'):
        df_a = pd.read_excel("proyectos_antiguos.xls")
        df_b = pd.read_excel("proyectos_recientes.xls")
        return pd.concat([df_a, df_b], ignore_index=True)

def main():
    st.set_page_config(page_title="Consolidador de Proyectos", layout="wide")
    
    st.title("📂 Gestión de Proyectos Consolidados")
    st.info(f"Sistema optimizado para búsqueda rápida en grandes volúmenes de datos.")

    try:
        # Usamos st.cache_data para que no tenga que leer los Excel cada vez que escribes una letra
        if 'df_master' not in st.session_state:
            st.session_state.df_master = cargar_y_unir()
        
        df = st.session_state.df_master

        # --- BUSCADOR DINÁMICO ---
        st.subheader("🔍 Buscador en tiempo real")
        busqueda = st.text_input(
            "Escribe el fragmento del Código organización:", 
            placeholder="Ej: ORG-20",
            help="El filtrado se aplica automáticamente mientras escribes.",
        )

        # Filtrado optimizado
        if busqueda:
            # Convertimos a string y buscamos coincidencias parciales (case insensitive)
            mask = df['Código organización'].astype(str).str.contains(busqueda, case=False, na=False)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        # --- VISUALIZACIÓN ---
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"Resultados encontrados: **{len(df_filtrado):,}**")
        
        # Mostrar el dataframe (Streamlit maneja bien miles de filas con scroll)
        st.dataframe(df_filtrado, use_container_width=True, height=500)

        # --- DESCARGA ---
        st.divider()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Opción: Guardar solo lo filtrado o todo el consolidado
            df_filtrado.to_excel(writer, index=False, sheet_name='Resultados')
        
        st.download_button(
            label="📥 Descargar resultados actuales (.xlsx)",
            data=buffer.getvalue(),
            file_name="proyectos_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except FileNotFoundError:
        st.error("❌ Archivos no encontrados. Verifica que estén en la misma carpeta.")
    except Exception as e:
        st.error(f"⚠️ Error inesperado: {e}")

if __name__ == "__main__":
    main()