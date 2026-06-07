import sqlite3
import pandas as pd
import smtplib
import email.message
from senha import senha

with sqlite3.connect("gasolina.db") as con:
    query = """
        SELECT * 
        FROM preco 
        ORDER BY data_coleta DESC 
        LIMIT 2;
    """
    df_recentes = pd.read_sql_query(query, con)

preco_novo    = df_recentes.loc[0, "preco_medio"]
preco_antigo  = df_recentes.loc[1, "preco_medio"]
data_nova     = pd.to_datetime(df_recentes.loc[0, "data_coleta"]).strftime("%d/%m/%Y")
data_antiga   = pd.to_datetime(df_recentes.loc[1, "data_coleta"]).strftime("%d/%m/%Y")
minimo_novo   = df_recentes.loc[0, "preco_minimo"]
maximo_novo   = df_recentes.loc[0, "preco_maximo"]

porcentagem = round(((preco_novo - preco_antigo) / preco_antigo) * 100, 2)
sinal = "▲" if porcentagem > 0 else "▼"


def enviar_email(porcentagem, preco_novo, preco_antigo,
                 data_nova, data_antiga, minimo_novo, maximo_novo):
    corpo_email = f"""
    <h3>Alerta de variação no preço da gasolina</h3>
    <p><b>Período comparado:</b> {data_antiga} → {data_nova}</p>
    <p><b>Preço anterior:</b> R$ {preco_antigo:.3f}</p>
    <p><b>Preço atual:</b> R$ {preco_novo:.3f}</p>
    <p><b>Variação:</b> {sinal} {abs(porcentagem)}%</p>
    <hr>
    <p><b>Mínimo registrado:</b> R$ {minimo_novo:.3f}</p>
    <p><b>Máximo registrado:</b> R$ {maximo_novo:.3f}</p>
    """

    msg = email.message.Message()
    msg['Subject'] = f"Gasolina {sinal} {abs(porcentagem)}%"
    msg['From'] = '@gmail.com'
    msg['To'] = '0@gmail.com'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(msg['From'], senha)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    s.quit()
    print('Email enviado')


if abs(porcentagem) > 2:
    enviar_email(porcentagem, preco_novo, preco_antigo,
                 data_nova, data_antiga, minimo_novo, maximo_novo)
else:
    print(f"Sem ajuste significativo. Variação: {porcentagem}%")
