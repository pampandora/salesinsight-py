# SalesInsight PY

## Sobre o projeto

**SalesInsight PY** é um projeto de análise de dados de vendas desenvolvido em Python, com foco na aplicação prática dos conceitos estudados no Módulo 01 — Semanas 01 a 05.

O projeto realiza o carregamento, inspeção, limpeza, transformação e agregação de um dataset de vendas, gerando métricas por período, produto, categoria e região, além de uma segmentação simples de clientes por faixa de gasto.

## O que o projeto analisa

* Receita total e volume de vendas por mês e por trimestre
* Top 5 produtos por receita
* Receita total por categoria
* Desempenho de vendas por região
* Segmentação de clientes por nível de gasto: Bronze, Prata e Ouro
* Quantidade de vendas com receita por transação acima da média geral
* Exportação de resultados em arquivos CSV e JSON

## Conceitos aplicados

**Módulo 01 — Semanas 01 a 05**

* Lógica de programação: variáveis, tipos, operadores, condicionais e repetições
* Estruturas de dados: listas, tuplas, dicionários e estruturas compostas
* Funções: parâmetros, retorno, docstrings e funções de ordem superior
* Expressões `lambda`
* Leitura e escrita de arquivos CSV e JSON
* Manipulação de datas com `datetime`
* Expressões regulares com `re`
* Organização em módulos e utilização de imports
* Git e GitHub: branches, commits e GitFlow simplificado

## Como executar

### Google Colab

1. Faça o upload dos arquivos `salesinsight.py` e `vendas.csv` para o Google Colab.
2. Execute no terminal do Colab:

```bash
!python salesinsight.py
```

3. Também é possível executar o código diretamente em células de um notebook `.ipynb`.

### Localmente com VS Code

1. Instale o Python 3.10 ou superior e o VS Code.
2. Clone ou baixe este repositório.
3. Nenhuma dependência externa é necessária, pois o projeto utiliza apenas bibliotecas da biblioteca padrão do Python.
4. Execute no terminal:

```bash
python salesinsight.py
```

Os arquivos de resultados serão gerados na pasta `outputs/`.

## Estrutura do projeto

```text
salesinsight-py/
│
├── salesinsight.py
├── vendas.csv
├── README.md
│
├── outputs/
│   ├── metricas_por_mes.csv
│   ├── segmentacao_clientes.csv
│   └── estatisticas_gerais.json

```

## Decisões técnicas

Durante o tratamento dos dados, registros com datas inválidas ou campos obrigatórios ausentes são removidos em vez de receber valores estimados. Essa decisão mantém a análise baseada apenas em informações válidas e evita a criação de dados que não estavam presentes na fonte original.

Para as métricas agregadas, foram utilizadas estruturas de dados como dicionários para acumular e organizar os resultados por período, produto, categoria e região, tornando o processamento mais organizado e reutilizável.

A separação do projeto em funções também foi adotada para facilitar a manutenção, reutilização e execução das diferentes etapas do fluxo de análise.

## Ferramentas utilizadas

* Python 3.10+
* Google Colab / VS Code
* Bibliotecas da biblioteca padrão do Python:

  * `csv`
  * `json`
  * `re`
  * `datetime`
  * `os`
  * `random`
* Git e GitHub
* GitHub Desktop (opcional)
* Trello / GitHub Projects para organização do Kanban

## Video de demonstração

[Inserir o link do Google Drive ou do YouTube aqui]
