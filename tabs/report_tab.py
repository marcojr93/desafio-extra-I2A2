import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def generate_report_content(df, report_items):
    """
    Gera o conteúdo completo do relatório em markdown
    """
    report_lines = []
    
    # Cabeçalho do relatório
    report_lines.append("# 📊 Relatório de Análise de Dados")
    report_lines.append(f"**Data de Geração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report_lines.append(f"**Dataset:** {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    report_lines.append("\n---\n")
    
    # Informações básicas do dataset
    report_lines.append("## 📈 Informações Básicas do Dataset")
    report_lines.append(f"- **Total de registros:** {df.shape[0]:,}")
    report_lines.append(f"- **Total de colunas:** {df.shape[1]}")
    report_lines.append(f"- **Colunas:** {', '.join(df.columns.tolist())}")
    
    # Tipos de dados
    report_lines.append("\n### 🔍 Tipos de Dados")
    for col, dtype in df.dtypes.items():
        report_lines.append(f"- **{col}:** {dtype}")
    
    # Estatísticas básicas para colunas numéricas
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        report_lines.append("\n### 📊 Estatísticas Descritivas")
        stats_df = df[numeric_cols].describe()
        report_lines.append("```")
        report_lines.append(stats_df.to_string())
        report_lines.append("```")
    
    report_lines.append("\n---\n")
    
    # Itens adicionados pelo usuário
    if report_items:
        report_lines.append("## 🎯 Análises e Insights")
        
        for i, item in enumerate(report_items, 1):
            report_lines.append(f"\n### {i}. {item.get('title', 'Análise')}")
            
            if item['type'] == 'qa':
                # Item de Q&A do chatbot
                content = item['content']
                report_lines.append(f"**Pergunta:** {content['pergunta']}")
                report_lines.append(f"**Resposta:** {content['resposta']}")
                
            elif item['type'] == 'eda':
                # Item de análise exploratória
                report_lines.append(f"**Categoria:** {item.get('category', 'EDA')}")
                if 'content' in item:
                    if isinstance(item['content'], str):
                        report_lines.append(item['content'])
                    else:
                        report_lines.append(str(item['content']))
            
            report_lines.append("")  # Linha em branco entre itens
    
    else:
        report_lines.append("## 📝 Nenhuma Análise Adicionada")
        report_lines.append("Adicione análises do chatbot ou da EDA para incluí-las no relatório.")
    
    # Rodapé
    report_lines.append("\n---")
    report_lines.append("*Relatório gerado automaticamente pelo EDA Chatbot - Sistema de análise de dados*")
    
    return "\n".join(report_lines)

def generate_pdf_report(df, report_items):
    """
    Gera um relatório em PDF usando ReportLab
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f77b4')
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=15,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    # Conteúdo do PDF
    story = []
    
    # Título
    story.append(Paragraph("📊 Relatório de Análise de Dados", title_style))
    story.append(Spacer(1, 12))
    
    # Informações básicas
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    story.append(Paragraph(f"<b>Data de Geração:</b> {timestamp}", normal_style))
    story.append(Paragraph(f"<b>Dataset:</b> {df.shape[0]:,} linhas × {df.shape[1]} colunas", normal_style))
    story.append(Spacer(1, 20))
    
    # Informações básicas do dataset
    story.append(Paragraph("📈 Informações Básicas do Dataset", heading2_style))
    
    # Tabela com informações básicas
    basic_data = [
        ['Métrica', 'Valor'],
        ['Total de registros', f"{df.shape[0]:,}"],
        ['Total de colunas', str(df.shape[1])],
        ['Valores ausentes', str(df.isnull().sum().sum())],
        ['Registros duplicados', str(df.duplicated().sum())]
    ]
    
    basic_table = Table(basic_data, colWidths=[2.5*inch, 2*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(basic_table)
    story.append(Spacer(1, 20))
    
    # Colunas do dataset
    story.append(Paragraph("🔍 Colunas do Dataset", heading3_style))
    columns_text = ", ".join(df.columns.tolist())
    story.append(Paragraph(f"<b>Colunas ({len(df.columns)}):</b> {columns_text}", normal_style))
    story.append(Spacer(1, 15))
    
    # Tipos de dados - apenas para colunas numéricas (evitar problemas de renderização)
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        story.append(Paragraph("📊 Estatísticas Descritivas (Variáveis Numéricas)", heading3_style))
        
        # Criar tabela de estatísticas resumida
        stats_df = df[numeric_cols].describe()
        
        # Pegar apenas algumas estatísticas principais
        stats_data = [['Coluna', 'Média', 'Mediana', 'Desvio Padrão', 'Min', 'Max']]
        
        for col in numeric_cols[:10]:  # Limitar a 10 colunas para não sobrecarregar
            if col in stats_df.columns:
                stats_data.append([
                    col,
                    f"{stats_df.loc['mean', col]:.2f}",
                    f"{stats_df.loc['50%', col]:.2f}",
                    f"{stats_df.loc['std', col]:.2f}",
                    f"{stats_df.loc['min', col]:.2f}",
                    f"{stats_df.loc['max', col]:.2f}"
                ])
        
        stats_table = Table(stats_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
    
    # Itens adicionados pelo usuário
    if report_items:
        story.append(PageBreak())
        story.append(Paragraph("🎯 Análises e Insights", heading2_style))
        
        for i, item in enumerate(report_items, 1):
            story.append(Paragraph(f"{i}. {item.get('title', 'Análise')}", heading3_style))
            
            if item['type'] == 'qa':
                # Item de Q&A do chatbot
                content = item['content']
                story.append(Paragraph(f"<b>Pergunta:</b> {content['pergunta']}", normal_style))
                story.append(Paragraph(f"<b>Resposta:</b> {content['resposta']}", normal_style))
                
            elif item['type'] == 'eda':
                # Item de análise exploratória
                story.append(Paragraph(f"<b>Categoria:</b> {item.get('category', 'EDA')}", normal_style))
                if 'content' in item:
                    content_text = str(item['content']).replace('\n', '<br/>')
                    story.append(Paragraph(content_text, normal_style))
            
            story.append(Spacer(1, 15))
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(Paragraph("────────────────────────────────────", normal_style))
    story.append(Paragraph("<i>Relatório gerado automaticamente pelo EDA Chatbot - Sistema de Analise de dados</i>", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, 
                                       textColor=colors.HexColor('#7f8c8d'))))
    
    # Construir o PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_download_link(content, filename):
    """
    Cria um link de download para o conteúdo fornecido
    """
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/markdown;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

def render(df):
    """
    Renderiza a aba de Relatórios com funcionalidade de download
    """
    st.header("📊 Relatório de Análise")
    
    # Verificar se há itens no relatório
    if not st.session_state.report_items:
        st.info("📝 **Nenhum item adicionado ao relatório ainda.**")
        st.markdown("""
        **Como adicionar itens ao relatório:**
        1. Vá para a aba **💬 Chatbot** e faça perguntas sobre os dados
        2. Clique no botão **📌 Adicionar ao Relatório** nas respostas interessantes
        3. Vá para a aba **🖥️ Análise Exploratória** e explore os gráficos
        4. Adicione visualizações relevantes ao relatório
        5. Volte aqui para gerar e baixar o relatório completo
        """)
    else:
        st.success(f"✅ **{len(st.session_state.report_items)} itens** adicionados ao relatório")
    
    # Mostrar prévia dos itens
    if st.session_state.report_items:
        with st.expander("👁️ Prévia dos Itens do Relatório", expanded=True):
            for i, item in enumerate(st.session_state.report_items, 1):
                st.markdown(f"**{i}. {item.get('title', 'Item sem título')}**")
                st.caption(f"Tipo: {item.get('type', 'desconhecido')} | Categoria: {item.get('category', 'geral')}")
                
                if item['type'] == 'qa' and 'content' in item:
                    st.info(f"P: {item['content']['pergunta']}")
                    st.success(f"R: {item['content']['resposta'][:100]}...")
                st.divider()
    
    # Seção de geração do relatório
    st.subheader("📄 Gerar Relatório")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Opções de formato
        format_option = st.selectbox(
            "📋 Formato do Relatório:",
            ["Markdown (.md)", "Texto (.txt)", "PDF (.pdf)"]
        )
    
    with col2:
        # Opções de conteúdo
        include_basic_stats = st.checkbox("Incluir estatísticas básicas", value=True)
    
    # Botão para gerar relatório
    if st.button("🔄 Gerar Relatório", type="primary"):
        with st.spinner("Gerando relatório..."):
            # Definir nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_option == "PDF (.pdf)":
                # Gerar PDF
                filename = f"relatorio_eda_{timestamp}.pdf"
                pdf_content = generate_pdf_report(df, st.session_state.report_items)
                
                # Armazenar o conteúdo PDF na sessão
                st.session_state.report_content = pdf_content
                st.session_state.report_filename = filename
                st.session_state.report_format = "pdf"
            else:
                # Gerar conteúdo de texto/markdown
                report_content = generate_report_content(df, st.session_state.report_items)
                
                if format_option == "Markdown (.md)":
                    filename = f"relatorio_eda_{timestamp}.md"
                else:
                    filename = f"relatorio_eda_{timestamp}.txt"
                
                # Armazenar o conteúdo na sessão para download
                st.session_state.report_content = report_content
                st.session_state.report_filename = filename
                st.session_state.report_format = "text"
            
            st.success("✅ Relatório gerado com sucesso!")
    
    # Mostrar prévia e download se o relatório foi gerado
    if hasattr(st.session_state, 'report_content'):
        st.subheader("👁️ Prévia do Relatório")
        
        # Verificar formato do relatório
        report_format = getattr(st.session_state, 'report_format', 'text')
        
        if report_format == "pdf":
            # Para PDF, mostrar informação em vez de conteúdo
            st.info("📄 Relatório PDF gerado com sucesso! Use o botão de download para baixar o arquivo.")
            st.warning("⚠️ A prévia não está disponível para arquivos PDF. Baixe o arquivo para visualizar o conteúdo.")
        else:
            # Mostrar prévia para texto/markdown
            with st.expander("Ver Conteúdo Completo", expanded=False):
                st.markdown(st.session_state.report_content)
        
        # Botão de download
        if report_format == "pdf":
            mime_type = "application/pdf"
        elif st.session_state.report_filename.endswith('.txt'):
            mime_type = "text/plain"
        else:
            mime_type = "text/markdown"
        
        st.download_button(
            label="📥 Baixar Relatório",
            data=st.session_state.report_content,
            file_name=st.session_state.report_filename,
            mime=mime_type,
            type="primary"
        )
        
        # Estatísticas do relatório
        if report_format == "pdf":
            st.caption(f"📊 Relatório PDF pronto para download")
        else:
            lines = len(st.session_state.report_content.split('\n'))
            chars = len(st.session_state.report_content)
            st.caption(f"📊 Relatório: {lines} linhas, {chars} caracteres")

def summarize_findings(df, memory: list) -> str:
    """Gera conclusões automáticas a partir das análises feitas."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    history = "\n".join(memory)
    prompt = f"""
    Você analisou um dataset com {df.shape[0]} linhas e {df.shape[1]} colunas.
    Histórico de análises anteriores: {history}

    Gere um relatorio com os itens selecionados pelo usuario na secao 'Itens para o Relatório na barra lateral',
    Siga as instruções abaixo:
    1. Estruture o relatório com seções claras e títulos descritivos.
    2. SE houver um aquivo .png salvo, não esqueça de incluir o arquivo gerado em seu relatorio final.
    3. Gere conclusoes acionaveis e insights práticos baseados nos dados analisados.
    4. Use linguagem clara e objetiva, evitando jargões técnicos.
    """

    response = model.generate_content(prompt)
    return response.text
