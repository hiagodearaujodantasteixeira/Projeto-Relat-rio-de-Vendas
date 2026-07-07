import os
import random
import pandas as pd
from datetime import datetime, timedelta

# 1. Criar uma pasta para simular a origem dos dados
pasta_origem = "dados_logistica_filiais"
os.makedirs(pasta_origem, exist_ok=True)

# Função auxiliar para gerar dados básicos de vendas/logística
def gerar_dados_base(num_linhas):
    produtos = ["Console Retro", "Cabo HDMI Gold", "Controle Wireless", "Headset Pro", "Cadeira Gamer"]
    skus = ["CON-RET-01", "CAB-HDMI-02", "CNT-WRL-03", "HDS-PRO-04", "CDR-GMR-05"]
    
    dados = []
    data_inicial = datetime(2025, 1, 1)
    
    for _ in range(num_linhas):
        idx = random.randint(0, len(produtos) - 1)
        data_venda = data_inicial + timedelta(days=random.randint(0, 365))
        preco_unitario = round(random.uniform(15.0, 350.0), 2)
        quantidade = random.randint(1, 5)
        
        dados.append({
            "Data": data_venda.strftime("%Y-%m-%d"),
            "SKU": skus[idx],
            "Produto": produtos[idx],
            "Preco": preco_unitario,
            "Qtd": quantidade,
            "Status_Entrega": random.choice(["Entregue", "Em Trânsito", "Cancelado"])
        })
    return pd.DataFrame(dados)

# --- GERANDO ARQUIVOS COM INCONSISTÊNCIAS PROPOSITAIS ---

# Filial 1: São Paulo (Dados Normais, mas cabeçalho diferente)
df_sp = gerar_dados_base(150)
df_sp.rename(columns={"Data": "Data_Venda", "Preco": "Valor_Unitario"}, inplace=True)
df_sp.to_excel(os.path.join(pasta_origem, "Vendas_Filial_SP.xlsx"), index=False)

# Filial 2: Paraná (Com linhas em branco no topo e linha de "Total" fake no final)
df_pr = gerar_dados_base(120)
df_pr.rename(columns={"Data": "DT_FATURAMENTO"}, inplace=True)
# Adiciona uma linha de total que vai quebrar o Group By se não for tratada
linha_total = pd.DataFrame([{"DT_FATURAMENTO": "Total Geral", "SKU": "", "Produto": "", "Preco": df_pr["Preco"].sum(), "Qtd": df_pr["Qtd"].sum(), "Status_Entrega": ""}], columns=df_pr.columns)
df_pr = pd.concat([df_pr, linha_total], ignore_index=True)

# Salvar PR deixando 3 linhas em branco no início usando o openpyxl via pandas
with pd.ExcelWriter(os.path.join(pasta_origem, "Vendas_Filial_PR.xlsx")) as writer:
    df_pr.to_excel(writer, index=False, startrow=3)

# Filial 3: Minas Gerais (Contém valores com erro de escala/falta de vírgula)
df_mg = gerar_dados_base(100)
# Vamos escolher algumas linhas de propósito e multiplicar por 1000 (fazendo 8.50 virar 8500.0)
df_mg.loc[df_mg.sample(frac=0.15).index, "Preco"] = df_mg["Preco"] * 1000
df_mg.to_excel(os.path.join(pasta_origem, "Vendas_Filial_MG.xlsx"), index=False)

print(f"🔥 Sucesso! 3 arquivos de filiais criados na pasta '{pasta_origem}'.")