from fastapi import FastAPI, Path
from pydantic import BaseModel
from typing import List
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from fastapi.responses import JSONResponse, Response

# ✅ Importa o router da pasta routes
from routes.grafico_fastapi import router as grafico_router

app = FastAPI(
    title="Comparador de Ativos API",
    description="API para comparar a evolução de rentabilidade de ativos (ações ou cripto)",
    version="1.0"
)

# ✅ Registra o router do gráfico
app.include_router(grafico_router)

class ComparacaoRequest(BaseModel):
    ativos: List[str]
    inicio: str  # formato 'YYYY-MM-DD'
    fim: str     # formato 'YYYY-MM-DD'
    aporte: float = 500

@app.post("/comparar")
def comparar_ativos(req: ComparacaoRequest):
    resultado = []
    fig, ax = plt.subplots(figsize=(12, 6))

    for ativo in req.ativos:
        dados = yf.download(ativo, start=req.inicio, end=req.fim, interval="1mo", auto_adjust=False)

        if 'Adj Close' not in dados.columns:
            return JSONResponse(status_code=500, content={
                "erro": f"'Adj Close' não encontrado para {ativo}. Colunas disponíveis: {list(dados.columns)}"
            })

        dados = dados[dados['Adj Close'].notna()]
        dados['Ano'] = dados.index.year

        if dados.empty:
            return JSONResponse(status_code=500, content={
                "erro": f"Sem dados disponíveis para {ativo} entre {req.inicio} e {req.fim}."
            })

        df_ano = dados.groupby('Ano').first().reset_index()
        total_unidades = 0
        historico = []

        for _, row in df_ano.iterrows():
            ano = int(row['Ano'])
            preco = float(row['Adj Close'])
            unidades = req.aporte / preco
            total_unidades += unidades
            preco_final = float(df_ano['Adj Close'].iloc[-1])
            valor_final = total_unidades * preco_final

            historico.append({
                "Ano": ano,
                "Preço": round(preco, 2),
                "Unidades Acumuladas": round(total_unidades, 6),
                "Evolução até 2025 (€)": round(valor_final, 2)
            })

        df_resultado = pd.DataFrame(historico)
        ax.plot(df_resultado['Ano'], df_resultado['Evolução até 2025 (€)'], marker='o', label=ativo)
        resultado.append({"ativo": ativo, "dados": historico})

    ax.set_title("Evolução de Investimentos por Ativo")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Valor acumulado (€)")
    ax.legend()
    ax.grid(True)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    imagem_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return JSONResponse(content={
        "comparacao": resultado,
        "grafico_base64": imagem_base64
    })
