# Monitor de Preço da Gasolina 

Me propus esse desafio pra aprender na prática, desenvolver um sistema que coleta dados oficiais da ANP, armazena o histórico em banco de dados e envia alerta por e-mail quando o preço médio semanal da gasolina em Brasília variar mais de 2% em relação à semana anterior.

---

## Como funciona

**1. Coleta os dados**

Pega o CSV direto do site do governo, sem precisar baixar nada manualmente:

```python
url = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv"
df = pd.read_csv(url, sep=';', encoding='latin1', decimal=',')
```

O DataFrame vem com 45.551 linhas e 16 colunas:

<img width="1469" height="782" alt="Captura de tela 2026-06-07 150241" src="https://github.com/user-attachments/assets/6bb2125d-a20a-4784-a582-1a7d5d6d0d42" />


---

**2. Limpa e filtra**

- Filtra só o Distrito Federal pela sigla do estado
- Usa `.str.contains('GASOLINA')` pra pegar todos os tipos de gasolina
- Converte `Data da Coleta` pra datetime no formato brasileiro (`%d/%m/%Y`)
- Remove as colunas `Valor de Compra` e `Complemento`
- Remove linhas com data ou preço nulos

Resultado após o filtro:

<img width="1516" height="315" alt="Captura de tela 2026-06-07 143408" src="https://github.com/user-attachments/assets/024f52a5-eb16-4de7-a149-0bb10ba86c72" />


---

**3. Agrupa por dia**

Agrupa por `Data da Coleta` e calcula preço médio, mínimo, máximo e quantidade de postos pesquisados com `.agg()`.

Renomeia as colunas com `.rename()` pra evitar conflito com o banco (a coluna `Data da Coleta` tem espaço, o que quebrava na hora de salvar no SQLite).

<img width="521" height="224" alt="Captura de tela 2026-06-07 143453" src="https://github.com/user-attachments/assets/458a50a1-aff0-4999-99ed-b9e745df5e9f" />

---

**4. Salva no banco**

Cria um banco SQLite local (`gasolina.db`). Se a tabela `preco` não existir, cria com `data_coleta` como chave primária, já que só existe um preço por dia.

```python
cursor.execute("""
CREATE TABLE IF NOT EXISTS preco (
    data_coleta DATE PRIMARY KEY,
    preco_medio REAL,
    preco_minimo REAL,
    preco_maximo REAL,
    qtd_postos INTEGER
)
""")
```

---

**5. Compara e dispara o alerta**

Busca as duas últimas datas no banco e calcula a variação percentual:

```python
porcentagem = round(((preco_novo - preco_antigo) / preco_antigo) * 100, 2)

if abs(porcentagem) > 2:
    enviar_email(porcentagem, preco_novo, preco_antigo,
                 data_nova, data_antiga, minimo_novo, maximo_novo)
else:
    print(f"Sem ajuste significativo. Variação: {porcentagem}%")
```

Usa `abs()` pra capturar tanto alta quanto queda se o valor absoluto passar de 2%, dispara o e-mail.

<img width="739" height="1600" alt="WhatsApp Image 2026-06-07 at 14 52 49" src="https://github.com/user-attachments/assets/d31b59fb-4fe6-447e-a059-2113fa250847" />


---

## Arquivos

```
├── dados.ipynb       # coleta, limpeza e salvamento no banco
├── sim.py            # comparação e envio de e-mail
├── senha.py          # senha do e-mail (não sobe pro GitHub)
├── gasolina.db       # banco de dados local (não sobe pro GitHub)
└── .gitignore
```

## .gitignore

```
gasolina.db
senha.py
```

## Requisitos

```
pandas
sqlite3
smtplib
```

> A senha usada no envio é uma **senha de aplicativo** do Gmail, não a senha normal da conta.
