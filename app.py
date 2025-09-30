import streamlit as st
import pandas as pd
import io
from typing import Optional, Tuple
# Importa todos os módulos de abas, incluindo a nova de insights
from tabs import chatbot_tab, report_tab, eda_tab

def load_csv_safely(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Carrega CSV de forma segura com validações e tratamento de erros.
    Retorna: (DataFrame ou None, mensagem_de_erro ou None)
    """
    if uploaded_file is None:
        return None, "Nenhum arquivo foi fornecido."
    
    # Resetar o ponteiro do arquivo para o início
    uploaded_file.seek(0)
    
    try:
        # Ler uma amostra do arquivo para validação
        sample = uploaded_file.read(1024).decode('utf-8', errors='ignore')
        uploaded_file.seek(0)  # Resetar novamente
        
        # Verificar se o arquivo está vazio
        if len(sample.strip()) == 0:
            return None, "❌ O arquivo está vazio. Por favor, envie um arquivo CSV com dados."
        
        # Detectar possível separador
        separators = [',', ';', '\t']
        best_separator = ','
        max_columns = 0
        
        for sep in separators:
            try:
                test_df = pd.read_csv(io.StringIO(sample), sep=sep, nrows=5)
                if len(test_df.columns) > max_columns:
                    max_columns = len(test_df.columns)
                    best_separator = sep
            except:
                continue
        
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)
                
                # Tentar ler o arquivo completo
                if encoding == 'utf-8':
                    df = pd.read_csv(uploaded_file, sep=best_separator)
                else:
                    # Para outros encodings, ler como bytes primeiro
                    content = uploaded_file.read()
                    decoded_content = content.decode(encoding)
                    df = pd.read_csv(io.StringIO(decoded_content), sep=best_separator)
                
                # Validações do DataFrame
                if df.empty:
                    return None, "❌ O arquivo não contém dados válidos."
                
                if len(df.columns) == 0:
                    return None, "❌ O arquivo não possui colunas válidas."
                
                # Verificar se há pelo menos uma linha de dados (além do cabeçalho)
                if len(df) == 0:
                    return None, "❌ O arquivo possui cabeçalhos mas nenhuma linha de dados."
                
                # Sucesso!
                return df, None
                
            except UnicodeDecodeError:
                continue
            except pd.errors.EmptyDataError:
                return None, "❌ O arquivo está vazio ou mal formatado. Verifique se é um CSV válido."
            except pd.errors.ParserError as e:
                return None, f"❌ Erro ao analisar o arquivo CSV: {str(e)}"
            except Exception as e:
                continue
        
        return None, "❌ Não foi possível ler o arquivo. Verifique se é um arquivo CSV válido com encoding UTF-8, Latin-1 ou similar."
        
    except Exception as e:
        return None, f"❌ Erro inesperado ao processar o arquivo: {str(e)}"

# Configuração da página
# Configuração da página
st.set_page_config(page_title="Data Inspector", layout="wide")

# Logo centralizada
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=300)
    
st.title("🚀 EDA Chatbot - Plataforma de Análise de Dados")

# --- ESTADO DA SESSÃO ---
# Inicializa as variáveis no estado da sessão para persistirem entre as interações.
if 'report_items' not in st.session_state:
    st.session_state.report_items = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'insights_gerados' not in st.session_state:
    st.session_state.insights_gerados = None

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuração")
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Chave de API do Google carregada!")
    except (FileNotFoundError, KeyError):
        st.error("Chave de API não encontrada. Verifique o arquivo .streamlit/secrets.toml")
        google_api_key = None

    st.markdown("---")
    st.header("📋 Itens para o Relatório")
    if st.session_state.report_items:
        for i, item in enumerate(st.session_state.report_items):
            st.info(f"Item {i+1}: {item['title']}")
        if st.button("Limpar Itens do Relatório"):
            st.session_state.report_items = []
            st.rerun()
    else:
        st.info("Nenhum item adicionado.")

# --- LÓGICA DE UPLOAD E PROCESSAMENTO DO ARQUIVO ---
upload_container = st.container(border=True)
with upload_container:
    uploaded_file = st.file_uploader("Selecione o arquivo CSV com os dados", type=["csv"])

    if uploaded_file is not None:
        if st.session_state.df is None:
            with st.spinner("Processando e analisando os dados..."):
                df, error_msg = load_csv_safely(uploaded_file)
                
                if df is not None:
                    st.session_state.df = df
                    st.success(f"✅ Dados carregados com sucesso! {df.shape[0]} linhas e {df.shape[1]} colunas encontradas.")
                    
                    # Mostrar preview dos dados
                    with st.expander("👁️ Preview dos Dados (primeiras 5 linhas)"):
                        st.dataframe(df.head())
                        
                else:
                    st.error(error_msg)
                    st.session_state.df = None
                    
                    # Dicas para o usuário
                    with st.expander("💡 Dicas para Resolver Problemas com CSV"):
                        st.write("""
                        **Formatos de CSV Suportados:**
                        - Separadores: vírgula (,), ponto e vírgula (;), ou tab
                        - Encoding: UTF-8, Latin-1, CP1252
                        - Deve ter pelo menos uma linha de cabeçalho e uma linha de dados
                        
                        **Problemas Comuns:**
                        - Arquivo vazio ou corrompido
                        - Encoding incorreto (tente salvar como UTF-8)
                        - Separador incorreto (use vírgula ou ponto e vírgula)
                        - Arquivo não é realmente um CSV
                        """)
    elif st.session_state.df is None:
        st.info("Aguardando o upload do arquivo CSV para começar a análise.")

# --- SEÇÃO PRINCIPAL COM EDA INICIALIZADA ---
if uploaded_file and st.session_state.df is not None:
    df = st.session_state.df  # Usar o DataFrame já carregado e validado
    st.session_state["data"] = df

    # Criação das abas principais
    tab_agent, tab_report, tab_dashboard = st.tabs([
        "💬 Chatbot",
        "📊 Relatorio",
        "🖥️ Analise exploratoria"
    ])

    # Renderiza cada aba, passando o DataFrame apropriado para cada uma
    with tab_agent:
        # O Agente Q&A usa o DataFrame original para responder perguntas sobre todos os dados
        chatbot_tab.render(df, google_api_key)

    with tab_report:
        report_tab.render(df)

    with tab_dashboard:
        eda_tab.render(df)
