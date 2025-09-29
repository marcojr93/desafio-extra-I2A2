import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Any, Optional
import pandas as pd
import os


def generate_fallback_response(pergunta: str, df: pd.DataFrame) -> Optional[str]:
    """
    Gera respostas diretas para perguntas básicas quando o agente AI falha
    """
    pergunta_lower = pergunta.lower()
    
    try:
        # Perguntas sobre quantidade/contagem
        if any(word in pergunta_lower for word in ['quantas', 'quantidade', 'total', 'número', 'count']):
            if any(word in pergunta_lower for word in ['transações', 'transacoes', 'linhas', 'registros', 'dados']):
                total = len(df)
                return f"O dataset contém **{total:,} transações** no total."
            
            elif 'colunas' in pergunta_lower:
                total_cols = len(df.columns)
                return f"O dataset possui **{total_cols} colunas**: {', '.join(df.columns.tolist())}"
        
        # Perguntas sobre estrutura dos dados
        elif any(word in pergunta_lower for word in ['colunas', 'campos', 'features', 'variáveis']):
            cols = df.columns.tolist()
            return f"**Colunas do dataset ({len(cols)} no total):**\n" + "\n".join([f"- {col}" for col in cols])
            
        # Perguntas sobre shape/formato
        elif any(word in pergunta_lower for word in ['shape', 'formato', 'dimensões', 'tamanho']):
            rows, cols = df.shape
            return f"**Dimensões do dataset:** {rows:,} linhas × {cols} colunas"
            
        # Perguntas sobre tipos de dados
        elif any(word in pergunta_lower for word in ['tipos', 'type', 'dtypes']):
            tipos = df.dtypes.to_dict()
            response = "**Tipos de dados por coluna:**\n"
            for col, tipo in tipos.items():
                response += f"- **{col}**: {tipo}\n"
            return response
            
        # Perguntas sobre estatísticas básicas
        elif any(word in pergunta_lower for word in ['estatísticas', 'describe', 'resumo', 'summary']):
            stats = df.describe()
            return f"**Estatísticas básicas:**\n```\n{stats.to_string()}\n```"
            
        # Se não conseguir responder, retorna None
        return None
        
    except Exception as e:
        return f"⚠️ Erro ao analisar dados: {str(e)}"


class PolishedCallbackHandler(BaseCallbackHandler):
    """Handler personalizado para exibir logs de forma profissional no Streamlit"""
    
    def __init__(self, agent_name: str = "AI Agent"):
        self.agent_name = agent_name
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        pass
        
    def on_tool_end(self, output: str, **kwargs) -> None:
        pass
        
    def on_text(self, text: str, **kwargs) -> None:
        pass


