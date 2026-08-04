import os
import sys

# --- CONEXÃO E CARREGAMENTO DOS DADOS ---
@st.cache_data
def carregar_dados():
    # Verifica se o banco existe e se não está vazio. Se não existir, roda o main.py
    if not os.path.exists("talita_school.db") or os.path.getsize("talita_school.db") == 0:
        os.system(f"{sys.executable} main.py")
    
    conn = sqlite3.connect("talita_school.db")
    
    try:
        df_alunos = pd.read_sql_query("SELECT * FROM dim_alunos", conn)
        df_turmas = pd.read_sql_query("SELECT * FROM dim_turmas", conn)
        df_funcionarios = pd.read_sql_query("SELECT * FROM dim_funcionarios", conn)
        df_matriculas = pd.read_sql_query("SELECT * FROM fato_matriculas", conn)
        df_boletim = pd.read_sql_query("SELECT * FROM fato_boletim", conn)
    except Exception as e:
        # Se falhar a leitura por qualquer motivo, força a reexecução do ETL e tenta novamente
        conn.close()
        os.system(f"{sys.executable} main.py")
        conn = sqlite3.connect("talita_school.db")
        df_alunos = pd.read_sql_query("SELECT * FROM dim_alunos", conn)
        df_turmas = pd.read_sql_query("SELECT * FROM dim_turmas", conn)
        df_funcionarios = pd.read_sql_query("SELECT * FROM dim_funcionarios", conn)
        df_matriculas = pd.read_sql_query("SELECT * FROM fato_matriculas", conn)
        df_boletim = pd.read_sql_query("SELECT * FROM fato_boletim", conn)
    finally:
        conn.close()
        
    return df_alunos, df_turmas, df_funcionarios, df_matriculas, df_boletim