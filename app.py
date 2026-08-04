import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Talita School - Gestão Escolar & Analytics",
    page_icon="🏫",
    layout="wide"
)

# --- RECRIAÇÃO GARANTIDA DO BANCO DE DADOS ---
def inicializar_banco():
    db_file = "talita_school.db"
    
    # Conecta ou cria o arquivo
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Força a criação limpa das tabelas
    cursor.execute("DROP TABLE IF EXISTS dim_alunos;")
    cursor.execute("DROP TABLE IF EXISTS dim_turmas;")
    cursor.execute("DROP TABLE IF EXISTS dim_funcionarios;")
    cursor.execute("DROP TABLE IF EXISTS fato_matriculas;")
    cursor.execute("DROP TABLE IF EXISTS fato_boletim;")
    
    cursor.execute("CREATE TABLE dim_alunos (id_aluno INTEGER PRIMARY KEY, nome_aluno TEXT);")
    cursor.execute("CREATE TABLE dim_turmas (id_turma INTEGER PRIMARY KEY, serie TEXT, turno TEXT);")
    cursor.execute("CREATE TABLE dim_funcionarios (id_funcionario INTEGER PRIMARY KEY, nome TEXT, cargo TEXT, salario REAL, turno TEXT);")
    cursor.execute("CREATE TABLE fato_matriculas (id_matricula INTEGER PRIMARY KEY, id_aluno INTEGER, id_turma INTEGER);")
    cursor.execute("CREATE TABLE fato_boletim (id_boletim INTEGER PRIMARY KEY, id_matricula INTEGER, disciplina TEXT, nota REAL, frequencia REAL);")
    
    # Inserção de dados
    cursor.executemany("INSERT INTO dim_alunos VALUES (?, ?);", [
        (1, "Ana Silva"), (2, "Bruno Costa"), (3, "Carla Souza"),
        (4, "Diego Oliveira"), (5, "Elena Santos"), (6, "Felipe Lima")
    ])
    cursor.executemany("INSERT INTO dim_turmas VALUES (?, ?, ?);", [
        (101, "1º Ano EM", "Manhã"),
        (102, "2º Ano EM", "Tarde"),
        (103, "3º Ano EM", "Manhã")
    ])
    cursor.executemany("INSERT INTO dim_funcionarios VALUES (?, ?, ?, ?, ?);", [
        (1, "Prof. Roberto", "Professor", 4500.0, "Manhã"),
        (2, "Profª. Maria", "Professor", 4800.0, "Tarde"),
        (3, "Carlos Andrade", "Coordenador", 6500.0, "Manhã"),
        (4, "Fernanda Lima", "Secretária", 3200.0, "Tarde")
    ])
    cursor.executemany("INSERT INTO fato_matriculas VALUES (?, ?, ?);", [
        (1001, 1, 101), (1002, 2, 101),
        (1003, 3, 102), (1004, 4, 102),
        (1005, 5, 103), (1006, 6, 103)
    ])
    # Incluindo alunos com notas abaixo de 6.0 e frequências abaixo de 75%
    cursor.executemany("INSERT INTO fato_boletim VALUES (?, ?, ?, ?, ?);", [
        (1, 1001, "Matemática", 8.5, 95.0), (2, 1001, "Português", 7.0, 90.0),
        (3, 1002, "Matemática", 5.0, 70.0), (4, 1002, "Português", 5.5, 78.0), # Bruno Costa em risco
        (5, 1003, "Matemática", 9.0, 98.0), (6, 1003, "Português", 8.5, 95.0),
        (7, 1004, "Matemática", 4.5, 65.0), (8, 1004, "Português", 5.5, 72.0), # Diego Oliveira em risco
        (9, 1005, "Matemática", 7.5, 88.0), (10, 1005, "Português", 8.0, 90.0),
        (11, 1006, "Matemática", 6.0, 85.0), (12, 1006, "Português", 6.5, 80.0)
    ])
    
    conn.commit()
    conn.close()

# Executa o reset do banco na inicialização
inicializar_banco()

