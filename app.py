import os
import sys
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

# --- GARANTE QUE O BANCO FOI GERADO VIA MAIN.PY ---
def garantir_banco_de_dados():
    # Executa o main.py se o arquivo do banco não existir ou estiver zerado
    if not os.path.exists("talita_school.db") or os.path.getsize("talita_school.db") == 0:
        try:
            import main
            if hasattr(main, 'main'):
                main.main()
        except Exception as e:
            st.error(f"Erro ao executar main.py para inicializar o banco: {e}")

garantir_banco_de_dados()

# --- CONEXÃO E CARREGAMENTO DOS DADOS ---
@st.cache_data
def carregar_dados():
    conn = sqlite3.connect("talita_school.db")
    
    try:
        df_alunos = pd.read_sql_query("SELECT * FROM dim_alunos", conn)
        df_turmas = pd.read_sql_query("SELECT * FROM dim_turmas", conn)
        df_funcionarios = pd.read_sql_query("SELECT * FROM dim_funcionarios", conn)
        df_matriculas = pd.read_sql_query("SELECT * FROM fato_matriculas", conn)
        df_boletim = pd.read_sql_query("SELECT * FROM fato_boletim", conn)
    except Exception as e:
        st.error(f"Erro ao ler tabelas do banco de dados: {e}")
        df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim = (
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )
    finally:
        conn.close()
        
    return df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim

# Carregar datasets
df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim = carregar_dados()

# --- MENU LATERAL: LOGO E FILTROS GLOBAIS ---
st.sidebar.image("https://img.icons8.com/illustrations/100/school.png", width=90)
st.sidebar.title("🏫 Talita School")
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros Globais")

# Filtro por Turno (Verificação de segurança na coluna)
if not df_turmas.empty and 'turno' in df_turmas.columns:
    turnos_disponiveis = ["Todos"] + list(df_turmas['turno'].dropna().unique())
else:
    turnos_disponiveis = ["Todos"]
turno_selecionado = st.sidebar.selectbox("Filtrar por Turno:", turnos_disponiveis)

# Filtro por Série (Verificação de segurança na coluna)
if not df_turmas.empty and 'serie' in df_turmas.columns:
    series_disponiveis = ["Todas"] + list(df_turmas['serie'].dropna().unique())
elif not df_turmas.empty and 'nome_serie' in df_turmas.columns:
    series_disponiveis = ["Todas"] + list(df_turmas['nome_serie'].dropna().unique())
else:
    series_disponiveis = ["Todas"]
serie_selecionada = st.sidebar.selectbox("Filtrar por Série:", series_disponiveis)

# --- APLICANDO FILTROS DADOS ACADÊMICOS ---
df_turmas_filtradas = df_turmas.copy()
if not df_turmas_filtradas.empty:
    if turno_selecionado != "Todos" and 'turno' in df_turmas_filtradas.columns:
        df_turmas_filtradas = df_turmas_filtradas[df_turmas_filtradas['turno'] == turno_selecionado]
    if serie_selecionada != "Todas":
        col_serie = 'serie' if 'serie' in df_turmas_filtradas.columns else ('nome_serie' if 'nome_serie' in df_turmas_filtradas.columns else None)
        if col_serie:
            df_turmas_filtradas = df_turmas_filtradas[df_turmas_filtradas[col_serie] == serie_selecionada]

turmas_ids = df_turmas_filtradas['id_turma'].unique() if not df_turmas_filtradas.empty and 'id_turma' in df_turmas_filtradas.columns else []
df_matriculas_filtradas = df_matriculas[df_matriculas['id_turma'].isin(turmas_ids)] if not df_matriculas.empty and 'id_turma' in df_matriculas.columns else df_matriculas
df_boletim_filtrado = df_boletim[df_boletim['id_matricula'].isin(df_matriculas_filtradas['id_matricula'])] if not df_boletim.empty and 'id_matricula' in df_boletim.columns else df_boletim

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
    
    total_alunos = df_matriculas_filtradas['id_aluno'].nunique() if not df_matriculas_filtradas.empty and 'id_aluno' in df_matriculas_filtradas.columns else 0
    media_nota = df_boletim_filtrado['nota'].mean() if not df_boletim_filtrado.empty and 'nota' in df_boletim_filtrado.columns else 0
    media_frequencia = df_boletim_filtrado['frequencia'].mean() if not df_boletim_filtrado.empty and 'frequencia' in df_boletim_filtrado.columns else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos Matriculados", total_alunos)
    col2.metric("Média Geral de Notas", f"{media_nota:.2f}")
    col3.metric("Frequência Média Geral", f"{media_frequencia:.1f}%")
    
    st.markdown("---")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("📚 Distribuição de Notas por Disciplina")
        if not df_boletim_filtrado.empty and 'disciplina' in df_boletim_filtrado.columns and 'nota' in df_boletim_filtrado.columns:
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
        if not df_boletim_filtrado.empty and 'disciplina' in df_boletim_filtrado.columns and 'frequencia' in df_boletim_filtrado.columns:
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
    
    df_rh = df_funcionarios.copy()
    if not df_rh.empty and turno_selecionado != "Todos" and 'turno' in df_rh.columns:
        df_rh = df_rh[df_rh['turno'] == turno_selecionado]

    total_func = len(df_rh)
    folha_total = df_rh['salario'].sum() if not df_rh.empty and 'salario' in df_rh.columns else 0
    salario_medio = df_rh['salario'].mean() if not df_rh.empty and 'salario' in df_rh.columns else 0
    
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
        if not df_rh.empty and 'cargo' in df_rh.columns and 'salario' in df_rh.columns:
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
    
    if not df_boletim.empty and not df_matriculas.empty and not df_alunos.empty and not df_turmas.empty:
        df_consolidado = df_boletim.merge(df_matriculas, on='id_matricula', how='inner')
        df_consolidado = df_consolidado.merge(df_alunos, on='id_aluno', how='inner')
        df_consolidado = df_consolidado.merge(df_turmas, on='id_turma', how='inner')

        col_serie = 'serie' if 'serie' in df_consolidado.columns else ('nome_serie' if 'nome_serie' in df_consolidado.columns else '')
        cols_exibir = [c for c in ['nome_aluno', col_serie, 'turno', 'disciplina', 'nota', 'frequencia'] if c and c in df_consolidado.columns]

        df_risco = df_consolidado[
            (df_consolidado['nota'] < 6.0) | (df_consolidado['frequencia'] < 75.0)
        ][cols_exibir] if 'nota' in df_consolidado.columns and 'frequencia' in df_consolidado.columns else pd.DataFrame()
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
        st.download_button(
            label="📄 Baixar Lista de Risco em CSV",
            data=csv_risco,
            file_name="alunos_em_risco_talita_school.csv",
            mime="text/csv"
        )
        
    with col_exp2:
        st.markdown("**Baixar Folha do Corpo Docente/RH (CSV)**")
        csv_rh = df_funcionarios.to_csv(index=False).encode('utf-8') if not df_funcionarios.empty else b""
        st.download_button(
            label="💼 Baixar Relatório do RH em CSV",
            data=csv_rh,
            file_name="quadro_funcionarios_talita_school.csv",
            mime="text/csv"
        )