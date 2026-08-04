import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Talita School - Gestão Escolar & Analytics",
    page_icon="🏫",
    layout="wide"
)

# --- CONEXÃO E CARREGAMENTO DOS DADOS ---
@st.cache_data
def carregar_dados():
    conn = sqlite3.connect("talita_school.db")
    
    df_alunos = pd.read_sql_query("SELECT * FROM dim_alunos", conn)
    df_turmas = pd.read_sql_query("SELECT * FROM dim_turmas", conn)
    df_funcionarios = pd.read_sql_query("SELECT * FROM dim_funcionarios", conn)
    df_matriculas = pd.read_sql_query("SELECT * FROM fato_matriculas", conn)
    df_boletim = pd.read_sql_query("SELECT * FROM fato_boletim", conn)
    
    conn.close()
    return df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim

# Carregar datasets
df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim = carregar_dados()

# --- MENU LATERAL: LOGO E FILTROS GLOBAIS ---
st.sidebar.image("https://img.icons8.com/illustrations/100/school.png", width=90)
st.sidebar.title("🏫 Talita School")
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros Globais")

# Filtro por Turno
turnos_disponiveis = ["Todos"] + list(df_turmas['turno'].dropna().unique())
turno_selecionado = st.sidebar.selectbox("Filtrar por Turno:", turnos_disponiveis)

# Filtro por Série
series_disponiveis = ["Todas"] + list(df_turmas['serie'].dropna().unique())
serie_selecionada = st.sidebar.selectbox("Filtrar por Série:", series_disponiveis)

# --- APLICANDO FILTROS DADOS ACADÊMICOS ---
df_turmas_filtradas = df_turmas.copy()
if turno_selecionado != "Todos":
    df_turmas_filtradas = df_turmas_filtradas[df_turmas_filtradas['turno'] == turno_selecionado]
if serie_selecionada != "Todas":
    df_turmas_filtradas = df_turmas_filtradas[df_turmas_filtradas['serie'] == serie_selecionada]

# Cruzando tabelas para manter coerência dos filtros
turmas_ids = df_turmas_filtradas['id_turma'].unique()
df_matriculas_filtradas = df_matriculas[df_matriculas['id_turma'].isin(turmas_ids)]
df_boletim_filtrado = df_boletim[df_boletim['id_matricula'].isin(df_matriculas_filtradas['id_matricula'])]

# --- TÍTULO PRINCIPAL ---
st.title("📊 Painel Integrado de Gestão Escolar & Analytics")
st.caption("Visão estratégica do corpo docente, desempenho estudantil e indicadores institucionais.")
st.markdown("---")

# --- ESTRUTURA EM ABAS ---
tab_academico, tab_rh, tab_alertas = st.tabs([
    "🎓 Visão Acadêmica", 
    "👥 RH & Corpo Docente", 
    "⚠️ Central de Alertas & Exportação"
])

# ==========================================
# ABA 1: VISÃO ACADÊMICA
# ==========================================
with tab_academico:
    st.subheader("📌 Indicadores Desempenho Geral")
    
    # Cálculos de KPIs
    total_alunos = df_matriculas_filtradas['id_aluno'].nunique()
    media_nota = df_boletim_filtrado['nota'].mean() if not df_boletim_filtrado.empty else 0
    media_frequencia = df_boletim_filtrado['frequencia'].mean() if not df_boletim_filtrado.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos Matriculados", total_alunos)
    col2.metric("Média Geral de Notas", f"{media_nota:.2f}")
    col3.metric("Frequência Média Geral", f"{media_frequencia:.1f}%")
    
    st.markdown("---")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("📚 Distribuição de Notas por Disciplina")
        if not df_boletim_filtrado.empty:
            media_por_materia = df_boletim_filtrado.groupby('disciplina')['nota'].mean().reset_index()
            fig_notas = px.bar(
                media_por_materia, 
                x='disciplina', 
                y='nota', 
                labels={'disciplina': 'Disciplina', 'nota': 'Média das Notas'},
                text_auto='.1f',
                color_discrete_sequence=['#1f77b4']
            )
            fig_notas.update_yaxes(range=[0, 10])
            st.plotly_chart(fig_notas, use_container_width=True)
        else:
            st.warning("Nenhum dado de nota para os filtros selecionados.")
            
    with col_graf2:
        st.subheader("🗓️ Média de Frequência por Disciplina")
        if not df_boletim_filtrado.empty:
            freq_por_materia = df_boletim_filtrado.groupby('disciplina')['frequencia'].mean().reset_index()
            fig_freq = px.line(
                freq_por_materia, 
                x='disciplina', 
                y='frequencia', 
                markers=True,
                labels={'disciplina': 'Disciplina', 'frequencia': 'Frequência (%)'},
                color_discrete_sequence=['#2ca02c']
            )
            fig_freq.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.warning("Nenhum dado de frequência para os filtros selecionados.")

