import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import acf, pacf
import inspect
# Nuevos imports para análisis completo
from src.analysis.analysis import get_analyze_complete, analisis_estacionaridad


def run():
    print(">>> Archivo cargado:", inspect.getfile(inspect.currentframe()))

    SEGMENTED_PATH = "src/data/segmented"

    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.title("📊 Análisis de series temporales")
    st.markdown("Para ejecutar el análisis selecciona una provincia y un producto.")

    # ---------------------------------------------------------
    # 1. Cargar provincias y productos (CÓDIGO ORIGINAL)
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

    # ---------------------------------------------------------
    # 3. BOTONES PARA EJECUTAR ANÁLISIS (CÓDIGO ORIGINAL + NUEVO)
    # ---------------------------------------------------------

    st.markdown("---")

    # Crear 3 columnas ahora (en lugar de 2)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Análisis Básico"):
            with st.spinner("Ejecutando Análisis Básico..."):
                analisis_estacionaridad(provincia, producto)
            st.success("✅ Análisis básico completado.")

    with col2:
        mostrar_resultados_basicos = st.button("🔍 Ver resultados básicos")

    # ---------------------------------------------------------
    # 4. SECCIÓN ANÁLISIS BÁSICO (CÓDIGO ORIGINAL)
    # ---------------------------------------------------------

    if mostrar_resultados_basicos:
        try:
            df_original, df_stationary, stationary_flag, metadata, metadata_completo = get_analyze_complete(provincia, producto)
            # Tabs para organizar mejor
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📊 Estadísticas",
                "🔗 Correlaciones",
                "📈 Series Temporales",
                "🎯 Diagnósticos",
                "📊 Estacionaridad",
                "📉 ACF/PACF"
            ])

            # ========================================================
            # TAB 1: ESTADÍSTICAS GENERALES
            # ========================================================
            with tab1:
                st.subheader("📊 Estadísticas Generales")
                
                stats = metadata_completo['estadisticas']
                
                # Métricas en columnas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Registros", f"{stats['n_registros']:,}")
                with col2:
                    st.metric("Precio Medio", f"{stats['precio']['media']:.4f} €/L")
                with col3:
                    st.metric("Desv. Estándar", f"{stats['precio']['std']:.4f}")
                with col4:
                    st.metric("Festivos", f"{stats['festivos']['total']} ({stats['festivos']['porcentaje']:.1f}%)")
                
                st.markdown("---")
                
                # Tabla de estadísticas detalladas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Precio (€/L)**")
                    precio_df = pd.DataFrame({
                        'Métrica': ['Media', 'Mediana', 'Mínimo', 'Máximo', 'Desv. Std'],
                        'Valor': [
                            f"{stats['precio']['media']:.4f}",
                            f"{stats['precio']['mediana']:.4f}",
                            f"{stats['precio']['min']:.4f}",
                            f"{stats['precio']['max']:.4f}",
                            f"{stats['precio']['std']:.4f}"
                        ]
                    })
                    st.dataframe(precio_df, hide_index=True, use_container_width=True)
                
                with col2:
                    st.markdown("**Brent (USD/Barril)**")
                    brent_df = pd.DataFrame({
                        'Métrica': ['Media', 'Mínimo', 'Máximo', 'Desv. Std'],
                        'Valor': [
                            f"{stats['brent']['media']:.2f}",
                            f"{stats['brent']['min']:.2f}",
                            f"{stats['brent']['max']:.2f}",
                            f"{stats['brent']['std']:.2f}"
                        ]
                    })
                    st.dataframe(brent_df, hide_index=True, use_container_width=True)

            # ========================================================
            # TAB 2: CORRELACIONES
            # ========================================================
            with tab2:
                st.subheader("🔗 Análisis de Correlaciones")
                
                corr = metadata_completo['correlaciones']
                
                # Mostrar correlaciones principales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Precio vs Brent",
                        f"{corr['precio_brent']:.3f}",
                        delta=corr['interpretacion']['Brent']['descripcion']
                    )
                
                with col2:
                    st.metric(
                        "Precio vs Tipo Cambio",
                        f"{corr['precio_tipo_cambio']:.3f}",
                        delta=corr['interpretacion']['TipoCambio']['descripcion']
                    )
                
                with col3:
                    st.metric(
                        "Precio vs Festivo",
                        f"{corr['precio_festivo']:.3f}",
                        delta=corr['interpretacion']['Festivo']['descripcion']
                    )
                
                st.markdown("---")
                
                # Heatmap de correlaciones
                corr_matrix = pd.DataFrame(corr['matriz'])
                
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    text=corr_matrix.values,
                    texttemplate='%{text:.3f}',
                    textfont={"size": 12},
                    colorbar=dict(title="Correlación")
                ))
                
                fig_corr.update_layout(
                    title='Matriz de Correlación',
                    height=500,
                    xaxis_title='',
                    yaxis_title=''
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Interpretación
                st.markdown("**💡 Interpretación:**")
                for var, info in corr['interpretacion'].items():
                    st.write(f"- **{var}**: {info['descripcion']} (r = {info['valor']:.3f})")

            # ========================================================
            # TAB 3: SERIES TEMPORALES
            # ========================================================
            with tab3:
                st.subheader("📈 Series Temporales con Variables Exógenas")
                
                # Reset index para Plotly
                df_plot = df_original.reset_index()
                
                # Crear subplots
                fig_series = make_subplots(
                    rows=4, cols=1,
                    subplot_titles=('Precio', 'Precio Brent', 'Tipo de Cambio EUR/USD', 'Festivos'),
                    vertical_spacing=0.08
                )
                
                # Precio
                fig_series.add_trace(
                    go.Scatter(x=df_plot['Fecha'], y=df_plot['Precio'], 
                              name='Precio', line=dict(color='darkred', width=1)),
                    row=1, col=1
                )
          
                # Brent
                fig_series.add_trace(
                    go.Scatter(x=df_plot['Fecha'], y=df_plot['Brent'], 
                              name='Brent', line=dict(color='darkblue', width=1)),
                    row=2, col=1
                )
                
                # Tipo Cambio
                fig_series.add_trace(
                    go.Scatter(x=df_plot['Fecha'], y=df_plot['TipoCambio'], 
                              name='EUR/USD', line=dict(color='darkgreen', width=1)),
                    row=3, col=1
                )
                
                # Festivos
                festivos_plot = df_plot[df_plot['Festivo'] == 1]
                fig_series.add_trace(
                    go.Scatter(x=festivos_plot['Fecha'], y=festivos_plot['Festivo'], 
                              name='Festivo', mode='markers', 
                              marker=dict(color='red', size=5)),
                    row=4, col=1
                )
                
                fig_series.update_layout(
                    height=1000,
                    showlegend=False,
                    hovermode='x unified'
                )
                
                fig_series.update_yaxes(title_text="Precio (dif)", row=1, col=1)
                fig_series.update_yaxes(title_text="USD/Barril", row=2, col=1)
                fig_series.update_yaxes(title_text="EUR/USD", row=3, col=1)
                fig_series.update_yaxes(title_text="Festivo", row=4, col=1)
                
                st.plotly_chart(fig_series, use_container_width=True)
                
                # Gráficos de dispersión
                st.markdown("**Relación Precio vs Variables Exógenas**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_scatter1 = px.scatter(
                        df_plot, x='Brent', y='Precio',
                        title='Precio vs Brent',
                        trendline='ols',
                        opacity=0.5
                    )
                    st.plotly_chart(fig_scatter1, use_container_width=True)
                
                with col2:
                    fig_scatter2 = px.scatter(
                        df_plot, x='TipoCambio', y='Precio',
                        title='Precio vs Tipo de Cambio',
                        trendline='ols',
                        opacity=0.5
                    )
                    st.plotly_chart(fig_scatter2, use_container_width=True)

            # ========================================================
            # TAB 4: DIAGNÓSTICOS
            # ========================================================
            with tab4:
                st.subheader("🎯 Diagnósticos Avanzados")
                
                # Test de Granger
                st.markdown("### 🔗 Test de Causalidad de Granger")
                
                granger = metadata_completo.get('causalidad', {})
                
                if 'error' in granger:
                    st.warning(f"⚠️ {granger['error']}")
                else:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'brent' in granger and 'error' not in granger['brent']:
                            brent_causa = granger['brent']['causa_precio']
                            st.metric(
                                "Brent → Precio",
                                "✅ SÍ causa" if brent_causa else "❌ NO causa",
                                f"p-value: {granger['brent']['p_value_minimo']:.4f}"
                            )
                            if brent_causa:
                                st.info(f"Lag óptimo: {granger['brent']['lag_optimo']} días")
                    
                    with col2:
                        if 'tipo_cambio' in granger and 'error' not in granger['tipo_cambio']:
                            tc_causa = granger['tipo_cambio']['causa_precio']
                            st.metric(
                                "Tipo Cambio → Precio",
                                "✅ SÍ causa" if tc_causa else "❌ NO causa",
                                f"p-value: {granger['tipo_cambio']['p_value_minimo']:.4f}"
                            )
                            if tc_causa:
                                st.info(f"Lag óptimo: {granger['tipo_cambio']['lag_optimo']} días")
                
                st.markdown("---")
                
                # VIF (Multicolinealidad)
                st.markdown("### 📊 Multicolinealidad (VIF)")
                
                vif = metadata_completo.get('multicolinealidad', {})
                
                if 'error' in vif:
                    st.warning(f"⚠️ {vif['error']}")
                else:
                    st.info(f"**Evaluación:** {vif['problema_multicolinealidad']}")
                    
                    vif_df = pd.DataFrame(vif['vif_por_variable'])
                    
                    fig_vif = go.Figure(data=[
                        go.Bar(
                            x=vif_df['variable'],
                            y=vif_df['vif'],
                            marker_color=[
                                'green' if v < 5 else 'orange' if v < 10 else 'red' 
                                for v in vif_df['vif']
                            ],
                            text=vif_df['vif'],
                            texttemplate='%{text:.2f}',
                            textposition='outside'
                        )
                    ])
                    
                    fig_vif.add_hline(y=5, line_dash="dash", line_color="orange", 
                                     annotation_text="VIF = 5")
                    fig_vif.add_hline(y=10, line_dash="dash", line_color="red",
                                     annotation_text="VIF = 10")
                    
                    fig_vif.update_layout(
                        title='Factor de Inflación de la Varianza (VIF)',
                        xaxis_title='Variable',
                        yaxis_title='VIF',
                        height=400
                    )
                    
                    st.plotly_chart(fig_vif, use_container_width=True)
                    
                    st.markdown("""
                    **Interpretación VIF:**
                    - VIF < 5: ✅ No hay problemas de multicolinealidad
                    - VIF 5-10: ⚠️ Multicolinealidad moderada
                    - VIF > 10: ❌ Multicolinealidad severa
                    """)
                
                st.markdown("---")
                
                # Análisis de festivos
                st.markdown("### 🎉 Análisis de Festivos")
                
                festivos_analysis = metadata_completo.get('festivos_analisis', {})
                
                if 'error' in festivos_analysis:
                    st.warning(f"⚠️ {festivos_analysis['error']}")
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Días Festivos", festivos_analysis['n_festivos'])
                    with col2:
                        st.metric("Precio Medio Festivos", 
                                 f"{festivos_analysis['media_festivos']:.4f} €/L")
                    with col3:
                        st.metric("Precio Medio No Festivos", 
                                 f"{festivos_analysis['media_no_festivos']:.4f} €/L")
                    
                    diferencia = festivos_analysis['diferencia']
                    sig = festivos_analysis['test_t']['diferencia_significativa']
                    
                    if sig:
                        st.success(f"✅ Diferencia SIGNIFICATIVA: {diferencia:.4f} €/L (p-value: {festivos_analysis['test_t']['p_value']:.4f})")
                    else:
                        st.info(f"ℹ️ Diferencia NO significativa: {diferencia:.4f} €/L (p-value: {festivos_analysis['test_t']['p_value']:.4f})")
            
            # ========================================================
            # TAB 5: ESTACIONARIDAD
            # ========================================================
            with tab5:
                # ---------------------------------------------------------
                # 5. Visualización de la serie original (CÓDIGO ORIGINAL)
                # ---------------------------------------------------------
                st.subheader("📈 Serie original")
                fig1 = px.line(
                    df_original,
                    x=df_original.index,
                    y="Precio",
                    title=f"Precio diario — {provincia} / {producto}"
                )
                st.plotly_chart(fig1, use_container_width=True)

                # ---------------------------------------------------------
                # 6. Visualización de la serie transformada (CÓDIGO ORIGINAL)
                # ---------------------------------------------------------

                if not stationary_flag:
                    st.subheader("🔁 Serie transformada (diferenciada)")
                    fig2 = px.line(
                        df_stationary,
                        x="Fecha",
                        y="Precio",
                        title="Serie diferenciada"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.success("La serie ya es estacionaria. No fue necesario diferenciarla.")

                # ---------------------------------------------------------
                # 7. Resultados estadísticos (CÓDIGO ORIGINAL)
                # ---------------------------------------------------------

                st.subheader("📊 Resultados de estacionariedad")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ADF p-value", f"{metadata['adf']['pvalue']:.4f}")
                    st.metric("ADF stat", f"{metadata['adf']['stat']:.2f}")

                with col2:
                    st.metric("KPSS p-value", f"{metadata['kpss']['pvalue']:.4f}")
                    st.metric("KPSS stat", f"{metadata['kpss']['stat']:.2f}")

                estado = "✅ Estacionaria" if stationary_flag else "⚠️ No estacionaria"
                st.info(f"**Serie evaluada como:** {estado}")

            # ========================================================
            # TAB 6: ACF/PACF
            # ========================================================
            with tab6:
                st.subheader("📉 Análisis ACF y PACF")
                
                params = metadata_completo.get('parametros_arima', {})
                
                if 'error' in params:
                    st.warning(f"⚠️ {params['error']}")
                else:
                    # Mostrar parámetros sugeridos
                    st.success(f"**🎯 Parámetros ARIMA Sugeridos (Preliminares):** `{params['recomendacion']}`")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("p (AR)", params['p'])
                    with col2:
                        st.metric("d (Diferenciación)", params['d'])
                    with col3:
                        st.metric("q (MA)", params['q'])
                    
                    st.markdown("---")
                    
                    # CALCULAR ACF/PACF PARA AMBAS SERIES
                    # Serie original
                    serie_original = df_original['Precio'].dropna()
                    nlags_orig = min(40, len(serie_original) // 3)
                    acf_orig = acf(serie_original, nlags=nlags_orig)
                    pacf_orig = pacf(serie_original, nlags=nlags_orig)
                    
                    # Serie estacionaria
                    serie_estacionaria = df_stationary.set_index('Fecha')['Precio'].dropna()
                    nlags_stat = min(40, len(serie_estacionaria) // 3)
                    acf_stat = acf(serie_estacionaria, nlags=nlags_stat)
                    pacf_stat = pacf(serie_estacionaria, nlags=nlags_stat)
                    
                    # Límites de confianza
                    conf_limit_orig = 1.96 / np.sqrt(len(serie_original))
                    conf_limit_stat = 1.96 / np.sqrt(len(serie_estacionaria))
                    
                    # CREAR 4 SUBPLOTS (2x2) COMO EL NOTEBOOK
                    fig_acf_pacf = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=(
                            'ACF - Serie Original',
                            'PACF - Serie Original',
                            f'ACF - Serie Estacionaria (d={params["d"]})',
                            f'PACF - Serie Estacionaria (d={params["d"]})'
                        ),
                        vertical_spacing=0.12,
                        horizontal_spacing=0.10
                    )
                    
                    # ROW 1, COL 1: ACF Original
                    for i in range(len(acf_orig)):
                        val = acf_orig[i]
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i, i], y=[0, val], mode='lines',
                                      line=dict(color='steelblue', width=2),
                                      showlegend=False, hoverinfo='skip'),
                            row=1, col=1
                        )
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i], y=[val], mode='markers',
                                      marker=dict(color='steelblue', size=5),
                                      showlegend=False,
                                      hovertemplate=f'Lag: {i}<br>ACF: {val:.4f}<extra></extra>'),
                            row=1, col=1
                        )
                    
                    fig_acf_pacf.add_hline(y=conf_limit_orig, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=1, col=1)
                    fig_acf_pacf.add_hline(y=-conf_limit_orig, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=1, col=1)
                    fig_acf_pacf.add_hline(y=0, line_color="black", line_width=1, row=1, col=1)
                    
                    # ROW 1, COL 2: PACF Original
                    for i in range(len(pacf_orig)):
                        val = pacf_orig[i]
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i, i], y=[0, val], mode='lines',
                                      line=dict(color='steelblue', width=2),
                                      showlegend=False, hoverinfo='skip'),
                            row=1, col=2
                        )
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i], y=[val], mode='markers',
                                      marker=dict(color='steelblue', size=5),
                                      showlegend=False,
                                      hovertemplate=f'Lag: {i}<br>PACF: {val:.4f}<extra></extra>'),
                            row=1, col=2
                        )
                    
                    fig_acf_pacf.add_hline(y=conf_limit_orig, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=1, col=2)
                    fig_acf_pacf.add_hline(y=-conf_limit_orig, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=1, col=2)
                    fig_acf_pacf.add_hline(y=0, line_color="black", line_width=1, row=1, col=2)
                    
                    # ROW 2, COL 1: ACF Estacionaria
                    for i in range(len(acf_stat)):
                        val = acf_stat[i]
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i, i], y=[0, val], mode='lines',
                                      line=dict(color='steelblue', width=2),
                                      showlegend=False, hoverinfo='skip'),
                            row=2, col=1
                        )
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i], y=[val], mode='markers',
                                      marker=dict(color='steelblue', size=5),
                                      showlegend=False,
                                      hovertemplate=f'Lag: {i}<br>ACF: {val:.4f}<extra></extra>'),
                            row=2, col=1
                        )
                    
                    fig_acf_pacf.add_hline(y=conf_limit_stat, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=2, col=1)
                    fig_acf_pacf.add_hline(y=-conf_limit_stat, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=2, col=1)
                    fig_acf_pacf.add_hline(y=0, line_color="black", line_width=1, row=2, col=1)
                    
                    # ROW 2, COL 2: PACF Estacionaria
                    for i in range(len(pacf_stat)):
                        val = pacf_stat[i]
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i, i], y=[0, val], mode='lines',
                                      line=dict(color='steelblue', width=2),
                                      showlegend=False, hoverinfo='skip'),
                            row=2, col=2
                        )
                        fig_acf_pacf.add_trace(
                            go.Scatter(x=[i], y=[val], mode='markers',
                                      marker=dict(color='steelblue', size=5),
                                      showlegend=False,
                                      hovertemplate=f'Lag: {i}<br>PACF: {val:.4f}<extra></extra>'),
                            row=2, col=2
                        )
                    
                    fig_acf_pacf.add_hline(y=conf_limit_stat, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=2, col=2)
                    fig_acf_pacf.add_hline(y=-conf_limit_stat, line_dash="dash", line_color="red", 
                                          line_width=1.5, row=2, col=2)
                    fig_acf_pacf.add_hline(y=0, line_color="black", line_width=1, row=2, col=2)
                    
                    # Configuración final
                    fig_acf_pacf.update_xaxes(title_text="Lag", gridcolor='lightgray')
                    fig_acf_pacf.update_yaxes(gridcolor='lightgray')
                    
                    fig_acf_pacf.update_layout(
                        height=900,
                        showlegend=False,
                        hovermode='closest',
                        title_text="Análisis ACF y PACF"
                    )
                    
                    st.plotly_chart(fig_acf_pacf, use_container_width=True)
                    
                    # Interpretación
                    st.markdown("---")
                    st.markdown("**💡 Interpretación:**")
                    
                    lags_sig_acf = [i for i, val in enumerate(acf_stat[1:], 1) if abs(val) > conf_limit_stat]
                    lags_sig_pacf = [i for i, val in enumerate(pacf_stat[1:], 1) if abs(val) > conf_limit_stat]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Serie Estacionaria - ACF**")
                        st.write(f"- Límite confianza 95%: ±{conf_limit_stat:.4f}")
                        if lags_sig_acf:
                            st.write(f"- Lags significativos: {', '.join(map(str, lags_sig_acf[:10]))}")
                            st.write(f"- **q sugerido = {params['q']}**")
                        else:
                            st.write("- No hay lags significativos")
                    
                    with col2:
                        st.markdown("**Serie Estacionaria - PACF**")
                        st.write(f"- Límite confianza 95%: ±{conf_limit_stat:.4f}")
                        if lags_sig_pacf:
                            st.write(f"- Lags significativos: {', '.join(map(str, lags_sig_pacf[:10]))}")
                            st.write(f"- **p sugerido = {params['p']}**")
                        else:
                            st.write("- No hay lags significativos")

        except FileNotFoundError:
            st.warning("⚠️ Aún no se ha ejecutado el análisis completo para este segmento. Haz clic en '🔬 Análisis Completo' arriba.")
        except Exception as e:
            st.error(f"❌ Error al cargar análisis completo: {str(e)}")
            with st.expander("Ver detalles del error"):
                import traceback
                st.code(traceback.format_exc())