# --- CARREGAMENTO DOS DADOS (Sem Cache para Garantir Atualização) ---
def carregar_dados():
    conn = sqlite3.connect("talita_school.db")
    df_alunos = pd.read_sql_query("SELECT * FROM dim_alunos", conn)
    df_turmas = pd.read_sql_query("SELECT * FROM dim_turmas", conn)
    df_funcionarios = pd.read_sql_query("SELECT * FROM dim_funcionarios", conn)
    df_matriculas = pd.read_sql_query("SELECT * FROM fato_matriculas", conn)
    df_boletim = pd.read_sql_query("SELECT * FROM fato_boletim", conn)
    conn.close()
    return df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim

df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim = carregar_dados()

# --- MENU LATERAL: LOGO E FILTROS ---
st.sidebar.image("https://img.icons8.com/illustrations/100/school.png", width=90)
st.sidebar.title("🏫 Talita School")
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros Globais")

turnos_disponiveis = ["Todos"] + list(df_turmas['turno'].dropna().unique()) if 'turno' in df_turmas.columns else ["Todos"]
turno_selecionado = st.sidebar.selectbox("Filtrar por Turno:", turnos_disponiveis)

series_disponiveis = ["Todas"] + list(df_turmas['serie'].dropna().unique()) if 'serie' in df_turmas.columns else ["Todas"]
serie_selecionada = st.sidebar.selectbox("Filtrar por Série:", series_disponiveis)

# --- APLICANDO FILTROS ---
df_turmas_filtradas = df_turmas.copy()
if not df_turmas_filtradas.empty:
    if turno_selecionado != "Todos" and 'turno' in df_turmas_filtradas.columns:
        df_turmas_filtradas = df_turmas_filtradas[df_turmas_filtradas['turno'] == turno_selecionado]
    if serie_selecionada != "Todas" and 'serie' in df_turmas_filtradas.columns:
        df_turmas_filtradas = df_turmas_filtradas[df_turmas_filtradas['serie'] == serie_selecionada]

turmas_ids = df_turmas_filtradas['id_turma'].unique() if 'id_turma' in df_turmas_filtradas.columns else []
df_matriculas_filtradas = df_matriculas[df_matriculas['id_turma'].isin(turmas_ids)] if 'id_turma' in df_matriculas.columns else df_matriculas
df_boletim_filtrado = df_boletim[df_boletim['id_matricula'].isin(df_matriculas_filtradas['id_matricula'])] if 'id_matricula' in df_boletim.columns else df_boletim

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Painel Integrado de Gestão Escolar & Analytics")
st.caption("Visão estratégica do corpo docente, desempenho estudantil e indicadores institucionais.")
st.markdown("---")

tab_academico, tab_rh, tab_alertas = st.tabs([
    "🎓 Visão Acadêmica", 
    "👥 RH & Corpo Docente", 
    "⚠️ Central de Alertas & Exportação"
])

# VISÃO ACADÊMICA
with tab_academico:
    st.subheader("📌 Indicadores Desempenho Geral")
    total_alunos = df_matriculas_filtradas['id_aluno'].nunique() if 'id_aluno' in df_matriculas_filtradas.columns else 0
    media_nota = df_boletim_filtrado['nota'].mean() if 'nota' in df_boletim_filtrado.columns and not df_boletim_filtrado.empty else 0
    media_frequencia = df_boletim_filtrado['frequencia'].mean() if 'frequencia' in df_boletim_filtrado.columns and not df_boletim_filtrado.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos Matriculados", total_alunos)
    col2.metric("Média Geral de Notas", f"{media_nota:.2f}")
    col3.metric("Frequência Média Geral", f"{media_frequencia:.1f}%")
    
    st.markdown("---")
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("📚 Distribuição de Notas por Disciplina")
        if not df_boletim_filtrado.empty and 'disciplina' in df_boletim_filtrado.columns:
            media_por_materia = df_boletim_filtrado.groupby('disciplina')['nota'].mean().reset_index()
            fig_notas = px.bar(media_por_materia, x='disciplina', y='nota', text_auto='.1f', color_discrete_sequence=['#1f77b4'])
            fig_notas.update_yaxes(range=[0, 10])
            st.plotly_chart(fig_notas, use_container_width=True)
        else:
            st.warning("Nenhum dado de nota para exibir.")
            
    with col_graf2:
        st.subheader("🗓️ Média de Frequência por Disciplina")
        if not df_boletim_filtrado.empty and 'disciplina' in df_boletim_filtrado.columns:
            freq_por_materia = df_boletim_filtrado.groupby('disciplina')['frequencia'].mean().reset_index()
            fig_freq = px.line(freq_por_materia, x='disciplina', y='frequencia', markers=True, color_discrete_sequence=['#2ca02c'])
            fig_freq.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.warning("Nenhum dado de frequência para exibir.")

