import csv
import random
import re
from datetime import datetime, timedelta

import pandas as pd
import numpy as np


# RF01 - Geração do dataset
def gerar_dataset_vendas(caminho_csv="vendas.csv", n_registros=200, seed=42):
    """Gera um dataset sintético de vendas com dados sujos e salva em CSV."""
    random.seed(seed)

    produtos = [
        "Notebook", "Smartphone", "Tablet", "Monitor",
        "Teclado", "Mouse", "Headset"
    ]

    categorias = {
        "Notebook": "Computadores",
        "Smartphone": "Celulares",
        "Tablet": "Celulares",
        "Monitor": "Computadores",
        "Teclado": "Perifericos",
        "Mouse": "Perifericos",
        "Headset": "Perifericos"
    }

    precos = {
        "Notebook": 3500,
        "Smartphone": 2200,
        "Tablet": 1800,
        "Monitor": 1200,
        "Teclado": 250,
        "Mouse": 120,
        "Headset": 350
    }

    regioes = [
        "Sudeste", "Sul", "Nordeste",
        "Centro-Oeste", "Norte"
    ]

    data_inicio = datetime(2025, 1, 1)

    colunas = [
        "id_venda",
        "data_venda",
        "cliente",
        "produto",
        "categoria",
        "regiao",
        "quantidade",
        "preco_unitario"
    ]

    with open(caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for i in range(n_registros):
            produto = random.choice(produtos)
            categoria = categorias[produto]
            quantidade = random.randint(1, 10)
            preco = round(
                precos[produto] * random.uniform(0.85, 1.15),
                2
            )

            data = data_inicio + timedelta(
                days=random.randint(0, 364)
            )
            data_txt = data.strftime("%Y-%m-%d")

            cliente = f"Cliente_{random.randint(1, 50):03d}"

            # Geração proposital de dados inconsistentes
            if random.random() < 0.05:
                quantidade = ""

            if random.random() < 0.04:
                preco = ""

            if random.random() < 0.06:
                produto = " " + produto + " "

            if random.random() < 0.03:
                data_txt = "DATA INVALIDA"

            if random.random() < 0.10:
                cliente = random.choice([
                    cliente.upper().replace("_", "-"),
                    cliente + "!!",
                    " " + cliente,
                    cliente.replace("Cliente_", "cliente#"),
                ])

            escritor.writerow({
                "id_venda": i + 1,
                "data_venda": data_txt,
                "cliente": cliente,
                "produto": produto,
                "categoria": categoria,
                "regiao": random.choice(regioes),
                "quantidade": quantidade,
                "preco_unitario": preco,
            })

    print(f"Dataset gerado com {n_registros} registros em '{caminho_csv}'.")


# RF02 - Carregamento e inspeção
def carregar_dataset(caminho_csv="vendas.csv"):
    """Carrega o CSV e retorna um DataFrame."""
    return pd.read_csv(caminho_csv)


def inspecionar_dados(df):
    """Exibe informações estruturais do dataset."""

    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Total de registros: {len(df)}")
    print(f"Total de colunas: {len(df.columns)}")

    print("\nColunas:")
    print(list(df.columns))

    print("\nValores ausentes por coluna:")
    print(df.isna().sum())

    print("\nPrimeiros registros:")
    print(df.head())


# RF03 - Limpeza e tratamento
def limpar_dados(df):
    """Limpa e trata os dados de vendas."""

    relatorio = {
        "iniciais": len(df),
        "removidos_data": 0,
        "removidos_nulos": 0,
        "finais": 0
    }

    # Remove espaços extras dos campos de texto
    colunas_texto = ["cliente", "produto", "categoria", "regiao"]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].str.strip()

    # Valida as datas e remove registros inválidos
    datas_validas = []

    for data in df["data_venda"]:
        try:
            data_convertida = datetime.strptime(data, "%Y-%m-%d")
            datas_validas.append(data_convertida)
        except ValueError:
            datas_validas.append(None)
            relatorio["removidos_data"] += 1

    df["data_venda"] = datas_validas
    df = df.dropna(subset=["data_venda"])

    # Remove registros com quantidade ou preço ausente
    registros_antes = len(df)

    df = df.dropna(
        subset=["quantidade", "preco_unitario"]
    )

    relatorio["removidos_nulos"] = registros_antes - len(df)

    # Garante os tipos numéricos esperados
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    # Padroniza e valida os nomes dos clientes
    padrao_cliente = re.compile(
        r"^Cliente_\d{3}$",
        flags=re.IGNORECASE
    )

    clientes_padronizados = []
    clientes_fora_padrao = []

    for cliente in df["cliente"]:
        cliente_original = cliente

        # Remove caracteres especiais
        cliente_limpo = re.sub(
            r"[^A-Za-z0-9_]",
            "",
            cliente
        )

        numero = re.search(r"\d{3}", cliente_limpo)

        if numero:
            cliente_padronizado = f"Cliente_{numero.group()}"
        else:
            cliente_padronizado = cliente_limpo

        clientes_padronizados.append(cliente_padronizado)
        clientes_fora_padrao.append(
            padrao_cliente.match(cliente_original) is None
        )

    df["cliente"] = clientes_padronizados
    df["cliente_fora_do_padrao"] = clientes_fora_padrao

    relatorio["finais"] = len(df)

    print("\n=== RELATÓRIO DE LIMPEZA ===")
    print(f"Registros iniciais: {relatorio['iniciais']}")
    print(f"Removidos por data inválida: {relatorio['removidos_data']}")
    print(f"Removidos por valores ausentes: {relatorio['removidos_nulos']}")
    print(f"Registros finais: {relatorio['finais']}")

    return df, relatorio

