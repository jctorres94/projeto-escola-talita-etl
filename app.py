import os
import random
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

# --- RECRIAÇÃO E POPULAÇÃO MASSIVA DO BANCO DE DADOS (~500 ALUNOS) ---
def inicializar_banco_expandido():
    db_file = "talita_school.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Reinicia a estrutura de tabelas
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
    
    # 1. Gerar Turmas
    series = ["1º Ano EM", "2º Ano EM", "3º Ano EM", "8º Ano EF", "9º Ano EF"]
    turnos = ["Manhã", "Tarde", "Noite"]
    turmas_data = []
    id_turma_counter = 101
    
    for s in series:
        for t in turnos:
            turmas_data.append((id_turma_counter, s, t))
            id_turma_counter += 1
            
    cursor.executemany("INSERT INTO dim_turmas VALUES (?, ?, ?);", turmas_data)
    
    # 2. Gerar ~500 Alunos e Matrículas
    nomes_ex = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Felipe", "Gabriel", "Helena", "Igor", "Julia", "Lucas", "Mariana", "Pedro", "Sofia", "Thiago", "Beatriz", "Rodrigo", "Larissa", "Mateus", "Camila"]
    sobrenomes_ex = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida"]
    
    random.seed(42)  # Semente fixa para manter os dados consistentes
    
    alunos_data = []
    matriculas_data = []
    boletim_data = []
    
    disciplinas = ["Matemática", "Português", "História", "Geografia", "Física", "Química"]
    
    id_matricula_counter = 10001
    id_boletim_counter = 1
    
    for id_aluno in range(1, 501):
        nome_completo = f"{random.choice(nomes_ex)} {random.choice(sobrenomes_ex)} {random.choice(sobrenomes_ex)}"
        alunos_data.append((id_aluno, nome_completo))
        
        # Sorteia uma turma para o aluno
        id_turma_sorteada = random.choice([t[0] for t in turmas_data])
        matriculas_data.append((id_matricula_counter, id_aluno, id_turma_sorteada))
        
        # Gera notas/frequências para cada disciplina do aluno
        for disc in disciplinas:
            # Sorteia valores variados (garantindo que uma parcela fique em risco < 6.0 ou < 75%)
            if random.random() < 0.18:  # ~18% de chance de o aluno estar em risco nesta matéria
                nota = round(random.uniform(2.0, 5.8), 1)
                frequencia = round(random.uniform(50.0, 74.0), 1)
            else:
                nota = round(random.uniform(6.0, 10.0), 1)
                frequencia = round(random.uniform(75.0, 100.0), 1)
                
            boletim_data.append((id_boletim_counter, id_matricula_counter, disc, nota, frequencia))
            id_boletim_counter += 1
            
        id_matricula_counter += 1

    cursor.executemany("INSERT INTO dim_alunos VALUES (?, ?);", alunos_data)
    cursor.executemany("INSERT INTO fato_matriculas VALUES (?, ?, ?);", matriculas_data)
    cursor.executemany("INSERT INTO fato_boletim VALUES (?, ?, ?, ?, ?);", boletim_data)

    # 3. Gerar Funcionários/RH (~30 funcionários)
    cargos_rh = [
        ("Professor", 4500.0), ("Professor", 4800.0), ("Professor", 5200.0),
        ("Coordenador", 6800.0), ("Secretária", 3200.0), ("Diretor", 9500.0),
        ("Inspetor", 2800.0), ("Orientador Educacional", 5500.0)
    ]
    
    funcionarios_data = []
    for id_func in range(1, 31):
        cargo, salario_base = random.choice(cargos_rh)
        nome_func = f"{'Prof. ' if 'Professor' in cargo else ''}{random.choice(nomes_ex)} {random.choice(sobrenomes_ex)}"
        turno_func = random.choice(turnos)
        salario_final = round(salario_base + random.uniform(-300, 500), 2)
        funcionarios_data.append((id_func, nome_func, cargo, salario_final, turno_func))
        
    cursor.executemany("INSERT INTO dim_funcionarios VALUES (?, ?, ?, ?, ?);", funcionarios_data)
    
    conn.commit()
    conn.close()

# Executa e constrói a base massiva
inicializar_banco_expandido()

# --- CARREGAMENTO DOS DADOS ---
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