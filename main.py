import sqlite3
import random
from faker import Faker

fake = Faker('pt_BR')
random.seed(42)

# --- 1. CONEXÃO COM O BANCO SQLite ---
conn = sqlite3.connect("talita_school.db")
cursor = conn.cursor()

# --- 2. CRIAÇÃO DAS TABELAS ---
cursor.executescript('''
DROP TABLE IF EXISTS fact_boletim;
DROP TABLE IF EXISTS fact_matriculas;
DROP TABLE IF EXISTS dim_funcionarios;
DROP TABLE IF EXISTS dim_turmas;
DROP TABLE IF EXISTS dim_alunos;

CREATE TABLE dim_alunos (
    id_aluno INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento DATE NOT NULL,
    nome_pai TEXT NOT NULL,
    nome_mae TEXT NOT NULL,
    telefone_responsavel TEXT NOT NULL
);

CREATE TABLE dim_turmas (
    id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel TEXT NOT NULL,          -- Infantil, Fundamental, Médio, Técnico
    nome_turma TEXT NOT NULL,     -- ex: Maternal, 5º Ano A, 2º Ano Médio, Técnico em Informática
    turno TEXT NOT NULL
);

CREATE TABLE dim_funcionarios (
    id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cargo TEXT NOT NULL,
    setor TEXT NOT NULL,          -- Docente, Coordenação, Secretaria, TI, Apoio/Operacional
    departamento_atendimento TEXT,
    salario REAL NOT NULL
);

CREATE TABLE fact_matriculas (
    id_matricula INTEGER PRIMARY KEY AUTOINCREMENT,
    id_aluno INTEGER,
    id_turma INTEGER,
    ano_letivo INTEGER,
    status TEXT,                 -- Ativo, Evasão, Transferido
    FOREIGN KEY(id_aluno) REFERENCES dim_alunos(id_aluno),
    FOREIGN KEY(id_turma) REFERENCES dim_turmas(id_turma)
);

CREATE TABLE fact_boletim (
    id_boletim INTEGER PRIMARY KEY AUTOINCREMENT,
    id_matricula INTEGER,
    disciplina TEXT NOT NULL,
    nota_b1 REAL,
    nota_b2 REAL,
    nota_b3 REAL,
    nota_b4 REAL,
    frequencia_pct REAL,
    FOREIGN KEY(id_matricula) REFERENCES fact_matriculas(id_matricula)
);
''')

print("✅ Tabelas recriadas com sucesso!")

# --- 3. POPULANDO TURMAS ---
turmas_dados = [
    ("Infantil", "Maternal A", "Manhã"),
    ("Infantil", "Pré-Escola I", "Manhã"),
    ("Fundamental", "3º Ano A", "Manhã"),
    ("Fundamental", "5º Ano B", "Tarde"),
    ("Fundamental", "8º Ano A", "Manhã"),
    ("Médio", "1º Ano Médio A", "Manhã"),
    ("Médio", "2º Ano Médio A", "Manhã"),
    ("Médio", "3º Ano Médio A", "Manhã"),
    ("Técnico", "Técnico em Informática", "Noite"),
    ("Técnico", "Técnico em Enfermagem", "Noite"),
    ("Técnico", "Técnico em Administração", "Noite")
]

cursor.executemany("INSERT INTO dim_turmas (nivel, nome_turma, turno) VALUES (?, ?, ?)", turmas_dados)

# --- 4. POPULANDO CORPODE FUNCIONÁRIOS COMPLETO ---
funcionarios = [
    # Professores
    ("Carlos Eduardo Silva", "Professor de Matemática", "Docente", "Ensino Fundamental/Médio", 5200.00),
    ("Ana Paula Souza", "Professora de Português", "Docente", "Ensino Fundamental/Médio", 5100.00),
    ("Roberto Mendes", "Professor de História", "Docente", "Ensino Médio", 4900.00),
    ("Fernanda Lima", "Professora de Biologia", "Docente", "Ensino Médio", 5000.00),
    ("Juliana Alves", "Professora Educação Infantil", "Docente", "Educação Infantil", 4200.00),
    ("Lucas Pedrosa", "Professor de TI", "Docente", "Ensino Técnico", 5500.00),
    ("Mariana Costa", "Professora de Enfermagem", "Docente", "Ensino Técnico", 5300.00),
    ("Ricardo Oliveira", "Professor de Gestão", "Docente", "Ensino Técnico", 5100.00),
    
    # Coordenadores
    ("Cláudia Regina", "Coordenadora Pedagógica", "Coordenação", "Educação Infantil e Fundamental", 7200.00),
    ("Marcos Vinícius", "Coordenador Pedagógico", "Coordenação", "Ensino Médio e Técnico", 7500.00),
    
    # Secretaria & Adm
    ("Patrícia Barbosa", "Secretária Escolar", "Secretaria", "Atendimento Geral", 3800.00),
    ("Camila Duarte", "Auxiliar de Secretaria", "Secretaria", "Matrículas & Documentos", 2600.00),
    
    # TI & Suporte Técnico
    ("Gabriel Torres", "Analista de Suporte TI", "Tecnologia", "Infraestrutura & Lab", 4200.00),
    ("Felipe Nogueira", "Técnico em Redes", "Tecnologia", "Sistemas & Redes", 3500.00),
    
    # Inspetores & Serviços Gerais
    ("José Antônio", "Inspetor de Alunos", "Apoio/Operacional", "Pátio & Portaria", 2300.00),
    ("Maria das Graças", "Inspetora de Alunos", "Apoio/Operacional", "Pátio & Corredores", 2300.00),
    ("Sonia Maria", "Auxiliar de Serviços Gerais", "Apoio/Operacional", "Higienização & Limpeza", 1950.00),
    ("Raimundo Nonato", "Auxiliar de Serviços Gerais", "Apoio/Operacional", "Manutenção & Limpeza", 1950.00)
]

