import streamlit as st
import os
from src.forecast.train_model import get_predict, predict_segment,cargar_metadata
import matplotlib.pyplot as plt

def run():
    key="param_s_v2"

    SEGMENTED_PATH = "src/data/segmented"
    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.title("📊 Predicción de Precios de Carburantes")
    st.markdown("Para ejecuta la predicción selecciona una provincia y un producto.")

    # ---------------------------------------------------------
    # 1. Cargar provincias y productos
    # ---------------------------------------------------------

    provincias = sorted([
        d for d in os.listdir(SEGMENTED_PATH)
        if os.path.isdir(os.path.join(SEGMENTED_PATH, d))
    ])

    if not provincias:
        st.error("No se encontraron provincias procesadas.")
        st.stop()

    provincia = st.selectbox("Provincia", provincias)

    productos = sorted([
        d for d in os.listdir(os.path.join(SEGMENTED_PATH, provincia))
        if os.path.isdir(os.path.join(SEGMENTED_PATH, provincia, d))
    ])

    if not productos:
        st.error("No se encontraron productos para esta provincia.")
        st.stop()

    producto = st.selectbox("Producto", productos)

    metadata = cargar_metadata(provincia, producto)
    
    if metadata is None:
        st.warning(f"""
        ⚠️ No se encontró archivo de metadatos para **{provincia} - {producto}**.
        
        Los parámetros SARIMAX deben ser calculados primero mediante análisis estadístico.
        Por favor, ejecuta el análisis en la sección correspondiente.
        """)
        
        # Usar valores por defecto
        usar_defecto = st.checkbox("Usar parámetros por defecto (no recomendado)", value=False)
        
        if not usar_defecto:
            return
        
        # Parámetros por defecto básicos
        params_default = {
            'p': 1, 'd': 1, 'q': 1,
            'seasonal': {'P': 1, 'D': 1, 'Q': 1, 's': 7}
        }
       
        metadata = params_default
        
        st.warning("⚠️ Usando parámetros por defecto. Los resultados pueden no ser óptimos.")
    
    # ========================================================================
    # CONFIGURACIÓN DE PARÁMETROS SARIMAX
    # ========================================================================
    st.markdown("---")
    st.subheader("⚙️ Configuración de Parámetros SARIMAX")
    
    # Mostrar recomendación si existe
    if 'recomendacion' in metadata:
        st.info(f"📌 **Parámetros recomendados:** {metadata['recomendacion']}")
    
    col1, col2, col3 = st.columns(3)
        
    with col1:
        p = st.number_input(
            "p (AR)",
            min_value=0,
            max_value=10,
            value=int(metadata.get('p', 1)),
            step=1,
            help="Orden del componente autoregresivo. Valores típicos: 0-5",
            key="param_p"
        )
        
    with col2:
        d = st.number_input(
            "d (I)",
            min_value=0,
            max_value=3,
            value=int(metadata.get('d', 1)),
            step=1,
            help="Orden de diferenciación para estacionaridad. Valores típicos: 0-2",
            key="param_d"
        )
        
    with col3:
        q = st.number_input(
            "q (MA)",
            min_value=0,
            max_value=10,
            value=int(metadata.get('q', 1)),
            step=1,
            help="Orden del componente de media móvil. Valores típicos: 0-5",
            key="param_q"
        )
        
        # Visualización de la configuración
    st.code(f"ARIMA({p}, {d}, {q})", language="text")
    
    # ========================================================================
    # TAB 2: PARÁMETROS ESTACIONALES (P, D, Q, s)
    # ========================================================================

    seasonal = metadata.get('seasonal', {})
        
    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        P = st.number_input(
            "P (AR estacional)",
            min_value=0,
            max_value=5,
            value=int(seasonal.get('P', 1)),
            step=1,
            help="Orden AR estacional. Valores típicos: 0-2",
            key="param_P"
        )
        
    with col2:
        D = st.number_input(
            "D (I estacional)",
            min_value=0,
            max_value=2,
            value=int(seasonal.get('D', 1)),
            step=1,
            help="Orden de diferenciación estacional. Valores típicos: 0-1",
            key="param_D"
        )
        
    with col3:
        Q = st.number_input(
            "Q (MA estacional)",
            min_value=0,
            max_value=5,
            value=int(seasonal.get('Q', 1)),
            step=1,
            help="Orden MA estacional. Valores típicos: 0-2",
            key="param_Q"
        )
        
    with col4:
        s = st.number_input(
            "s (Período)",
            min_value=0,
            max_value=365,
            value=int(seasonal.get('s', 0)),
            step=1,
            help="Período estacional. Común: 7 (semanal), 30 (mensual), 365 (anual)",
            key="param_s_v2"
        )
        
    # Visualización de la configuración
    st.code(f"SARIMA({P}, {D}, {Q}, {s})", language="text")
    
    # ========================================================================
    # CONFIGURACIÓN COMPLETA
    # ========================================================================
    
    # ---------------------------------------------------------
    # 3. BOTÓN PARA EJECUTAR EL MODELO
    # ---------------------------------------------------------

    st.markdown("---")
    #st.subheader("📊 Ejecutar Predicción")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Predecir serie seleccionada"):
            # Preparar parámetros
            order = (p, d, q)
            seasonal_order = (P, D, Q, s)
            with st.spinner("Ejecutando predicción"):
                 predict_segment(provincia,producto,order,seasonal_order)
            st.success("Predicción completada.")

    with col2:
        mostrar_resultados = st.button("🔍 Ver resultados")

    if not mostrar_resultados:
        st.stop()
    
    y_test, pred_mean, pred_ci, mae, rmse = get_predict(provincia, producto)
    # ---------------------------------------------------------
    # 5. Visualización de la serie original
    # ---------------------------------------------------------
    if mostrar_resultados:
        st.write("MAE:", mae)
        st.write("RMSE:", rmse)

        # --- Visualización ---
        fig, ax = plt.subplots(figsize=(10,5))
        y_test.plot(ax=ax, label="Real", color="blue")
        pred_mean.plot(ax=ax, label="Predicción", color="red")
        ax.fill_between(pred_ci.index,
                        pred_ci.iloc[:,0],
                        pred_ci.iloc[:,1],
                        color="pink", alpha=0.3)
        ax.set_title(f"Predicción de precios - {provincia} / {producto}")
        ax.legend()
        st.pyplot(fig)
