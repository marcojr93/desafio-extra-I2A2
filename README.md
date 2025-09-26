# 🤖 EDA Chatbot - Análise Exploratória de Dados Inteligente

Uma aplicação Streamlit avançada que combina inteligência artificial com análise exploratória de dados (EDA) para proporcionar insights automatizados e relatórios abrangentes sobre seus datasets.

## 🌟 Características Principais

### 📊 **Análise Exploratória Automática**
- Estatísticas descritivas completas
- Análise de correlação com visualizações
- Detecção de valores ausentes e outliers
- Distribuição de variáveis categóricas e numéricas
- Gráficos interativos com Plotly e Seaborn

### 🤖 **Chatbot Inteligente**
- Integração com Google AI (Gemini)
- Consultas em linguagem natural sobre seus dados
- Sistema de fallback para respostas robustas
- Histórico de conversação persistente

### 📄 **Geração de Relatórios**
- Relatórios em múltiplos formatos: **Markdown**, **Texto** e **PDF**
- Compilação automática de insights das análises
- Sistema de memória para capturar descobertas importantes
- Download direto dos relatórios gerados

## 🛠️ Tecnologias Utilizadas

### Backend & IA
- **Streamlit** - Interface web interativa
- **LangChain** - Framework para aplicações com IA
- **Google Generative AI** - Modelos Gemini para processamento de linguagem natural
- **Pandas** - Manipulação e análise de dados

### Visualização & Análise
- **Plotly** - Gráficos interativos
- **Matplotlib & Seaborn** - Visualizações estatísticas
- **SciPy** - Análise estatística avançada
- **NumPy** - Computação científica

### Relatórios
- **ReportLab** - Geração de PDFs profissionais
- **Tabulate** - Formatação de tabelas

## 📋 Requisitos

```txt
streamlit
pandas
numpy
matplotlib
seaborn
scipy
plotly
python-dotenv
langchain
langchain-google-genai
langchain-experimental
langchain-community
langchain-core
google-generativeai
tabulate
reportlab
```

## 🚀 Instalação

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd EDA-Chatbot
```

### 2. Crie um Ambiente Virtual
```bash
python -m venv .venv
```

### 3. Ative o Ambiente Virtual
**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/MacOS:**
```bash
source .venv/bin/activate
```

### 4. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 5. Configure a API do Google AI
1. Obtenha uma chave API no [Google AI Studio](https://aistudio.google.com/)
2. Crie um arquivo `.env` na raiz do projeto:
```env
GOOGLE_API_KEY=sua_chave_api_aqui
```

### 6. Execute a Aplicação
```bash
streamlit run app.py
```

## 📖 Como Usar

### 1. **Upload do Dataset**
- Acesse a aplicação no navegador
- Faça upload de um arquivo CSV na barra lateral
- A aplicação detecta automaticamente separadores e codificações

### 2. **Navegue pelas Abas**

#### 🤖 **Aba Chatbot**
- Faça perguntas sobre seus dados em linguagem natural
- Exemplos:
  - "Quantas transações temos no total?"
  - "Qual é a média da coluna 'valor'?"
  - "Existem valores ausentes?"
  - "Mostre estatísticas da coluna 'categoria'"

#### 📊 **Aba Análise Exploratória**
- **Visão Geral**: Informações básicas do dataset
- **Estatísticas Descritivas**: Medidas centrais e dispersão
- **Análise de Variáveis**: Distribuições e frequências
- **Correlações**: Matriz de correlação e heatmap
- **Botões "📌 Adicionar ao Relatório"**: Capture insights importantes

#### 📄 **Aba Relatório**
- Visualize todos os insights capturados
- Escolha o formato de saída:
  - **Markdown (.md)** - Para documentação
  - **Texto (.txt)** - Formato simples
  - **PDF (.pdf)** - Relatório profissional
- Gere e baixe relatórios completos

## 🏗️ Arquitetura do Projeto

```
EDA-Chatbot/
├── app.py                 # Aplicação principal Streamlit
├── requirements.txt       # Dependências do projeto
├── README.md             # Documentação do projeto
├── .env                  # Configurações de ambiente
├── creditcard.csv        # Dataset de exemplo
├── tabs/                 # Módulos das abas
│   ├── __init__.py
│   ├── chatbot_tab.py    # Interface do chatbot
│   ├── eda_tab.py        # Análise exploratória
│   └── report_tab.py     # Geração de relatórios
└── .venv/                # Ambiente virtual
```

## 🔧 Funcionalidades Técnicas

### Sistema de Carregamento Robusto
- Detecção automática de separadores CSV (`,`, `;`, `\t`)
- Múltiplas codificações suportadas (`utf-8`, `latin1`, `cp1252`)
- Validação de integridade dos dados
- Tratamento de erros de parsing

### Integração com IA
- Agente pandas especializado para consultas em dados
- Sistema de callback para monitoramento
- Fallback automático para consultas básicas
- Gerenciamento de contexto e histórico

### Geração de PDF Avançada
- Layout profissional A4
- Estilos customizados para diferentes seções
- Formatação de tabelas e estatísticas
- Metadados do documento

## 🎯 Casos de Uso

### 📈 **Análise Financeira**
- Análise de transações de cartão de crédito
- Detecção de padrões de fraude
- Análise de comportamento de clientes

### 📊 **Business Intelligence**
- Relatórios automatizados para stakeholders
- Insights rápidos sobre vendas e marketing
- Análise de performance de produtos

### 🔬 **Pesquisa e Academia**
- Análise exploratória inicial de datasets
- Documentação de descobertas
- Geração de relatórios para publicações

## 🐛 Troubleshooting

### Problema com API Key
```
Se você receber erros de autenticação:
1. Verifique se a chave API está correta no arquivo .env
2. Confirme se a API do Google AI está habilitada
3. Restart a aplicação após alterar o .env
```

### Erro de Encoding
```
Se o CSV não carregar:
1. Tente salvar o arquivo com codificação UTF-8
2. Verifique se o separador está correto
3. Use a opção de "detecção automática" da aplicação
```

### Problemas de Instalação
```bash
# Se houver conflitos de dependências
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📝 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, siga estes passos:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Se você encontrar problemas ou tiver dúvidas:
- Abra uma issue no GitHub
- Entre em contato através do email do projeto
- Consulte a documentação das tecnologias utilizadas

## 🔮 Próximas Funcionalidades

- [ ] Suporte para múltiplos formatos de arquivo (Excel, JSON, Parquet)
- [ ] Análise de séries temporais automatizada
- [ ] Integração com bancos de dados
- [ ] Dashboard personalizado
- [ ] Exportação de gráficos interativos
- [ ] Análise de machine learning automatizada

---

**Desenvolvido por Marco Junior**