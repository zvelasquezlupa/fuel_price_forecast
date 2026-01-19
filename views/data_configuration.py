import streamlit as st
from src.data_exogenous.load_bret import loadBret, getBret


def run():
    st.title("📥 Carga de precios base (EIA)")
    
    df_final= getBret()
    
    uploaded_file = st.file_uploader(
        "Sube el archivo Excel de la EIA (.xls / .xlsx)",
        type=["xls", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            df_final=loadBret(uploaded_file)
            # --- UI ---
            st.success(f"✅ Datos cargados")

        except Exception as e:
                st.error("❌ Error procesando el archivo")
                st.exception(e)

    if df_final is None:
        st.warning("No hay archivos de precios cargados todavía.")
    else:
        df_final = df_final.sort_values("Fecha", ascending=False)
        df_view = df_final.rename(columns={
            "Fecha": "Fecha",
            "precio_brent": "Precio Brent (USD/barril)",
            "precio_gasolina": "Precio Gasolina (USD/galón)",
            "precio_diesel": "Precio Diésel (USD/galón)"
        })
        st.caption(f"Filas: {len(df_view)} | Desde {df_view['Fecha'].min().date()} hasta {df_view['Fecha'].max().date()}")
        st.subheader("📊 Datos Precio Petroleo")
        st.dataframe(df_view, use_container_width=True)