cursor.executemany('''
    INSERT INTO dim_funcionarios (nome, cargo, setor, departamento_atendimento, salario)
    VALUES (?, ?, ?, ?, ?)
''', funcionarios)

# --- 5. POPULANDO ALUNOS, MATRÍCULAS E BOLETIM ---
def gerar_alunos_e_notas(qtd=200):
    disciplinas_regulares = ["Matemática", "Português", "História", "Geografia", "Ciências"]
    disciplinas_tecnicas = {
        "Técnico em Informática": ["Algoritmos", "Banco de Dados", "Desenvolvimento Web"],
        "Técnico em Enfermagem": ["Anatomia Humana", "Primeiros Socorros", "Farmacologia"],
        "Técnico em Administração": ["Contabilidade", "Marketing Digital", "Gestão Financeira"]
    }

    for _ in range(qtd):
        nome_aluno = fake.name()
        data_nasc = fake.date_of_birth(minimum_age=4, maximum_age=19).strftime("%Y-%m-%d")
        nome_pai = fake.name_male()
        nome_mae = fake.name_female()
        tel = fake.cellphone_number()

        cursor.execute('''
            INSERT INTO dim_alunos (nome, data_nascimento, nome_pai, nome_mae, telefone_responsavel)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome_aluno, data_nasc, nome_pai, nome_mae, tel))
        id_aluno = cursor.lastrowid

        tipo_perfil = random.choices(["REGULAR", "MEDIO_MAIS_TECNICO", "SO_TECNICO"], weights=[0.7, 0.15, 0.15])[0]

        if tipo_perfil in ["REGULAR", "MEDIO_MAIS_TECNICO"]:
            id_turma_reg = random.randint(1, 8)
            cursor.execute('''
                INSERT INTO fact_matriculas (id_aluno, id_turma, ano_letivo, status)
                VALUES (?, ?, 2026, 'Ativo')
            ''', (id_aluno, id_turma_reg))
            id_mat = cursor.lastrowid

            for disc in disciplinas_regulares:
                b1, b2, b3, b4 = [round(random.uniform(4.0, 10.0), 1) for _ in range(4)]
                freq = round(random.uniform(70.0, 100.0), 1)
                cursor.execute('''
                    INSERT INTO fact_boletim (id_matricula, disciplina, nota_b1, nota_b2, nota_b3, nota_b4, frequencia_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (id_mat, disc, b1, b2, b3, b4, freq))

        if tipo_perfil in ["MEDIO_MAIS_TECNICO", "SO_TECNICO"]:
            id_turma_tec = random.randint(9, 11)
            cursor.execute('''
                INSERT INTO fact_matriculas (id_aluno, id_turma, ano_letivo, status)
                VALUES (?, ?, 2026, 'Ativo')
            ''', (id_aluno, id_turma_tec))
            id_mat_tec = cursor.lastrowid

            cursor.execute("SELECT nome_turma FROM dim_turmas WHERE id_turma = ?", (id_turma_tec,))
            nome_tec = cursor.fetchone()[0]

            for disc in disciplinas_tecnicas[nome_tec]:
                b1, b2, b3, b4 = [round(random.uniform(5.0, 10.0), 1) for _ in range(4)]
                freq = round(random.uniform(75.0, 100.0), 1)
                cursor.execute('''
                    INSERT INTO fact_boletim (id_matricula, disciplina, nota_b1, nota_b2, nota_b3, nota_b4, frequencia_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (id_mat_tec, disc, b1, b2, b3, b4, freq))

gerar_alunos_e_notas(200)

conn.commit()
conn.close()
print("🎉 Banco de dados 'talita_school.db' regerado com Suporte aos Funcionários e RH!")