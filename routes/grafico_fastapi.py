from fastapi import APIRouter, Response, Path
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io

router = APIRouter()

@router.get("/grafico/{ativos}", response_class=Response, tags=["Gráficos"])
def gerar_grafico_comparativo(ativos: str = Path(..., description="Tickers separados por vírgula (ex: PETR4.SA,VALE3.SA)")):
    lista_ativos = [a.strip() for a in ativos.split(",")]
    fig, ax = plt.subplots(figsize=(12, 6))

    for ativo in lista_ativos:
        dados = yf.download(ativo, period="5y", interval="1mo", auto_adjust=False)

        if 'Adj Close' not in dados.columns or dados.empty:
            continue  # pula ativos com dados inválidos

        dados = dados[dados['Adj Close'].notna()]
        dados['Ano'] = dados.index.year
        df_ano = dados.groupby('Ano').first().reset_index()

        total_unidades = 0
        aporte = 500
        valores = []

        for _, row in df_ano.iterrows():
            preco = float(row['Adj Close'])
            total_unidades += aporte / preco
            preco_final = float(df_ano['Adj Close'].iloc[-1])
            valores.append(total_unidades * preco_final)

        ax.plot(df_ano['Ano'], valores, marker='o', label=ativo)

    ax.set_title("Comparação de Evolução dos Ativos")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Valor Acumulado (€)")
    ax.grid(True)
    ax.legend()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    return Response(content=buf.read(), media_type="image/png")