def render(df, google_api_key):
    """
    Renderiza a aba do Agente de Q&A (Perguntas e Respostas).
    """
    st.header("💬 Chatbot - Descubra mais sobre seus dados")
    st.write("Faça perguntas ao chatbot. O processo de raciocínio do agente será exibido no terminal.")

    # Inicializar histórico se não existir
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_items" not in st.session_state:
        st.session_state.report_items = []

    # Formulário para o usuário inserir a pergunta
    with st.form(key="qa_form"):
        pergunta_usuario = st.text_input("Sua pergunta sobre os dados:", key="pergunta_input")
        submitted = st.form_submit_button("Perguntar ao Agente 🤖")

    if submitted and pergunta_usuario:
        if google_api_key:
            with st.spinner("A LLM está processando a resposta... 🧠 (verifique o terminal para o log detalhado)"):
                
                AGENT_PREFIX = """Você é um assistente de análise de dados especializado em datasets CSV.

FORMATO OBRIGATÓRIO - SEMPRE siga esta estrutura:
Thought: [Seu raciocínio sobre como resolver a pergunta]
Action: python_repl_ast
Action Input: [código Python para analisar os dados]

REGRAS IMPORTANTES:
1. NUNCA responda diretamente sem usar código Python
2. SEMPRE use o formato Thought/Action/Action Input
3. Para contar registros use: len(df) ou df.shape[0]
4. Para ver colunas use: df.columns.tolist()
5. Para estatísticas use: df.describe()
6. Seja específico e analise os dados reais do DataFrame
7. Para distribuições ou frequências, use: df[column].value_counts().
8. Nunca invente valores ou colunas — sempre use apenas os dados disponíveis no DataFrame.
9. IMPORTANTE: Se a sua resposta exigir um gráfico, use Matplotlib para gerá-lo. Após criar o gráfico, salve em 'grafico.png'. Exiba no Streamlit com: st.image('grafico.png').
10. Sua função é extrair, interpretar e apresentar insights de forma compreensível.
"""

                try:
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash",
                        google_api_key=google_api_key,
                        temperature=0,
                        convert_system_message_to_human=True
                    )
                    st.success("✅ Modelo Gemini 2.0 Flash inicializado com sucesso!")
                except Exception as e:
                    error_str = str(e)
                    st.warning(f"⚠️ Tentando modelo alternativo... Erro: {error_str[:100]}...")
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-flash-latest",
                            google_api_key=google_api_key,
                            temperature=0,
                            convert_system_message_to_human=True
                        )
                        st.success("✅ Modelo Gemini Flash Latest inicializado com sucesso!")
                    except Exception as e2:
                        error_str2 = str(e2)
                        if "401" in error_str2 or "unauthorized" in error_str2:
                            st.error("❌ **API Key inválida ou expirada**")
                            return
                        elif "429" in error_str2 or "quota" in error_str2.lower():
                            st.error("❌ **Limite de quota excedido**")
                            return
                        else:
                            st.error("❌ **Erro com ambos os modelos**")
                            return

                agent = create_pandas_dataframe_agent(
                    llm, 
                    df, 
                    prefix=AGENT_PREFIX,
                    verbose=True,
                    allow_dangerous_code=True,
                    max_iterations=3,
                    early_stopping_method="generate"
                )
                
                try:
                    handler = PolishedCallbackHandler(agent_name="Detector de Fraudes")
                    resposta = agent.invoke(
                        {"input": pergunta_usuario},
                        config={"callbacks": [handler]}
                    )

                    resposta_text = resposta['output']
                    if any(phrase in resposta_text.lower() for phrase in [
                        "cannot be determined", 
                        "unable to answer", 
                        "not provided",
                        "without access to"
                    ]):
                        resposta_fallback = generate_fallback_response(pergunta_usuario, df)
                        if resposta_fallback:
                            resposta['output'] = resposta_fallback
                            st.info("🔧 **Modo Fallback**: Resposta gerada diretamente dos dados")

                    # Criar registro da conversa
                    nova_conversa = {
                        "pergunta": pergunta_usuario,
                        "resposta": resposta['output']
                    }

                    # Se o gráfico foi salvo como grafico.png, incluir no histórico
                    if os.path.exists("grafico.png"):
                        nova_conversa["grafico"] = "grafico.png"

                    st.session_state.chat_history.insert(0, nova_conversa)
                    st.rerun()

                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ **Erro inesperado**: {error_msg}")
                    with st.expander("🔧 Detalhes Técnicos (para desenvolvedores)"):
                        st.code(error_msg)
        else:
            st.warning("A chave de API do Google é necessária para esta funcionalidade.")

    st.markdown("---")

    # Exibe o histórico de conversas da sessão atual
    if st.session_state.chat_history:
        st.subheader("Histórico da Sessão Atual")
        for i, conversa in enumerate(st.session_state.chat_history):
            with st.container(border=True):
                st.info(f"**Você perguntou:** {conversa['pergunta']}")
                st.success(f"**Resposta do Agente:** {conversa['resposta']}")

                # Exibir gráfico se existir
                if "grafico" in conversa:
                    st.image(conversa["grafico"], caption="📊 Gráfico gerado pelo agente")

                if st.button("📌 Adicionar ao Relatório", key=f"pin_qa_{i}"):
                    item_para_adicionar = {
                        "type": "qa", 
                        "category": "q&a",
                        "title": f"Pergunta: {conversa['pergunta'][:50]}...",
                        "content": conversa
                    }
                    if item_para_adicionar not in st.session_state.report_items:
                        st.session_state.report_items.append(item_para_adicionar)
                        st.success("Adicionado ao relatório! Veja na barra lateral.")
                        st.rerun()
                    else:
                        st.warning("Este item já foi adicionado ao relatório.")