# ==========================================
# ABA 2: RH & CORPO DOCENTE
# ==========================================
with tab_rh:
    st.subheader("💼 Indicadores de Gestão de Pessoas & RH")
    
    # Filtro específico para RH (Turno do funcionário)
    df_rh = df_funcionarios.copy()
    if turno_selecionado != "Todos":
        df_rh = df_rh[df_rh['turno'] == turno_selecionado]

    # KPIs de RH
    total_func = len(df_rh)
    folha_total = df_rh['salario'].sum() if not df_rh.empty else 0
    salario_medio = df_rh['salario'].mean() if not df_rh.empty else 0
    
    col_rh1, col_rh2, col_rh3 = st.columns(3)
    col_rh1.metric("Total de Funcionários", total_func)
    col_rh2.metric("Folha Salarial Mensal", f"R$ {folha_total:,.2f}")
    col_rh3.metric("Salário Médio", f"R$ {salario_medio:,.2f}")
    
    st.markdown("---")
    
    col_rh_g1, col_rh_g2 = st.columns(2)
    
    with col_rh_g1:
        st.subheader("👥 Distribuição por Cargo")
        if not df_rh.empty:
            cargos_count = df_rh['cargo'].value_counts().reset_index()
            cargos_count.columns = ['cargo', 'quantidade']
            fig_cargos = px.pie(
                cargos_count, 
                names='cargo', 
                values='quantidade', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_cargos, use_container_width=True)
        else:
            st.info("Sem dados de funcionários para este turno.")

    with col_rh_g2:
        st.subheader("💰 Média Salarial por Cargo")
        if not df_rh.empty:
            sal_cargo = df_rh.groupby('cargo')['salario'].mean().reset_index()
            fig_sal = px.bar(
                sal_cargo, 
                x='cargo', 
                y='salario',
                labels={'cargo': 'Cargo', 'salario': 'Salário Médio (R$)'},
                text_auto=',.2f',
                color_discrete_sequence=['#ff7f0e']
            )
            st.plotly_chart(fig_sal, use_container_width=True)

# ==========================================
# ABA 3: CENTRAL DE ALERTAS & EXPORTAÇÃO
# ==========================================
with tab_alertas:
    st.subheader("⚠️ Alerta Preditivo: Alunos em Risco de Reprovação")
    st.caption("Critério de Alerta: Nota média inferior a 6.0 OU Frequência inferior a 75%.")
    
    # Cruzamento para identificar alunos em risco
    df_consolidado = df_boletim.merge(df_matriculas, on='id_matricula')
    df_consolidado = df_consolidado.merge(df_alunos, on='id_aluno')
    df_consolidado = df_consolidado.merge(df_turmas, on='id_turma')

    # Filtrar alunos em risco
    df_risco = df_consolidado[
        (df_consolidado['nota'] < 6.0) | (df_consolidado['frequencia'] < 75.0)
    ][['nome_aluno', 'serie', 'turno', 'disciplina', 'nota', 'frequencia']]
    
    if not df_risco.empty:
        st.error(f"🚨 Atualmente existem **{len(df_risco)} ocorrências** de alunos com notas baixas ou baixa frequência.")
        st.dataframe(df_risco, use_container_width=True)
    else:
        st.success("🎉 Nenhum aluno identificado em situação de risco para os parâmetros atuais!")

    st.markdown("---")
    st.subheader("📥 Exportação de Dados e Relatórios")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.markdown("**Baixar Relatório de Alunos em Risco (CSV)**")
        csv_risco = df_risco.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Baixar Lista de Risco em CSV",
            data=csv_risco,
            file_name="alunos_em_risco_talita_school.csv",
            mime="text/csv"
        )
        
    with col_exp2:
        st.markdown("**Baixar Folha do Corpo Docente/RH (CSV)**")
        csv_rh = df_funcionarios.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💼 Baixar Relatório do RH em CSV",
            data=csv_rh,
            file_name="quadro_funcionarios_talita_school.csv",
            mime="text/csv"
        )