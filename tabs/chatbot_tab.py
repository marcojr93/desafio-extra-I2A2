import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Any, List, Optional
import pandas as pd

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
        """Executado quando uma ferramenta começa a ser usada"""
        pass
        
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Executado quando uma ferramenta termina"""
        pass
        
    def on_text(self, text: str, **kwargs) -> None:
        """Executado quando há texto para exibir"""
        pass

def render(df, google_api_key):
    """
    Renderiza a aba do Agente de Q&A (Perguntas e Respostas).
    """
    st.header("💬 Chatbot - Descubra mais sobre seus dados")
    st.write("Faça perguntas ao chatbot. O processo de raciocínio do agente será exibido no terminal.")
    
    # Formulário para o usuário inserir a pergunta
    with st.form(key="qa_form"):
        pergunta_usuario = st.text_input("Sua pergunta sobre os dados:", key="pergunta_input")
        submitted = st.form_submit_button("Perguntar ao Agente 🤖")

    # Lógica executada apenas quando o formulário é enviado com uma pergunta
    if submitted and pergunta_usuario:
        # Verifica se a chave de API foi fornecida
        if google_api_key:
            # Mostra um spinner na interface enquanto o agente trabalha
            with st.spinner("O Gemini está pensando... 🧠 (verifique o terminal para o log detalhado)"):
                
                # Define o prompt de sistema para guiar o agente
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
3. Para contar registros, use: len(df) ou df.shape[0].
4. Para estatísticas descritivas, use: df.describe().
5. Para distribuições ou frequências, use: df[column].value_counts().
6. Nunca invente valores ou colunas — sempre use apenas os dados disponíveis no DataFrame.
7. Sempre explique os resultados de forma clara e objetiva em linguagem natural.
8. Sugira gráficos (histogramas, boxplots, scatterplots) apenas quando forem úteis para embasar a resposta.
9. Adapte sua análise de acordo com o tipo de dado (numérico, categórico, temporal, etc.).
10. Sua função é extrair, interpretar e apresentar insights de forma compreensível para qualquer tipo de dataset CSV.
"""

                # Configurar para usar Google AI Studio com modelos funcionais
                try:
                    # Usar modelo mais recente que sabemos que funciona
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash",  # Modelo mais recente e rápido
                        google_api_key=google_api_key,
                        temperature=0,
                        convert_system_message_to_human=True  # Compatibilidade com AI Studio
                    )
                    
                    st.success("✅ Modelo Gemini 2.0 Flash inicializado com sucesso!")
                    
                except Exception as e:
                    error_str = str(e)
                    st.warning(f"⚠️ Tentando modelo alternativo... Erro: {error_str[:100]}...")
                    
                    # Fallback para o modelo flash-latest se o 2.0-flash não funcionar
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-flash-latest",  # Fallback confiável
                            google_api_key=google_api_key,
                            temperature=0,
                            convert_system_message_to_human=True
                        )
                        st.success("✅ Modelo Gemini Flash Latest inicializado com sucesso!")
                        
                    except Exception as e2:
                        error_str2 = str(e2)
                        
                        # Diagnóstico específico do erro
                        if "401" in error_str2 or "unauthorized" in error_str2:
                            st.error("❌ **API Key inválida ou expirada**")
                            st.info("💡 Gere uma nova API key em: https://aistudio.google.com/app/apikey")
                            return
                            
                        elif "429" in error_str2 or "quota" in error_str2.lower():
                            st.error("❌ **Limite de quota excedido**")
                            st.info("💡 Aguarde alguns minutos ou verifique suas quotas no console")
                            return
                            
                        else:
                            st.error(f"❌ **Erro com ambos os modelos**")
                            st.error(f"Gemini 2.0: {error_str}")
                            st.error(f"Gemini Flash: {error_str2}")
                            return

                # Cria a instância do agente, passando o LLM e o DataFrame
                agent = create_pandas_dataframe_agent(
                    llm, 
                    df, 
                    prefix=AGENT_PREFIX,
                    verbose=True,  # Ativar verbose para debug
                    allow_dangerous_code=True,
                    max_iterations=3,  # Limitar iterações para evitar loops
                    early_stopping_method="generate"  # Parar cedo se necessário
                )
                
                try:
                    # Instancia nosso handler final, dando um nome profissional ao agente
                    handler = PolishedCallbackHandler(agent_name="Detector de Fraudes")

                    # Executa o agente com a pergunta do usuário usando o método mais recente
                    resposta = agent.invoke(
                        {"input": pergunta_usuario},
                        config={"callbacks": [handler]}
                    )

                    # Verificar se a resposta é genérica demais e tentar fallback
                    resposta_text = resposta['output']
                    if any(phrase in resposta_text.lower() for phrase in [
                        "cannot be determined", 
                        "unable to answer", 
                        "not provided",
                        "without access to"
                    ]):
                        # Tentar resposta direta para perguntas básicas
                        resposta_fallback = generate_fallback_response(pergunta_usuario, df)
                        if resposta_fallback:
                            resposta['output'] = resposta_fallback
                            st.info("🔧 **Modo Fallback**: Resposta gerada diretamente dos dados")

                    # Adiciona a conversa ao histórico e atualiza a interface
                    st.session_state.chat_history.insert(0, {"pergunta": pergunta_usuario, "resposta": resposta['output']})
                    st.rerun()

                except Exception as e:
                    error_msg = str(e)
                    
                    # Tratamento específico para erro de parsing - usar fallback
                    if "output parsing error" in error_msg.lower() or "could not parse llm output" in error_msg.lower():
                        st.warning("⚠️ **Problema de formato na resposta do AI**")
                        st.info("🔧 **Tentando resposta alternativa...**")
                        
                        # Tentar resposta direta para perguntas básicas
                        resposta_fallback = generate_fallback_response(pergunta_usuario, df)
                        if resposta_fallback:
                            # Criar resposta simulada
                            resposta_simulada = {"output": resposta_fallback}
                            st.session_state.chat_history.insert(0, {
                                "pergunta": pergunta_usuario, 
                                "resposta": resposta_fallback
                            })
                            st.success("✅ **Resposta gerada com método alternativo!**")
                            st.rerun()
                        else:
                            # Se não conseguir fallback, mostrar erro mas com orientação
                            st.error("❌ **O AI teve dificuldade com o formato da resposta**")
                            st.info("💡 **Tente reformular sua pergunta de forma mais direta, como:**\n- 'Quantos registros tem o dataset?'\n- 'Quais são as colunas?'\n- 'Mostre as estatísticas básicas'")
                            
                    # Tratamento para outros tipos de erro
                    elif "404" in error_msg and "model" in error_msg.lower():
                        st.error("❌ **Erro de Modelo**: O modelo Gemini especificado não está disponível.")
                        st.info("💡 **Possíveis soluções:**\n- Verifique se sua API key é válida\n- Certifique-se de que tem acesso aos modelos Gemini\n- Tente novamente em alguns minutos")
                    elif "401" in error_msg or "unauthorized" in error_msg.lower():
                        st.error("❌ **Erro de Autenticação**: API key inválida ou expirada.")
                        st.info("💡 Verifique sua API key nas configurações.")
                    elif "403" in error_msg or "forbidden" in error_msg.lower():
                        st.error("❌ **Erro de Permissão**: Sem acesso ao modelo ou API.")
                        st.info("💡 Verifique se sua conta tem acesso aos modelos Gemini.")
                    elif "429" in error_msg or "rate limit" in error_msg.lower():
                        st.error("❌ **Limite de Taxa Excedido**: Muitas requisições.")
                        st.info("💡 Aguarde alguns minutos antes de tentar novamente.")
                    else:
                        st.error(f"❌ **Erro inesperado**: {error_msg}")
                    
                    # Mostrar detalhes técnicos em um expander
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
                
                # Botão para adicionar a conversa ao relatório final
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