# CLAUDE.md

Script Python puro para registro de gastos de veículos. Sem dependências externas, sem packaging.

## Rodar

```bash
python motoregis.py
# ou via alias no .bashrc:
alias motoregis='python ~/deving/MotorCostTracker/motoregis.py'
```

## Estrutura

```
motoregis.py        ← script único
configs.json        ← config global
veiculos/
  himalayan_22.json ← config e intervalos de manutenção
  himalayan_22.csv  ← registros (append-only)
  etios_16.json
```

`DATA_DIR` é sempre o diretório do próprio script (`os.path.dirname(__file__)`).

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

Abastecimentos (`categoria=1`) marcam `detalhes` como `combustivel|cheio` ou `combustivel|parcial`. Uma tag extra `|gap` (ex.: `gasolina_comum|cheio|gap`) indica que houve abastecimento(s) reais não registrados antes desse (ex.: veículo emprestado) — `show_cost_analysis` ignora o par cheio-a-cheio que termina numa linha `|gap` ao calcular km/L e custo/100km, pra não distorcer as médias com uma distância grande dividida pelos litros de só um tanque. `record_fuel` sugere marcar `|gap` automaticamente quando a distância desde o último abastecimento é bem maior que a média histórica.

## Regras

- Zero dependências externas — só stdlib (`csv`, `json`, `os`, `subprocess`, `datetime`)
- Python 3.10+ — usar `X | Y` em vez de `Optional[X]`
- Type hints em todas as assinaturas
