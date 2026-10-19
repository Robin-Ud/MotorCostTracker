# MotoRegis

Rastreador de gastos de veículos via terminal — puro Python, zero dependências.

*Vehicle expense tracker CLI — pure Python, zero dependencies.*

[![CI](https://github.com/Robin-Ud/MotorCostTracker/actions/workflows/ci.yml/badge.svg)](https://github.com/Robin-Ud/MotorCostTracker/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Zero deps](https://img.shields.io/badge/dependencies-zero-brightgreen)

---

## O que é

MotoRegis registra abastecimentos, manutenções e outros gastos de veículos diretamente no terminal. Cada registro vai para um CSV local e pode ser sincronizado automaticamente com um repositório Git. O script controla intervalos de manutenção por quilometragem e por tempo, emitindo alertas quando algum serviço está próximo do vencimento.

## Funcionalidades

- Menu interativo no terminal
- Múltiplos veículos configuráveis
- Alertas de manutenção por km e por tempo (dias/meses)
- Análise de custos detalhada (custo total e de combustível por 100 km, km/L média e do último tanque, custo por dia)
- Apenas stdlib Python — sem `pip install` nenhum

## Instalação

```bash
git clone https://github.com/Robin-Ud/MotorCostTracker.git
cd MotorCostTracker
python motoregis.py
```

Opcional — alias no `.bashrc` para rodar de qualquer lugar:

```bash
alias motoregis='python ~/MotorCostTracker/motoregis.py'
```

**Requisito:** Python 3.10+

### Seus dados

Os veículos e os registros ficam em `pessoal/`, fora do git. Sem ela, o script roda
em cima do `exemplo/` (uma Honda CG 160 e um Onix inventados). Para começar os seus:

```bash
mkdir pessoal && cp -r exemplo/* pessoal/   # e edite pessoal/configs.json
```

Se `pessoal/` for um clone de um repo privado seu, o `motoregis.sh` faz pull antes e
push depois de cada registro, e dá para registrar de mais de uma máquina.

## Uso

Ao rodar, o script exibe o menu principal:

```
=== MotoRegis — Royal Enfield Himalayan 411 ===
Odômetro: 1.234 km

0. Análise de custos
1. Registrar abastecimento
2. Registrar manutenção preventiva
3. Registrar acessório / upgrade
4. Registrar manutenção corretiva
5. Registrar burocracia (IPVA, seguro…)
6. Alterar veículo
7. Alterar data (para registros retroativos)
9. Sair
```

Em manutenção preventiva, o script mostra quais serviços estão vencidos ou próximos do vencimento com base no odômetro atual e na data do último registro de cada item.

## Estrutura de dados

Cada veículo tem um arquivo CSV append-only:

| Coluna | Descrição |
|--------|-----------|
| `data` | Data do registro (DD/MM/AA) |
| `odometro` | Leitura do odômetro (km) |
| `categoria` | 1=Abastec. 2=Prev. 3=Acess. 4=Corret. 5=Buro. |
| `custo` | Valor em R$ |
| `litros` | Litros abastecidos (0.00 nas demais categorias) |
| `detalhes` | Notas livres separadas por `\|` |

Exemplo:

```csv
data,odometro,categoria,custo,litros,detalhes
27/04/26,1089,2,107.87,0.00,ajustar_valvulas|trocar_oleo_e_filtro
30/04/26,1113,1,30.69,4.39,gasolina_aditivada|cheio
```

## Configuração de veículo

Cada veículo tem um JSON em `pessoal/veiculos/`. Exemplo de intervalos de manutenção:

```json
{
  "veiculo": "Royal Enfield Himalayan 411",
  "ano": 2022,
  "intervalo_revisao_km": 5000,
  "manutencoes": {
    "por_quilometragem": {
      "trocar_oleo_e_filtro": 5000,
      "ajustar_valvulas": 5000,
      "trocar_vela_ignicao": 15000
    },
    "por_tempo_meses": {
      "trocar_oleo_e_filtro": 6,
      "ajustar_valvulas": 6
    },
    "por_tempo_dias": {
      "limpar_lubrificar_corrente": 15
    }
  }
}
```

`pessoal/configs.json` mapeia os nomes dos veículos para seus arquivos:

```json
{
  "veiculos_index": {
    "Royal Enfield Himalayan 411": "veiculos/himalayan_22.json",
    "Toyota Etios": "veiculos/etios_16.json"
  }
}
```

## Estrutura do projeto

```
motoregis.py        ← script único
motoregis.sh        ← wrapper (pull/push do pessoal/ quando ele é um clone git)
exemplo/            ← dados inventados, no mesmo formato
pessoal/            ← seus dados, fora do git
  configs.json      ← config global e índice de veículos
  veiculos/
    himalayan_22.json ← intervalos de manutenção do veículo
    himalayan_22.csv  ← registros (append-only)
```

## Contribuindo

Issues e PRs são bem-vindos. Antes de abrir um PR:

- Python 3.10+ — usar `X | Y` em vez de `Optional[X]`
- Sem dependências externas (apenas stdlib)
- Type hints em todas as assinaturas
- Testes com pytest: `pytest tests/ -v`
