import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render(df):
    """
    Renderiza a aba de Análise Exploratória de Dados (EDA)
    """
    st.header("🔍 Análise Exploratória de Dados")
    
    if df is None or df.empty:
        st.warning("Nenhum dado carregado. Por favor, faça o upload de um arquivo CSV.")
        return
    
    # Seção 1: Visão Geral dos Dados
    st.subheader("📋 Visão Geral dos Dados")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Número de Linhas", df.shape[0])
    with col2:
        st.metric("Número de Colunas", df.shape[1])
    with col3:
        st.metric("Valores Ausentes", df.isnull().sum().sum())
    with col4:
        st.metric("Duplicatas", df.duplicated().sum())
    
    # Mostrar primeiras linhas
    st.subheader("📊 Primeiras 10 Linhas dos Dados")
    st.dataframe(df.head(10))
    
    # Botão para adicionar visão geral ao relatório
    if st.button("📌 Adicionar Visão Geral ao Relatório", key="add_overview"):
        overview_content = f"""
**Visão Geral do Dataset:**
- Número de linhas: {df.shape[0]:,}
- Número de colunas: {df.shape[1]}
- Valores ausentes: {df.isnull().sum().sum()}
- Registros duplicados: {df.duplicated().sum()}
- Colunas: {', '.join(df.columns.tolist())}
        """
        
        item_para_adicionar = {
            "type": "eda",
            "category": "visao_geral", 
            "title": "Visão Geral do Dataset",
            "content": overview_content
        }
        
        if item_para_adicionar not in st.session_state.report_items:
            st.session_state.report_items.append(item_para_adicionar)
            st.success("✅ Visão geral adicionada ao relatório!")
            st.rerun()
        else:
            st.warning("⚠️ Este item já foi adicionado ao relatório.")
    
    # Seção 2: Tipos de Dados
    st.subheader("🔧 Tipos de Dados")
    
    # Análise dos tipos de dados
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Variáveis Numéricas:**")
        if numeric_cols:
            for col in numeric_cols:
                st.write(f"• {col} ({df[col].dtype})")
        else:
            st.write("Nenhuma variável numérica encontrada")
            
        st.write("**Variáveis de Data/Hora:**")
        if datetime_cols:
            for col in datetime_cols:
                st.write(f"• {col} ({df[col].dtype})")
        else:
            st.write("Nenhuma variável de data/hora encontrada")
    
    with col2:
        st.write("**Variáveis Categóricas:**")
        if categorical_cols:
            for col in categorical_cols:
                unique_values = df[col].nunique()
                st.write(f"• {col} ({unique_values} valores únicos)")
        else:
            st.write("Nenhuma variável categórica encontrada")
    
    # Tabela detalhada de tipos
    st.subheader("📝 Detalhes dos Tipos de Dados")
    tipos_df = pd.DataFrame({
        'Coluna': df.columns,
        'Tipo': df.dtypes,
        'Valores Únicos': df.nunique(),
        'Valores Ausentes': df.isnull().sum(),
        'Porcentagem Ausentes (%)': (df.isnull().sum() / len(df) * 100).round(2)
    })
    st.dataframe(tipos_df)
    
    # Seção 3: Análise de Variáveis Numéricas
    if numeric_cols:
        st.subheader("📈 Análise de Variáveis Numéricas")
        
        # Estatísticas descritivas
        st.write("**Estatísticas Descritivas:**")
        desc_stats = df[numeric_cols].describe()
        st.dataframe(desc_stats)
        
        # Botão para adicionar estatísticas ao relatório
        if st.button("📌 Adicionar Estatísticas Descritivas ao Relatório", key="add_desc_stats"):
            stats_content = f"""
**Estatísticas Descritivas das Variáveis Numéricas:**

{desc_stats.to_string()}

**Observações:**
- {len(numeric_cols)} variáveis numéricas analisadas
- Variáveis: {', '.join(numeric_cols)}
            """
            
            item_para_adicionar = {
                "type": "eda",
                "category": "estatisticas_descritivas",
                "title": "Estatísticas Descritivas",
                "content": stats_content
            }
            
            if item_para_adicionar not in st.session_state.report_items:
                st.session_state.report_items.append(item_para_adicionar)
                st.success("✅ Estatísticas descritivas adicionadas ao relatório!")
                st.rerun()
            else:
                st.warning("⚠️ Este item já foi adicionado ao relatório.")
        
        # Medidas adicionais
        st.write("**Medidas Adicionais de Tendência Central e Variabilidade:**")
        
        additional_stats = pd.DataFrame(index=numeric_cols)
        additional_stats['Variância'] = df[numeric_cols].var()
        additional_stats['Desvio Padrão'] = df[numeric_cols].std()
        additional_stats['Coef. Variação (%)'] = (df[numeric_cols].std() / df[numeric_cols].mean() * 100).round(2)
        additional_stats['Assimetria'] = df[numeric_cols].skew()
        additional_stats['Curtose'] = df[numeric_cols].kurtosis()
        additional_stats['Amplitude'] = df[numeric_cols].max() - df[numeric_cols].min()
        
        st.dataframe(additional_stats)
        
        # Seletor de variável para análise detalhada
        st.write("**Análise Detalhada por Variável:**")
        selected_numeric = st.selectbox("Selecione uma variável numérica para análise detalhada:", numeric_cols)
        
        if selected_numeric:
            col1, col2 = st.columns(2)
            
            with col1:
                # Histograma
                fig_hist = px.histogram(
                    df, 
                    x=selected_numeric, 
                    nbins=30,
                    title=f"Distribuição de {selected_numeric}",
                    template="plotly_white"
                )
                fig_hist.update_layout(
                    xaxis_title=selected_numeric,
                    yaxis_title="Frequência",
                    showlegend=False
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Box plot
                fig_box = px.box(
                    df, 
                    y=selected_numeric,
                    title=f"Box Plot de {selected_numeric}",
                    template="plotly_white"
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            with col2:
                # Estatísticas da variável selecionada
                col_data = df[selected_numeric].dropna()
                
                st.write(f"**Estatísticas de {selected_numeric}:**")
                st.write(f"• **Média:** {col_data.mean():.3f}")
                st.write(f"• **Mediana:** {col_data.median():.3f}")
                st.write(f"• **Moda:** {col_data.mode().iloc[0] if not col_data.mode().empty else 'N/A'}")
                st.write(f"• **Desvio Padrão:** {col_data.std():.3f}")
                st.write(f"• **Variância:** {col_data.var():.3f}")
                st.write(f"• **Mínimo:** {col_data.min():.3f}")
                st.write(f"• **Máximo:** {col_data.max():.3f}")
                st.write(f"• **Amplitude:** {(col_data.max() - col_data.min()):.3f}")
                st.write(f"• **Assimetria:** {col_data.skew():.3f}")
                st.write(f"• **Curtose:** {col_data.kurtosis():.3f}")
                
                # Quartis
                st.write("**Quartis:**")
                st.write(f"• **Q1 (25%):** {col_data.quantile(0.25):.3f}")
                st.write(f"• **Q2 (50% - Mediana):** {col_data.quantile(0.50):.3f}")
                st.write(f"• **Q3 (75%):** {col_data.quantile(0.75):.3f}")
                st.write(f"• **IQR:** {(col_data.quantile(0.75) - col_data.quantile(0.25)):.3f}")
                
                # Botão para adicionar análise da variável ao relatório
                if st.button(f"📌 Adicionar Análise de {selected_numeric} ao Relatório", key=f"add_var_analysis_{selected_numeric}"):
                    var_analysis_content = f"""
**Análise Detalhada da Variável: {selected_numeric}**

**Estatísticas Principais:**
- Média: {col_data.mean():.3f}
- Mediana: {col_data.median():.3f}
- Desvio Padrão: {col_data.std():.3f}
- Mínimo: {col_data.min():.3f}
- Máximo: {col_data.max():.3f}
- Amplitude: {(col_data.max() - col_data.min()):.3f}
- Assimetria: {col_data.skew():.3f}
- Curtose: {col_data.kurtosis():.3f}

**Quartis:**
- Q1 (25%): {col_data.quantile(0.25):.3f}
- Q2 (Mediana): {col_data.quantile(0.50):.3f}  
- Q3 (75%): {col_data.quantile(0.75):.3f}
- IQR: {(col_data.quantile(0.75) - col_data.quantile(0.25)):.3f}
                    """
                    
                    item_para_adicionar = {
                        "type": "eda",
                        "category": "analise_variavel",
                        "title": f"Análise Detalhada: {selected_numeric}",
                        "content": var_analysis_content
                    }
                    
                    if item_para_adicionar not in st.session_state.report_items:
                        st.session_state.report_items.append(item_para_adicionar)
                        st.success(f"✅ Análise de {selected_numeric} adicionada ao relatório!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Esta análise já foi adicionada ao relatório.")
        
        # Matriz de correlação
        if len(numeric_cols) > 1:
            st.write("**Matriz de Correlação:**")
            corr_matrix = df[numeric_cols].corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Matriz de Correlação entre Variáveis Numéricas",
                template="plotly_white",
                color_continuous_scale="RdBu"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Botão para adicionar matriz de correlação ao relatório
            if st.button("📌 Adicionar Matriz de Correlação ao Relatório", key="add_correlation"):
                # Encontrar as correlações mais altas
                corr_pairs = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        corr_val = corr_matrix.iloc[i, j]
                        corr_pairs.append((numeric_cols[i], numeric_cols[j], corr_val))
                
                # Ordenar por valor absoluto da correlação
                corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                
                correlation_content = f"""
**Análise de Correlação entre Variáveis Numéricas**

**Correlações mais significativas (top 5):**
"""
                for i, (var1, var2, corr_val) in enumerate(corr_pairs[:5], 1):
                    correlation_content += f"\n{i}. **{var1}** ↔ **{var2}**: {corr_val:.3f}"
                
                correlation_content += f"""

**Observações:**
- Correlação próxima de +1: Correlação positiva forte
- Correlação próxima de -1: Correlação negativa forte  
- Correlação próxima de 0: Sem correlação linear
- Total de {len(numeric_cols)} variáveis numéricas analisadas
                """
                
                item_para_adicionar = {
                    "type": "eda",
                    "category": "correlacao",
                    "title": "Análise de Correlação",
                    "content": correlation_content
                }
                
                if item_para_adicionar not in st.session_state.report_items:
                    st.session_state.report_items.append(item_para_adicionar)
                    st.success("✅ Análise de correlação adicionada ao relatório!")
                    st.rerun()
                else:
                    st.warning("⚠️ Esta análise já foi adicionada ao relatório.")
    
    # Seção 4: Análise de Variáveis Categóricas
    if categorical_cols:
        st.subheader("📊 Análise de Variáveis Categóricas")
        
        selected_categorical = st.selectbox("Selecione uma variável categórica para análise:", categorical_cols)
        
        if selected_categorical:
            col1, col2 = st.columns(2)
            
            with col1:
                # Contagem de valores
                value_counts = df[selected_categorical].value_counts()
                
                # Gráfico de barras
                fig_bar = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Frequência de {selected_categorical}",
                    template="plotly_white"
                )
                fig_bar.update_layout(
                    xaxis_title=selected_categorical,
                    yaxis_title="Frequência"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Gráfico de pizza
                fig_pie = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=f"Distribuição de {selected_categorical}",
                    template="plotly_white"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Tabela de frequências
            st.write(f"**Tabela de Frequências - {selected_categorical}:**")
            freq_table = pd.DataFrame({
                'Valor': value_counts.index,
                'Frequência': value_counts.values,
                'Porcentagem (%)': (value_counts.values / value_counts.sum() * 100).round(2)
            })
            st.dataframe(freq_table)
    
    # Seção 5: Análise de Valores Ausentes
    st.subheader("🕳️ Análise de Valores Ausentes")
    
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    
    if missing_data.sum() > 0:
        missing_df = pd.DataFrame({
            'Coluna': missing_data.index,
            'Valores Ausentes': missing_data.values,
            'Porcentagem (%)': missing_percent.values.round(2)
        })
        missing_df = missing_df[missing_df['Valores Ausentes'] > 0].sort_values('Valores Ausentes', ascending=False)
        
        if not missing_df.empty:
            # Gráfico de valores ausentes
            fig_missing = px.bar(
                missing_df,
                x='Coluna',
                y='Valores Ausentes',
                title="Valores Ausentes por Coluna",
                template="plotly_white"
            )
            st.plotly_chart(fig_missing, use_container_width=True)
            
            # Tabela de valores ausentes
            st.dataframe(missing_df)
        else:
            st.success("🎉 Não há valores ausentes no dataset!")
    else:
        st.success("🎉 Não há valores ausentes no dataset!")
    
    # Seção 6: Análise de Outliers
    if numeric_cols:
        st.subheader("🎯 Análise de Outliers")
        
        selected_outlier_col = st.selectbox("Selecione uma variável para análise de outliers:", numeric_cols, key="outlier_analysis")
        
        if selected_outlier_col:
            col_data = df[selected_outlier_col].dropna()
            
            # Cálculo de outliers usando IQR
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Número de Outliers", len(outliers))
                st.metric("Porcentagem de Outliers (%)", f"{(len(outliers)/len(col_data)*100):.2f}%")
                st.write(f"**Limites para Outliers:**")
                st.write(f"• Limite Inferior: {lower_bound:.3f}")
                st.write(f"• Limite Superior: {upper_bound:.3f}")
            
            with col2:
                if len(outliers) > 0:
                    st.write("**Valores dos Outliers:**")
                    outlier_df = pd.DataFrame({
                        'Índice': outliers.index,
                        'Valor': outliers.values
                    })
                    st.dataframe(outlier_df.head(10))  # Mostrar apenas os primeiros 10
                    if len(outliers) > 10:
                        st.write(f"... e mais {len(outliers) - 10} outliers")
    
    # Seção 7: Resumo Final
    st.subheader("📋 Resumo da Análise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Características do Dataset:**")
        st.write(f"• Total de registros: {df.shape[0]:,}")
        st.write(f"• Total de variáveis: {df.shape[1]}")
        st.write(f"• Variáveis numéricas: {len(numeric_cols)}")
        st.write(f"• Variáveis categóricas: {len(categorical_cols)}")
        st.write(f"• Variáveis de data/hora: {len(datetime_cols)}")
        
    with col2:
        st.write("**Qualidade dos Dados:**")
        completude = (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        st.write(f"• Completude: {completude:.1f}%")
        st.write(f"• Registros duplicados: {df.duplicated().sum():,}")
        st.write(f"• Valores únicos totais: {df.nunique().sum():,}")
        
        if numeric_cols:
            avg_skewness = abs(df[numeric_cols].skew()).mean()
            if avg_skewness < 0.5:
                skew_desc = "Baixa"
            elif avg_skewness < 1:
                skew_desc = "Moderada"
            else:
                skew_desc = "Alta"
            st.write(f"• Assimetria média: {skew_desc} ({avg_skewness:.2f})")
    
    # Seção 8: Recomendações
    st.subheader("💡 Recomendações")
    
    recomendacoes = []
    
    # Verificar valores ausentes
    if df.isnull().sum().sum() > 0:
        missing_percent_total = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_percent_total > 5:
            recomendacoes.append("🔴 Alto percentual de valores ausentes detectado. Considere estratégias de imputação ou remoção.")
        else:
            recomendacoes.append("🟡 Alguns valores ausentes detectados. Avalie a necessidade de tratamento.")
    else:
        recomendacoes.append("🟢 Excelente! Nenhum valor ausente encontrado.")
    
    # Verificar duplicatas
    if df.duplicated().sum() > 0:
        recomendacoes.append("🔴 Registros duplicados encontrados. Considere removê-los para evitar viés na análise.")
    else:
        recomendacoes.append("🟢 Nenhum registro duplicado encontrado.")
    
    # Verificar assimetria
    if numeric_cols:
        high_skew_cols = [col for col in numeric_cols if abs(df[col].skew()) > 2]
        if high_skew_cols:
            recomendacoes.append(f"🟡 Variáveis com alta assimetria detectadas: {', '.join(high_skew_cols)}. Considere transformações (log, sqrt).")
    
    # Verificar variabilidade
    if numeric_cols:
        high_cv_cols = []
        for col in numeric_cols:
            if df[col].mean() != 0:
                cv = (df[col].std() / df[col].mean()) * 100
                if cv > 100:
                    high_cv_cols.append(col)
        if high_cv_cols:
            recomendacoes.append(f"🟡 Alta variabilidade detectada em: {', '.join(high_cv_cols)}. Considere normalização.")
    
    for rec in recomendacoes:
        st.write(rec)
