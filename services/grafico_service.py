import matplotlib.pyplot as plt
import io
import random
import datetime

def gerar_grafico_png(ativo):
    # Exemplo com dados fictícios
    dias = [datetime.date.today() - datetime.timedelta(days=i) for i in range(14, -1, -1)]
    valores = [random.uniform(90, 110) for _ in dias]

    fig, ax = plt.subplots()
    ax.plot(dias, valores, marker='o')
    ax.set_title(f'Desempenho de {ativo.upper()} nos últimos 15 dias')
    ax.set_xlabel('Data')
    ax.set_ylabel('Valor')
    fig.autofmt_xdate()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()
