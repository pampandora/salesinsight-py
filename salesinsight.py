import csv
import random
import re
from datetime import datetime, timedelta
import json
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


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


# RF06 - Segmentação de clientes
def segmentar_clientes(df):
    """Agrupa clientes, calcula o gasto total e define o segmento."""

    gastos_clientes = (
        df.groupby("cliente")
        .agg(total_gasto=("receita_total", "sum"))
        .reset_index()
    )

    classificar = lambda total: (
        "Ouro" if total > 15000
        else "Prata" if total >= 5000
        else "Bronze"
    )

    gastos_clientes["segmento"] = (
        gastos_clientes["total_gasto"].map(classificar)
    )

    top_10 = (
        gastos_clientes
        .sort_values("total_gasto", ascending=False)
        .head(10)
    )

    distribuicao = (
        gastos_clientes["segmento"]
        .value_counts()
        .rename_axis("segmento")
        .reset_index(name="quantidade_clientes")
    )

    return {
        "clientes": gastos_clientes,
        "top_10": top_10,
        "distribuicao": distribuicao
    }


# RF07
def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """
    Aplica uma função de transformação a uma coluna do DataFrame.
    Demonstra o uso de função como argumento.
    """
    nome_saida = nome_saida or f"{coluna}_transformado"

    df[nome_saida] = df[coluna].map(funcao_transformacao)

    return df


# RF08
def calcular_estatisticas_gerais(df):
    """Calcula estatísticas gerais das vendas."""

    receitas = df["receita_total"].to_numpy()

    receita_media = np.mean(receitas)
    receita_mediana = np.median(receitas)
    receita_desvio_padrao = np.std(receitas)

    return {
        "total_vendas": len(df),
        "receita_total": np.sum(receitas),
        "receita_media_por_venda": receita_media,
        "receita_mediana": receita_mediana,
        "receita_desvio_padrao": receita_desvio_padrao,
        "vendas_acima_da_media": int(
            np.sum(receitas > receita_media)
        )
    }


def exportar_resultados(metricas, clientes, estatisticas):
    """Exporta os resultados do projeto em CSV e JSON."""
    os.makedirs("outputs", exist_ok=True)

    por_mes = metricas["mensais"].to_dict("records")

    with open(
        "outputs/metricas_por_mes.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        escritor = csv.DictWriter(
            f,
            fieldnames=por_mes[0].keys()
        )
        escritor.writeheader()
        escritor.writerows(por_mes)

    clientes = clientes["clientes"].to_dict("records")

    with open(
        "outputs/segmentacao_clientes.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        escritor = csv.DictWriter(
            f,
            fieldnames=clientes[0].keys()
        )
        escritor.writeheader()
        escritor.writerows(clientes)

    serializavel = {
        "total_vendas": int(estatisticas["total_vendas"]),
        "receita_total": round(
            float(estatisticas["receita_total"]), 2
        ),
        "receita_media_por_venda": round(
            float(estatisticas["receita_media_por_venda"]), 2
        ),
        "receita_mediana": round(
            float(estatisticas["receita_mediana"]), 2
        ),
        "receita_desvio_padrao": round(
            float(estatisticas["receita_desvio_padrao"]), 2
        ),
        "vendas_acima_da_media": int(
            estatisticas["vendas_acima_da_media"]
        )
    }

    caminho = "outputs/estatisticas_gerais.json"

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            serializavel,
            f,
            indent=4,
            ensure_ascii=False
        )

    with open(caminho, "r", encoding="utf-8") as f:
        conferencia = json.load(f)

    print(f"JSON gravado e lido: {conferencia}")


# RF09 - Fluxo de Execução

