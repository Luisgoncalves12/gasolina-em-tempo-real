# Monitor de Preço da Gasolina 

Projeto que coleta dados de preço da gasolina direto do site da ANP, processa e manda um e-mail automático quando o preço varia mais de 2%.

---

## Como funciona

**1. Coleta os dados**

Pega o CSV direto do site do governo, sem precisar baixar nada manualmente:

```python
url = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv"
df = pd.read_csv(url, sep=';', encoding='latin1', decimal=',')
```

O DataFrame vem com 45.551 linhas e 16 colunas:

![DataFrame original](images/image3.png)

---

**2. Limpa e filtra**

- Filtra só o Distrito Federal pela sigla do estado
- Usa `.str.contains('GASOLINA')` pra pegar todos os tipos de gasolina
- Converte `Data da Coleta` pra datetime no formato brasileiro (`%d/%m/%Y`)
- Remove as colunas `Valor de Compra` e `Complemento`
- Remove linhas com data ou preço nulos

Resultado após o filtro:

![DataFrame filtrado](images/image4.png)

---

**3. Agrupa por dia**

Agrupa por `Data da Coleta` e calcula preço médio, mínimo, máximo e quantidade de postos pesquisados com `.agg()`.

Renomeia as colunas com `.rename()` pra evitar conflito com o banco (a coluna `Data da Coleta` tem espaço, o que quebrava na hora de salvar no SQLite).

![Resultado agrupado](images/image1.png)

---

**4. Salva no banco**

Cria um banco SQLite local (`gasolina.db`). Se a tabela `preco` não existir, cria — com `data_coleta` como chave primária, já que só existe um preço por dia.

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
```

Usa `abs()` pra capturar tanto alta quanto queda — se o valor absoluto passar de 2%, dispara o e-mail.

![E-mail recebido](images/image2.png)

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
