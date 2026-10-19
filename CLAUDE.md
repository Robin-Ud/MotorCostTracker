# CLAUDE.md

Script Python puro para registro de gastos de veículos. Sem dependências externas, sem packaging.

## Rodar

```bash
python motoregis.py
# ou via alias no .bashrc:
alias motoregis='python ~/deving/veiculos-saude/MotorCostTracker/motoregis.py'
```

## Estrutura

```
motoregis.py        ← script único
exemplo/            ← dados inventados (Honda CG 160 Titan, Chevrolet Onix), mesmo formato
pessoal/            ← dados reais, fora do git (clone do repo privado veiculos-dados)
  configs.json      ← config global
  veiculos/
    himalayan_22.json ← config e intervalos de manutenção
    himalayan_22.csv  ← registros (append-only)
    etios_16.json
```

`DATA_DIR` é `pessoal/` ao lado do script; sem ela, `exemplo/`. A pasta tem o mesmo
formato que o `motor_dir` do argos (que lê e grava nela também).

`veiculos_index` em `configs.json` mapeia nome → caminho relativo do JSON. O CSV usa o mesmo caminho com extensão `.csv`.

## Arquitetura

Quatro zonas no `motoregis.py`:

| Zona | Papel |
|------|-------|
| 1 — Data Engines | `load_json`, `read_csv`, `append_record`, `git_sync` — só I/O |
| 2 — Validators | `get_int`, `get_float`, `select_index` — validação isolada |
| 3 — Orchestration | lógica de negócio: manutenção, odômetro, fluxos de registro |
| 4 — Interface | loop do menu principal |

## CSV

Colunas: `data, odometro, categoria, custo, litros, detalhes`

Categorias: `1`=Abastecimento, `2`=Manutenção Preventiva, `3`=Acessórios, `4`=Manutenção Corretiva, `5`=Burocracia

Primeira linha é header. Registros a partir da linha 2.

Abastecimentos (`categoria=1`) marcam `detalhes` como `combustivel|cheio` ou `combustivel|parcial`. Uma tag extra `|gap` (ex.: `gasolina_comum|cheio|gap`) indica que houve abastecimento(s) reais não registrados antes desse (ex.: veículo emprestado) — `show_cost_analysis` ignora o par cheio-a-cheio que termina numa linha `|gap` ao calcular km/L e custo/10km, pra não distorcer as médias com uma distância grande dividida pelos litros de só um tanque. `record_fuel` sugere marcar `|gap` automaticamente quando a distância desde o último abastecimento é bem maior que a média histórica. Outra tag extra opcional, `|viagem` ou `|cidade` (ex.: `gasolina_comum|cheio|viagem`), classifica o trecho desde o abastecimento anterior — só armazenada, não usada em nenhum cálculo hoje. Todas as tags são independentes e podem se acumular (`combustivel|cheio|gap|viagem`); o parsing em todo o código é feito por substring (`in`), nunca por índice fixo, então a ordem não importa.

`show_cost_analysis` imprime um resumo enxuto em dois blocos, com lógica de exibição invertida entre eles:
- **Padrão de pilotagem** (km/L, dias rodados, km rodados): mostra por padrão o valor do **último** trecho cheio-a-cheio; a média geral só aparece como linha extra se o último desviar mais de 10% dela.
- **Custo** (custo/dia médio do período, combustível + manutenção amortizada; custo/10km): mostra por padrão a **média geral**; o valor do último tanque só aparece como linha extra se desviar mais de 10% da média.

Escolha de "mostrar por padrão o último vs. a média" é proposital: pilotagem recente é o que motiva ação imediata, custo é melhor julgado pela tendência do período todo. No menu principal, escolher "0. Análise de Custos" agora encerra o programa depois de imprimir (não volta pro menu).

## Regras

- Zero dependências externas — só stdlib (`csv`, `json`, `os`, `subprocess`, `datetime`)
- Python 3.10+ — usar `X | Y` em vez de `Optional[X]`
- Type hints em todas as assinaturas

## Possibilidades (não ler sem ordem clara — ideias soltas, não roadmap)

- **Registrar posto de abastecimento**: nome genérico de posto/postos vizinhos torna geocoding pouco confiável. Alternativa: campo `posto` novo (quebra o schema atual do CSV, precisa migração).
- **Scan de nota fiscal (NFC-e)**: ler o QR code da nota (`pyzbar` + `Pillow`) → resolver CNPJ/razão social via portal da SEFAZ do estado → evita ambiguidade de nome e resolve postos vizinhos por CNPJ único. Fallback OCR (Tesseract) só se QR falhar. Cache `CNPJ → apelido do posto` pra não reconsultar toda vez.
- **Port para bot de Telegram**: manteria zonas 1-3 do `motoregis.py` quase intactas, trocando só a zona 4 (menu) por handlers do Telegram (`python-telegram-bot`). Isso rompe a regra de zero dependências externas — aceitável só nesse fork/port, não no script principal.
  - Ordem sugerida se for adiante: (a) bot recebendo foto e extraindo QR cru, (b) parser de nota de 1 estado da SEFAZ, (c) fluxo de confirmação + `append_record`, (d) cache de posto por CNPJ, (e) OCR fallback por último.
  - Custo: baixo — hospedagem em VPS free tier ou máquina própria, APIs do Telegram e da SEFAZ são grátis. Custo real é tempo de dev, principalmente por causa da variação de portal entre estados.

@pessoal/CLAUDE.md
