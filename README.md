# Otimização de Quadro de Horários Universitário (UCTP)

Este repositório contém o projeto final da disciplina de Pesquisa Operacional. O objetivo central é solucionar o **Problema de Alocação de Horários Universitários (University Course Timetabling Problem - UCTP)**, um problema clássico de otimização combinatória classificado como NP-Difícil.

Para resolver este problema de alta complexidade computacional, o sistema implementa uma heurística híbrida combinando:
1. **GRASP (Greedy Randomized Adaptive Search Procedure):** Responsável por gerar uma população inicial de alta qualidade.
2. **Algoritmo Genético (AG):** Responsável pela busca evolutiva das melhores grades horárias, minimizando choques de professores e maximizando a alocação eficiente de salas.

## Tecnologias e Arquitetura
O projeto foi desenvolvido com foco absoluto em performance computacional e adoção de boas práticas de Engenharia de Software.

- **Linguagem:** Python 3.13 (Vanilla)
- **Bibliotecas:** Apenas *Standard Library* (`random`, `math`, `csv`, `unittest`), garantindo um sistema autocontido e sem *overhead* de *frameworks* externos.
- **Entrada de Dados:** Arquivos `.csv` modulares.

## Estrutura de Diretórios
A arquitetura do projeto segue inicialmente o padrão de separação de responsabilidades:

```text
university_couse_timetabling_problem/
├── data/                  
│   ├── professores.csv
│   ├── disciplinas.csv
│   └── ...
├── src/                  
│   ├── domain/             
│   ├── fitness/
│   ├── infrastructure/            
│   ├── algorithms/         
│   └── main.py             
├── tests/                  
│   └── test_fitness.py      
├── LICENSE                
└── README.md               
```

## Como Executar

### Pré-requisitos

Certifique-se de ter o Python 3.10 ou superior instalado na sua máquina. Nenhuma instalação via `pip` é necessária.

### Rodando o Algoritmo Principal

Para executar o algoritmo de otimização, navegue até o diretório raiz do projeto no seu terminal e execute:

```bash
python src/main.py

```

### Rodando os Testes Automatizados

Para garantir que as regras matemáticas da função de *fitness* estão corretas e sem regressões, execute a suíte de testes:

```bash
python -m unittest discover -s tests

```

## Autoria

Desenvolvido por **Barbara Carvalho** como requisito avaliativo da disciplina de Pesquisa Operacional.