# RH & CORPO DOCENTE
with tab_rh:
    st.subheader("💼 Indicadores de Gestão de Pessoas & RH")
    df_rh = df_funcionarios.copy()
    if not df_rh.empty and turno_selecionado != "Todos" and 'turno' in df_rh.columns:
        df_rh = df_rh[df_rh['turno'] == turno_selecionado]

    total_func = len(df_rh)
    folha_total = df_rh['salario'].sum() if 'salario' in df_rh.columns and not df_rh.empty else 0
    salario_medio = df_rh['salario'].mean() if 'salario' in df_rh.columns and not df_rh.empty else 0
    
    col_rh1, col_rh2, col_rh3 = st.columns(3)
    col_rh1.metric("Total de Funcionários", total_func)
    col_rh2.metric("Folha Salarial Mensal", f"R$ {folha_total:,.2f}")
    col_rh3.metric("Salário Médio", f"R$ {salario_medio:,.2f}")
    
    st.markdown("---")
    col_rh_g1, col_rh_g2 = st.columns(2)
    
    with col_rh_g1:
        st.subheader("👥 Distribuição por Cargo")
        if not df_rh.empty and 'cargo' in df_rh.columns:
            cargos_count = df_rh['cargo'].value_counts().reset_index()
            cargos_count.columns = ['cargo', 'quantidade']
            fig_cargos = px.pie(cargos_count, names='cargo', values='quantidade', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_cargos, use_container_width=True)
        else:
            st.info("Sem dados de funcionários.")

    with col_rh_g2:
        st.subheader("💰 Média Salarial por Cargo")
        if not df_rh.empty and 'cargo' in df_rh.columns and 'salario' in df_rh.columns:
            sal_cargo = df_rh.groupby('cargo')['salario'].mean().reset_index()
            fig_sal = px.bar(sal_cargo, x='cargo', y='salario', text_auto=',.2f', color_discrete_sequence=['#ff7f0e'])
            st.plotly_chart(fig_sal, use_container_width=True)

# CENTRAL DE ALERTAS & EXPORTAÇÃO
with tab_alertas:
    st.subheader("⚠️ Alerta Preditivo: Alunos em Risco de Reprovação")
    st.caption("Critério de Alerta: Nota média inferior a 6.0 OU Frequência inferior a 75%.")
    
    if not df_boletim.empty and not df_matriculas.empty and not df_alunos.empty and not df_turmas.empty:
        df_consolidado = df_boletim.merge(df_matriculas, on='id_matricula', how='inner')
        df_consolidado = df_consolidado.merge(df_alunos, on='id_aluno', how='inner')
        df_consolidado = df_consolidado.merge(df_turmas, on='id_turma', how='inner')

        df_risco = df_consolidado[(df_consolidado['nota'] < 6.0) | (df_consolidado['frequencia'] < 75.0)][['nome_aluno', 'serie', 'turno', 'disciplina', 'nota', 'frequencia']]
    else:
        df_risco = pd.DataFrame()
    
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
        csv_risco = df_risco.to_csv(index=False).encode('utf-8') if not df_risco.empty else b""
        st.download_button("📄 Baixar Lista de Risco em CSV", data=csv_risco, file_name="alunos_em_risco_talita_school.csv", mime="text/csv")
        
    with col_exp2:
        st.markdown("**Baixar Folha do Corpo Docente/RH (CSV)**")
        csv_rh = df_funcionarios.to_csv(index=False).encode('utf-8') if not df_funcionarios.empty else b""
        st.download_button("💼 Baixar Relatório do RH em CSV", data=csv_rh, file_name="quadro_funcionarios_talita_school.csv", mime="text/csv")