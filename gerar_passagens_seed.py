"""
Gerador determinístico de dataset de compras de passagens de ônibus (2024).

Regras de negócio:
- Origem fixa: São Paulo (Tietê)
- Ônibus com 42 lugares (21 fileiras x assentos A/B, códigos 1A..21B)
- Cada combinação destino + dia = uma única viagem (mesmo ônibus):
  mesmo preço por assento, assentos sem repetição entre compras da viagem
- Inclui, de forma proposital: duplicatas de reprocessamento (~1-3%),
  inconsistências de digitação/valor/data (~5%), erros aleatórios extras (~2%)
  e dados faltantes (~3-7%)

Uso:
    python gerar_passagens_seed_v2.py 42
    python gerar_passagens_seed_v2.py 42 --saida meu_arquivo.csv
"""

import argparse
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def gerar_dataset(seed: int) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)

    origem = "São Paulo (Tietê)"

    destinos = [
        "Rio de Janeiro (RJ)", "Belo Horizonte (MG)", "Curitiba (PR)",
        "Porto Alegre (RS)", "Salvador (BA)", "Recife (PE)",
        "Fortaleza (CE)", "Brasília (DF)", "Goiânia (GO)", "Florianópolis (SC)",
    ]

    base_precos = {
        "Rio de Janeiro (RJ)": 90, "Belo Horizonte (MG)": 110,
        "Curitiba (PR)": 130, "Porto Alegre (RS)": 220,
        "Salvador (BA)": 280, "Recife (PE)": 320,
        "Fortaleza (CE)": 340, "Brasília (DF)": 180,
        "Goiânia (GO)": 160, "Florianópolis (SC)": 190,
    }

    ALL_SEATS = [f"{r}{l}" for r in range(1, 22) for l in ("A", "B")]
    horarios_possiveis = ["06:00", "07:30", "09:00", "11:00", "13:00",
                           "15:30", "18:00", "20:00", "22:30", "23:45"]

    # 1) Gerar viagens
    viagens = []
    vid = 0
    for destino in destinos:
        n_viagens = random.randint(6, 9)
        dias = random.sample(range(0, 366), n_viagens)
        for d in dias:
            data = datetime(2024, 1, 1) + timedelta(days=d)
            hora_str = random.choice(horarios_possiveis)
            hh, mm = map(int, hora_str.split(":"))
            dt = data.replace(hour=hh, minute=mm)
            preco = round(np.random.normal(base_precos[destino], 15), 2)
            preco = max(40.0, min(350.0, preco))
            viagens.append({
                "id": vid, "destino": destino, "data_partida": dt,
                "preco_unitario": preco, "assentos_livres": ALL_SEATS.copy(),
            })
            vid += 1

    # 2) Gerar compras
    N_COMPRAS = 500
    compras = []
    compra_num = 1
    tentativas = 0
    while len(compras) < N_COMPRAS and tentativas < N_COMPRAS * 30:
        tentativas += 1
        viagem = random.choice(viagens)
        livres = viagem["assentos_livres"]
        if not livres:
            continue
        qtd = random.choices([1, 2, 3, 4, 5], weights=[45, 30, 15, 7, 3])[0]
        qtd = min(qtd, len(livres))
        escolhidos = random.sample(livres, qtd)
        for a in escolhidos:
            livres.remove(a)

        compras.append({
            "compra_id": f"C-{compra_num:06d}",
            "quantidade_assentos": qtd,
            "posicoes_assentos": ", ".join(escolhidos),
            "origem": origem,
            "destino": viagem["destino"],
            "preco_unitario": viagem["preco_unitario"],
            "data_partida": viagem["data_partida"].strftime("%Y-%m-%d %H:%M"),
        })
        compra_num += 1

    df = pd.DataFrame(compras)

    # 3) Duplicatas de reprocessamento (1% a 3%)
    pct_dup = random.uniform(0.01, 0.03)
    n_dup = max(1, int(len(df) * pct_dup))
    dup_idx = np.random.choice(df.index, size=n_dup, replace=False)
    duplicatas = df.loc[dup_idx].copy()
    df = pd.concat([df, duplicatas], ignore_index=True)
    df = df.sample(frac=1, random_state=seed + 7).reset_index(drop=True)

    # 4) Inconsistências propositais (~5%)
    def gerar_typo_cidade(nome):
        opcoes = []
        sem_acento = (nome.replace("ã","a").replace("é","e").replace("í","i")
                          .replace("ó","o").replace("â","a").replace("ê","e")
                          .replace("ô","o").replace("ç","c").replace("Á","A"))
        opcoes.append(sem_acento)
        opcoes.append(nome.replace(" (", "(").replace(") ", ")"))
        opcoes.append(nome.lower())
        if len(nome) > 5:
            i = random.randint(1, len(nome) - 2)
            troca = nome[:i] + nome[i+1] + nome[i] + nome[i+2:]
            opcoes.append(troca)
        opcoes.append(nome.replace(")", "").replace("(", ""))
        return random.choice(opcoes)

    n_total = len(df)
    n_inconsist = int(n_total * 0.05)
    idx_pool = list(df.index)
    random.shuffle(idx_pool)
    idx_inconsist = idx_pool[:n_inconsist]
    terco = n_inconsist // 3

    for pos, idx in enumerate(idx_inconsist):
        tipo = 0 if pos < terco else (1 if pos < 2 * terco else 2)
        if tipo == 0:
            atual = df.loc[idx, "destino"]
            if pd.notna(atual):
                df.loc[idx, "destino"] = gerar_typo_cidade(str(atual))
        elif tipo == 1:
            erro_preco = random.choice([
                round(random.uniform(400, 999), 2),
                round(random.uniform(-50, -1), 2),
                0.0,
                round(random.uniform(4000, 9999), 2),
            ])
            df.loc[idx, "preco_unitario"] = erro_preco
        else:
            atual = df.loc[idx, "data_partida"]
            if pd.notna(atual):
                partes = str(atual).split(" ")
                data_str = partes[0]
                erro_data = random.choice([
                    data_str,
                    data_str.replace("-", "/"),
                    "/".join(reversed(data_str.split("-"))),
                    f"{data_str} 25:99",
                    f"{data_str} {partes[1]}" if len(partes) > 1 else data_str,
                ])
                df.loc[idx, "data_partida"] = erro_data

    # 5) Erros aleatórios adicionais (~2%)
    n_extra = int(n_total * 0.02)
    idx_extra = random.sample(list(df.index), n_extra)
    for idx in idx_extra:
        tipo = random.randint(0, 3)
        if tipo == 0 and pd.notna(df.loc[idx, "preco_unitario"]):
            df.loc[idx, "preco_unitario"] = round(float(df.loc[idx, "preco_unitario"]) + random.choice([-7, 7, 15, -15]), 2)
        elif tipo == 1:
            df.loc[idx, "origem"] = str(df.loc[idx, "origem"]).lower()
        elif tipo == 2 and pd.notna(df.loc[idx, "quantidade_assentos"]):
            df.loc[idx, "quantidade_assentos"] = df.loc[idx, "quantidade_assentos"] + random.choice([-1, 1])
        else:
            if pd.notna(df.loc[idx, "posicoes_assentos"]):
                df.loc[idx, "posicoes_assentos"] = str(df.loc[idx, "posicoes_assentos"]) + "  "

    # 6) Dados faltantes (3% a 7%)
    colunas_com_falha = ["preco_unitario", "posicoes_assentos", "destino", "data_partida"]
    total_celulas_alvo = len(df) * len(colunas_com_falha)
    pct_falha = random.uniform(0.03, 0.07)
    n_falhas = int(total_celulas_alvo * pct_falha)
    for _ in range(n_falhas):
        col = random.choice(colunas_com_falha)
        row = random.randint(0, len(df) - 1)
        df.loc[row, col] = np.nan

    return df


def main():
    parser = argparse.ArgumentParser(description="Gera dataset determinístico de passagens de ônibus (v2).")
    parser.add_argument(
        "seed",
        type=int,
        nargs="?",
        default=42,
        help="Seed inteira para reprodutibilidade (padrão: 42)",
    )
    parser.add_argument("--saida", type=str, default=None, help="Nome do arquivo de saída (opcional)")
    args = parser.parse_args()

    df = gerar_dataset(args.seed)
    nome_saida = args.saida or f"dados_passagens_raw_seed{args.seed}.csv"
    df.to_csv(nome_saida, index=False, encoding="utf-8-sig")

    print(f"Seed usada: {args.seed}")
    print(f"Arquivo gerado: {nome_saida}")
    print(f"Total de linhas: {len(df)}")


if __name__ == "__main__":
    main()
