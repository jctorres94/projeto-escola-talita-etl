# 🏫 Talita School — Gestão Escolar & Analytics (ETL + Streamlit)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)

Unidade de Inteligência e Análise de Dados Educacionais e Operacionais para o **Talita School**. O projeto consiste na estruturação de um pipeline ETL (Extract, Transform, Load) em Python, armazenado em banco de dados SQLite relacional e integrado a um Dashboard Executivo e Preditivo em Streamlit.

---

## 📌 Principais Funcionalidades

### 🎓 1. Visão Acadêmica & Desempenho
* **Métricas Principais (KPIs):** Total de alunos matriculados, média geral de notas e frequência média.
* **Análise por Disciplina:** Gráficos interativos para identificar disciplinas com menor rendimento ou baixa assiduidade.
* **Filtros Globais:** Segmentação instantânea de dados por **Turno** (Manhã, Tarde, Noite) e **Série**.

### 👥 2. Gestão de RH & Corpo Docente
* **Análise da Folha Salarial:** Total investido em salários e cálculo de salário médio da instituição.
* **Métricas de Pessoal:** Distribuição da equipe por cargos e média salarial por função.

### ⚠️ 3. Central de Alertas & Exportação (Analytics)
* **Identificação Automática de Alunos em Risco:** Regra de negócio automatizada que sinaliza alunos com **Nota < 6.0** ou **Frequência < 75%**.
* **Exportação de Dados:** Botões de download em formato CSV para relatórios da Central de Riscos e Folha de RH.

---

## 🛠️ Arquitetura e Modelagem de Dados

O banco de dados armazena os dados no formato **Star Schema** (Esquema Estrela), garantindo performance e escalabilidade nas consultas SQL:

* **Tabelas Dimensão (`dim_*`):**
  * `dim_alunos`: Dados cadastrais dos estudantes.
  * `dim_turmas`: Cadastro de turmas, séries e turnos.
  * `dim_funcionarios`: Dados do corpo docente e administrativos (cargo, turno e salário).
* **Tabelas Fato (`fato_*`):**
  * `fato_matriculas`: Vínculo entre alunos e turmas.
  * `fato_boletim`: Registros contínuos de notas, faltas e frequências.

---

## 📁 Estrutura do Repositório

```text
├── app.py              # Aplicação principal e Dashboard em Streamlit
├── main.py             # Script ETL (Geração de dados sintéticos e carga no SQLite)
├── talita_school.db    # Banco de dados relacional SQLite
├── requirements.txt    # Dependências do projeto Python
└── README.md           # Documentação do projeto