# RF04 - Criação de colunas derivadas
def criar_colunas_derivadas(df):
    """Cria colunas calculadas a partir dos dados de vendas."""

    df["receita_total"] = (
        df["quantidade"] * df["preco_unitario"]
    )

    df["mes"] = [
        data.month for data in df["data_venda"]
    ]

    df["ano"] = [
        data.year for data in df["data_venda"]
    ]

    meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    df["mes_nome"] = df["mes"].map(meses)

    trimestres = []

    for mes in df["mes"]:
        if mes <= 3:
            trimestre = "Q1"
        elif mes <= 6:
            trimestre = "Q2"
        elif mes <= 9:
            trimestre = "Q3"
        else:
            trimestre = "Q4"

        trimestres.append(trimestre)

    df["trimestre"] = trimestres

    faixas = []

    for receita in df["receita_total"]:
        if receita < 500:
            faixa = "Baixo Valor"
        elif receita < 5000:
            faixa = "Medio Valor"
        else:
            faixa = "Alto Valor"

        faixas.append(faixa)

    df["faixa_receita_item"] = faixas

    return df

# RF05 - Agregações e métricas
def calcular_metricas(df):
    """Calcula métricas de vendas por diferentes dimensões."""

    metricas_mensais = (
        df.groupby(["mes", "mes_nome"])
        .agg(
            receita_total=("receita_total", "sum"),
            quantidade_vendida=("quantidade", "sum"),
            numero_vendas=("id_venda", "count")
        )
        .reset_index()
        .sort_values("mes")
    )

    top_produtos = (
        df.groupby("produto")
        .agg(
            receita_total=("receita_total", "sum")
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
        .head(5)
    )

    receita_categoria = (
        df.groupby("categoria")
        .agg(
            receita_total=("receita_total", "sum")
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )

    metricas_regiao = (
        df.groupby("regiao")
        .agg(
            receita_total=("receita_total", "sum"),
            ticket_medio=("receita_total", "mean")
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )

    metricas = {
        "mensais": metricas_mensais,
        "top_produtos": top_produtos,
        "categorias": receita_categoria,
        "regioes": metricas_regiao
    }

    return metricas

# Execução
gerar_dataset_vendas()
df = carregar_dataset()
inspecionar_dados(df)
df, relatorio = limpar_dados(df)
df = criar_colunas_derivadas(df)

print("\n=== DADOS APÓS TRANSFORMAÇÕES ===")
print(df.head())

metricas = calcular_metricas(df)

print("\n=== MÉTRICAS MENSAIS ===")
print(metricas["mensais"])

print("\n=== TOP 5 PRODUTOS ===")
print(metricas["top_produtos"])

print("\n=== RECEITA POR CATEGORIA ===")
print(metricas["categorias"])

print("\n=== MÉTRICAS POR REGIÃO ===")
print(metricas["regioes"])