def visualizar_receita_mensal(metricas):
    """Exibe e salva a evolução da receita total ao longo dos meses."""

    dados = metricas["mensais"]

    os.makedirs("outputs/graficos", exist_ok=True)

    plt.figure(figsize=(10, 5))

    sns.lineplot(
        data=dados,
        x="mes_nome",
        y="receita_total",
        marker="o"
    )

    plt.title("Receita Total por Mês")
    plt.xlabel("Mês")
    plt.ylabel("Receita Total (R$)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        "outputs/graficos/receita_total_por_mes.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# Gráfico - Top 5 produtos
def visualizar_top_produtos(metricas):
    """Exibe e salva o Top 5 produtos por receita."""

    dados = metricas["top_produtos"]

    os.makedirs("outputs/graficos", exist_ok=True)

    plt.figure(figsize=(10, 5))

    sns.barplot(
        data=dados,
        x="receita_total",
        y="produto"
    )

    plt.title("Top 5 Produtos por Receita")
    plt.xlabel("Receita Total (R$)")
    plt.ylabel("Produto")
    plt.tight_layout()

    plt.savefig(
        "outputs/graficos/top_5_produtos.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# Gráfico - Receita por categoria
def visualizar_receita_categoria(metricas):
    """Exibe e salva a receita total por categoria."""

    dados = metricas["categorias"]

    os.makedirs("outputs/graficos", exist_ok=True)

    plt.figure(figsize=(10, 5))

    sns.barplot(
        data=dados,
        x="categoria",
        y="receita_total"
    )

    plt.title("Receita Total por Categoria")
    plt.xlabel("Categoria")
    plt.ylabel("Receita Total (R$)")
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig(
        "outputs/graficos/receita_por_categoria.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# Gráfico - Receita por região
def visualizar_receita_regiao(metricas):
    """Exibe e salva a receita total por região."""

    dados = metricas["regioes"]

    os.makedirs("outputs/graficos", exist_ok=True)

    plt.figure(figsize=(10, 5))

    sns.barplot(
        data=dados,
        x="regiao",
        y="receita_total"
    )

    plt.title("Receita Total por Região")
    plt.xlabel("Região")
    plt.ylabel("Receita Total (R$)")
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig(
        "outputs/graficos/receita_por_regiao.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# Projeção de tendência
def projetar_receita_media_movel(metricas, meses_futuros=3):
    """Projeta a receita dos próximos meses usando média móvel."""

    dados = metricas["mensais"].copy()

    # Seleciona os últimos 3 meses disponíveis
    ultimos_meses = dados["receita_total"].tail(3)

    # Calcula a média das receitas
    media_movel = ultimos_meses.mean()

    ultimo_mes = dados["mes"].max()

    projecoes = []

    for i in range(1, meses_futuros + 1):
        mes_projetado = ultimo_mes + i

        # Volta para janeiro após dezembro
        if mes_projetado > 12:
            mes_projetado -= 12

        projecoes.append({
            "mes": mes_projetado,
            "receita_projetada": media_movel
        })

    projecoes_df = pd.DataFrame(projecoes)

    print("\n=== B02 - PROJEÇÃO DE RECEITA ===")
    print(
        f"Média móvel dos últimos 3 meses: "
        f"R$ {media_movel:.2f}"
    )

    print("\nReceita projetada para os próximos meses:")
    print(projecoes_df)

    return projecoes_df


# Gráfico - Receita real x projeção
def visualizar_projecao_receita(metricas, projecao):
    """Exibe e salva o gráfico de receita real e projetada."""

    dados_reais = metricas["mensais"].copy()

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

    projecao = projecao.copy()
    projecao["mes_nome"] = projecao["mes"].map(meses)

    dados_reais["tipo"] = "Real"
    projecao["tipo"] = "Projetada"

    plt.figure(figsize=(10, 5))

    sns.lineplot(
        data=dados_reais,
        x="mes_nome",
        y="receita_total",
        marker="o",
        label="Receita Real"
    )

    sns.lineplot(
        data=projecao,
        x="mes_nome",
        y="receita_projetada",
        marker="o",
        linestyle="--",
        label="Receita Projetada"
    )

    plt.title("Receita Real x Projeção por Média Móvel")
    plt.xlabel("Mês")
    plt.ylabel("Receita (R$)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "outputs/graficos/receita_real_x_projecao.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# Pivot mês × categoria
def criar_tabela_pivot(df):
    """Cria uma tabela cruzada de receita por mês e categoria."""

    tabela_pivot = pd.pivot_table(
        df,
        values="receita_total",
        index="mes_nome",
        columns="categoria",
        aggfunc="sum",
        fill_value=0
    )

    # Ordena os meses na ordem correta
    ordem_meses = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ]

    tabela_pivot = tabela_pivot.reindex(ordem_meses)

    print("\n=== B03 - TABELA PIVOT MÊS × CATEGORIA ===")
    print(tabela_pivot)

    return tabela_pivot


# Histograma da receita
def visualizar_distribuicao_receita(df):
    """Exibe e salva a distribuição da receita por venda."""

    os.makedirs("outputs/graficos", exist_ok=True)

    plt.figure(figsize=(10, 5))

    sns.histplot(
        data=df,
        x="receita_total",
        bins=20,
        kde=True
    )

    plt.title("Distribuição da Receita por Venda")
    plt.xlabel("Receita por Venda (R$)")
    plt.ylabel("Quantidade de Vendas")

    plt.tight_layout()

    plt.savefig(
        "outputs/graficos/distribuicao_receita_por_venda.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# Exportação adicional dos dados relevantes
def exportar_dados_adicionais(
    df,
    metricas,
    segmentacao,
    projecao,
    tabela_pivot
):
    """Exporta os principais resultados adicionais em CSV."""

    os.makedirs("outputs", exist_ok=True)

    # Dataset tratado
    df.to_csv(
        "outputs/dataset_tratado.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Top 5 produtos
    metricas["top_produtos"].to_csv(
        "outputs/top_5_produtos.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Receita por categoria
    metricas["categorias"].to_csv(
        "outputs/receita_por_categoria.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Receita por região
    metricas["regioes"].to_csv(
        "outputs/receita_por_regiao.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Top 10 clientes
    segmentacao["top_10"].to_csv(
        "outputs/top_10_clientes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Distribuição dos segmentos
    segmentacao["distribuicao"].to_csv(
        "outputs/distribuicao_segmentos.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Projeção
    projecao.to_csv(
        "outputs/projecao_receita.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Tabela pivot
    tabela_pivot.to_csv(
        "outputs/tabela_pivot_mes_categoria.csv",
        encoding="utf-8-sig"
    )

    print("\n=== EXPORTAÇÃO DOS DADOS ===")
    print("Dados adicionais exportados para a pasta 'outputs'.")


class SalesInsight:
    """Classe responsável por executar o fluxo do SalesInsight PY."""

    def executar(self):
        """Executa todas as etapas do projeto."""

        # RF01 - Geração do dataset
        gerar_dataset_vendas()

        # RF02 - Carregamento e inspeção
        df = carregar_dataset()
        inspecionar_dados(df)

        # RF03 - Limpeza dos dados
        df, relatorio = limpar_dados(df)

        # RF04 - Criação das colunas derivadas
        df = criar_colunas_derivadas(df)

        print("\n=== DADOS APÓS TRANSFORMAÇÕES ===")
        print(df.head())

        # RF05 - Cálculo das métricas
        metricas = calcular_metricas(df)

        # Visualização da receita mensal
        visualizar_receita_mensal(metricas)

        # Gráfico Top 5 produtos
        visualizar_top_produtos(metricas)

        # Gráfico receita por categoria
        visualizar_receita_categoria(metricas)

        # Gráfico receita por região
        visualizar_receita_regiao(metricas)

        # B02 - Projeção simples por média móvel
        projecao = projetar_receita_media_movel(metricas)

        # Gráfico da projeção
        visualizar_projecao_receita(
            metricas,
            projecao
        )

        # B03 - Tabela cruzada mês × categoria
        tabela_pivot = criar_tabela_pivot(df)

        # B04 - Gráfico adicional
        visualizar_distribuicao_receita(df)

        print("\n=== MÉTRICAS MENSAIS ===")
        print(metricas["mensais"])

        print("\n=== TOP 5 PRODUTOS ===")
        print(metricas["top_produtos"])

        print("\n=== RECEITA POR CATEGORIA ===")
        print(metricas["categorias"])

        print("\n=== MÉTRICAS POR REGIÃO ===")
        print(metricas["regioes"])

        # RF06 - Segmentação dos clientes
        segmentacao = segmentar_clientes(df)

        print("\n=== TOP 10 CLIENTES ===")
        print(segmentacao["top_10"])

        print("\n=== DISTRIBUIÇÃO POR SEGMENTO ===")
        print(segmentacao["distribuicao"])

        # RF07 - Funções de transformação
        df = processar_coluna(
            df,
            "receita_total",
            lambda x: round(x / 1000, 2),
            nome_saida="receita_em_milhares"
        )

        df = processar_coluna(
            df,
            "quantidade",
            lambda q: "Alto Volume" if q > 5 else "Baixo Volume",
            nome_saida="perfil_volume"
        )

        print("\n=== COLUNAS CRIADAS NO RF07 ===")
        print(
            df[
                [
                    "receita_total",
                    "receita_em_milhares",
                    "quantidade",
                    "perfil_volume"
                ]
            ].head()
        )

        # RF08 - Estatísticas com NumPy
        estatisticas = calcular_estatisticas_gerais(df)

        print("\n=== ESTATÍSTICAS GERAIS ===")
        print(f"Total de vendas: {estatisticas['total_vendas']}")
        print(f"Receita total: {estatisticas['receita_total']:.2f}")
        print(
            f"Receita média por venda: "
            f"{estatisticas['receita_media_por_venda']:.2f}"
        )
        print(
            f"Receita mediana: "
            f"{estatisticas['receita_mediana']:.2f}"
        )
        print(
            f"Desvio padrão da receita: "
            f"{estatisticas['receita_desvio_padrao']:.2f}"
        )
        print(
            f"Vendas acima da média: "
            f"{estatisticas['vendas_acima_da_media']}"
        )

        # RF08 - Exportação dos resultados
        exportar_resultados(
            metricas,
            segmentacao,
            estatisticas
        )

        # Exportação adicional dos dados
        exportar_dados_adicionais(
            df,
            metricas,
            segmentacao,
            projecao,
            tabela_pivot
        )

        print("\n[CONCLUIDO] Fluxo completo do SalesInsight PY.")


def main():
    """Executa o fluxo completo do SalesInsight PY."""

    app = SalesInsight()
    app.executar()


if __name__ == "__main__":
    main()