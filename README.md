# MotoRegis 🏍️

Um sistema minimalista via linha de comando (CLI)(inicialmente) para registro de abastecimentos, manutenções e customizações de motocicletas. Desenvolvido com foco em velocidade, **baixa fricção** e na filosofia KISS (*Keep It Simple, Stupid*).

Pensado para uso rápido em cotidiano via Termux, com os dados sendo versionados via Git para análises posteriores no PC(inicialmente).

---

## 🧠 Filosofia e Arquitetura

O projeto é estritamente dividido para manter a simplicidade e a segurança dos dados:
* **Interface e Lógica:** Script em Python puro.
* **Armazenamento:** Arquivo `.csv` (agnóstico e perfeito para análise de dados).
* **Configuração:** Arquivo `.json` estritamente **somente leitura** pelo script.
* **Manutenção das configurações** Script em Python puro dedicado a isso ou manualmente

---

## ⚙️ Configuração

Para evitar acidentes e simplificar o código, o script de acesso ao usuario não altera as configurações. A mudança de configurações deve ser realizada manualmente ou via script dedicado guardado em uma pasta oculta


**Exemplo de config.json:**

    ```
    motos = [virago 98, Himalayan 411]
    moto_padrão = motos[1]

---

## 🗃️ Estrutura de Dados (O CSV)

Todos os registros são salvos no arquivo configurado, seguindo a estrutura de colunas abaixo. Isso garante que a importação via Pandas ou outras ferramentas de análise seja direta.

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `data` | String | Data do registro | 2026-04-14 |
| `moto` | String | Identificador da moto (puxado do config) | Himalayan 411 |
| `odometro` | Int | Quilometragem atual | 15400 |
| `tipo` | Int | Categoria do gasto (1: Abast, 2: Manut_per, 3:Manut, 4:Acessor ) | 1 |
| `valor_gasto`| Float | Custo total da operação em Reais | 85.50 |
| `detalhes` | String | Litros, peça trocada ou local | oléo motor |
| `litros` | Float | total em L abastecidos | 14.2 |

---

## 🚀 Como Usar

graph TD
    %% Definição do Início
    Start[Início do Código<br>Mostra Moto e Data Selecionadas] --> Menu{Menu Principal}

    %% Opções do Menu
    Menu -->|1| Abast(Abastecimento)
    Menu -->|2| ManutP(Manutenção Periódica)
    Menu -->|3| Acess(Acessórios/Cosméticos)
    Menu -->|4| ManutS(Manutenção Séria)
    Menu -->|8| MudarV(Mudar Veículo)
    Menu -->|9| MudarD(Mudar Data)

    %% Loops de alteração
    MudarV -->|Muda a Moto| Start
    MudarD -->|Muda a Data| Start

    %% Gargalo do Odômetro e Valor (DRY)
    Abast --> Odo[Cap Odômetro]
    ManutP --> Odo
    Acess --> Odo
    ManutS --> Odo

    Odo --> Valor[Cap Valor]

    %% Ramificações Específicas
    Valor -->|Se 1| Litros[Cap Litros]
    Valor -->|Se 2| Opcao[Cap Opção Restrita]
    Valor -->|Se 3| Txt1[Cap Texto Livre]
    Valor -->|Se 4| Txt2[Cap Texto Livre]

    %% Fechamento
    Litros --> Salvar[Salva no CSV Correspondente]
    Opcao --> Salvar
    Txt1 --> Salvar
    Txt2 --> Salvar

    Salvar --> Alertas[Avisa se há manutenção atrasada]
    Alertas --> Fim[Imprime Sucesso e Sincroniza via Git]

---

## 🗺️ Roadmap e Ideias Futuras

- [ ] **Validadores Robustos:** Implementar funções isoladas para validar inputs (impedir odômetro regressivo, barrar valores negativos).
- [ ] **Sync Automático:** Integrar comandos do Git diretamente no Python para fazer *commit* e *push* silenciosos após cada novo registro.
- [ ] **Evolução da Interface:** A lógica de validação e I/O de dados está isolada. No futuro, avaliar a migração da CLI atual para uma TUI (ex: Textual/Rich) ou uma GUI Mobile (Flet), mantendo o mesmo arquivo CSV como base.
- [ ] **Analise dos dados** geradas no proprio cell caso migre pra TUI ou GUI ou somente no computador caso siga apenas via linha de comando
