# 🏫 Talita School — Gestão Escolar & Analytics (ETL & Dashboard)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)

Uma solução completa e integrada de **Gestão Escolar & Analytics**. O projeto abrange desde a modelagem multidimensional de dados (Star Schema/Snowflake) até a disponibilização de um **Dashboard Executivo Interativo** para tomada de decisão em instituições de ensino.

---

## 🔗 Aplicação em Produção

O dashboard do projeto está implantado e rodando ao vivo via **Streamlit Cloud**:

👉 **[Acessar Painel Interativo — Talita School](https://projeto-escola-talita-etl-mayytqx3zjwrave3wjtlkf.streamlit.app/)**

---

## 📌 Visão Geral do Projeto

O sistema foi built para simular o ecossistema de dados de uma rede/escola de ensino fundamental e médio. Ele consolida informações sobre **~500 estudantes**, corpo docente, turmas e registros acadêmicos diários, oferecendo visões estratégicas para gestores, coordenadores e equipes de RH.

### 🌟 Principais Funcionalidades

- **🎓 Visão Acadêmica**: Monitoramento do total de alunos matriculados, média geral de notas por disciplina e métricas de frequência.
- **👥 RH & Corpo Docente**: Indicadores financeiros de pessoal, folha de pagamento total, salário médio e distribuição de colaboradores por cargo.
- **⚠️ Central de Alertas Preditivos**: Identificação automática em tempo real de estudantes em **situação de risco de reprovação** (critérios: Nota média < 6.0 ou Frequência < 75%).
- **🎯 Filtros Globais**: Filtragem dinâmica de todo o dashboard por **Turno** (Manhã, Tarde, Noite) e por **Série** (8º e 9º EF, 1º ao 3º EM).
- **📥 Exportação de Dados**: Download direto em formato `.csv` de relatórios compilados da lista de risco acadêmico e do quadro corporativo de RH.

---

## 🏗️ Arquitetura de Dados (Modelagem ETL)

O projeto utiliza um banco de dados **SQLite3** estruturado em um modelo multidimensional com tabelas **Dimensão** e **Fato**:
┌───────────────────────┐
              │      dim_alunos       │
              ├───────────────────────┤
              │ id_aluno (PK)         │
              │ nome_aluno            │
              └───────────┬───────────┘
                          │
                          │
┌──────────────────┐  ┌─────┴───────────────┐  ┌───────────────────┐
│    dim_turmas    │  │   fato_matriculas   │  │    fato_boletim   │
├──────────────────┤  ├─────────────────────┤  ├───────────────────┤
│ id_turma (PK)    ├──┼─> id_turma (FK)     │  │ id_boletim (PK)   │
│ serie            │  │ id_aluno (FK)       │  │ id_matricula (FK) ◄┐
│ turno            │  │ id_matricula (PK)   ├──┼───────────────────┘│
└──────────────────┘  └─────────────────────┘  │ disciplina        │
│ nota              │
┌──────────────────────────────────────────┐   │ frequencia        │
│             dim_funcionarios             │   └───────────────────┘
├──────────────────────────────────────────┤
│ id_funcionario (PK)                      │
│ nome | cargo | salario | turno           │
└──────────────────────────────────────────┘


---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3
- **Banco de Dados**: SQLite3
- **Manipulação de Dados**: Pandas
- **Visualização de Dados**: Plotly Express
- **Interface Web**: Streamlit
- **Deploy**: Streamlit Cloud & GitHub

---

## 📂 Estrutura do Repositório

```text
.
├── app.py              # Aplicação principal Streamlit (Engine ETL e Dashboard UI)
├── requirements.txt    # Dependências do projeto Python
├── README.md           # Documentação do projeto
└── talita_school.db    # Banco de dados SQLite (sincronizado automaticamente)
🚀 Como Executar o Projeto Localmente
Pré-requisitos
Python 3.9 ou superior instalado.

Git instalado.

Passo a Passo
Clone este repositório:

Bash
git clone [https://github.com/jctorres94/projeto-escola-talita-etl.git](https://github.com/jctorres94/projeto-escola-talita-etl.git)
cd projeto-escola-talita-etl
Crie e ative um ambiente virtual (opcional, mas recomendado):

Bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
Instale as dependências requeridas:

Bash
pip install -r requirements.txt
Execute a aplicação Streamlit:

Bash
streamlit run app.py
O painel abrirá automaticamente no seu navegador em: http://localhost:8501.

📄 Licença
Este projeto é disponibilizado sob a licença MIT.