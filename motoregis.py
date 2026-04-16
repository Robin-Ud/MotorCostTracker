"""
MotoRegis - Motor Cost Tracker
---------------------------------------------------------
Manifesto de Desenvolvimento:
1. KISS (Keep It Simple, Stupid): Priorize a simplicidade.
   Se uma lógica pode ser resolvida com menos linhas e menos pacotes, faça-o.
2. DRY (Don't Repeat Yourself): Funções de captura e validação devem ser genéricas.
3. Baixa Fricção: O fluxo deve ser otimizado para uso rápido via Termux.
4. Portabilidade: Dados em CSV para garantir que o usuário seja dono da informação.
5. Agnosticismo de Interface: A lógica de validação deve ser isolada da captura
   de input, facilitando futura migração para TUI/GUI.

Desenvolvido por: @Robin-Ud
Licença: GNU GPLv3
---------------------------------------------------------
"""

import csv
import json
import os
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ==========================================
# ZONA 1: MOTORES DE DADOS (JSON e CSV)
# Funções burras. Elas só leem e escrevem, não tomam decisões.
# ==========================================

def json_to_dict(caminho):
    try:
        with open(os.path.join(BASE_DIR, caminho), 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def gets_data(caminho):
    try:
        with open(os.path.join(BASE_DIR, caminho), 'r', encoding='utf-8') as f:
            return [linha.strip().split(',') for linha in f if linha.strip()]
    except FileNotFoundError:
        return []

def save_record(caminho, registro):
    with open(os.path.join(BASE_DIR, caminho), 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(registro)

def git_sync(csv_path, veiculo_nome, data_str, odometro):
    msg = f"registro: {veiculo_nome} | {data_str} | {odometro}km"
    subprocess.run(['git', '-C', BASE_DIR, 'add', csv_path], capture_output=True)
    result = subprocess.run(['git', '-C', BASE_DIR, 'commit', '-m', msg], capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.run(['git', '-C', BASE_DIR, 'push'], capture_output=True)


# ==========================================
# ZONA 2: VALIDADORES (As fundações)
# Garantem que o usuário não digite letras onde vai número, etc.
# ==========================================

def select_index(msg, range_max):
    while True:
        try:
            valor = int(input(msg))
            if valor in range(0, range_max + 1):
                return valor
            print(f'❌ Digite apenas valores de 0 a {range_max}')
        except ValueError:
            print('❌ Por favor, digite apenas números inteiros')

def get_float(msg):
    while True:
        entrada = input(msg).strip().replace(',', '.')
        try:
            valor = float(entrada)
            if valor >= 0:
                return valor
            print('❌ Digite apenas valores maiores ou iguais a 0')
        except ValueError:
            print('❌ Digite apenas numerais')

def get_int(msg):
    while True:
        try:
            valor = int(input(msg).strip())
            if valor >= 0:
                return valor
            print('❌ Digite apenas valores maiores ou iguais a 0')
        except ValueError:
            print('❌ Por favor, digite apenas números inteiros')


# ==========================================
# ZONA 3: FLUXOS / ORQUESTRAÇÃO
# Juntam as validações e mandam salvar nos motores.
# ==========================================

def legivel(chave, veiculo=None):
    if veiculo and 'nomes_display' in veiculo:
        return veiculo['nomes_display'].get(chave, ' '.join(chave.split('_')).capitalize())
    return ' '.join(chave.split('_')).capitalize()

def load_config():
    config = json_to_dict('configs.json')
    if config is None:
        print("❌ Erro: configs.json não encontrado.")
        exit(1)
    return config

def select_veiculo(config):
    veiculos = list(config['veiculos_index'].keys())
    print("\n=== Selecionar Veículo ===")
    for i, nome in enumerate(veiculos, 1):
        print(f"  {i}. {nome}")
    print("  0. Cancelar")
    idx = select_index("Veículo: ", len(veiculos))
    if idx == 0:
        return None, None, None
    nome = veiculos[idx - 1]
    json_path = config['veiculos_index'][nome]
    return nome, json_path, json_path.replace('.json', '.csv')

def get_last_odometer(csv_path):
    data = gets_data(csv_path)
    if len(data) <= 1:
        return 0
    try:
        return int(data[-1][1])
    except (IndexError, ValueError):
        return 0

def get_last_fuel_record(csv_path):
    data = gets_data(csv_path)
    for linha in reversed(data[1:]):
        try:
            if linha[2] == '1' and float(linha[4]) > 0:
                return int(linha[1]), float(linha[4])
        except (IndexError, ValueError):
            continue
    return None, None

def check_manutencoes(csv_path, json_path, odometro_atual, data_atual):
    veiculo = json_to_dict(json_path)
    if veiculo is None:
        return

    data = gets_data(csv_path)
    if len(data) <= 1:
        return

    manutencoes = veiculo.get('manutencoes', {})
    data_atual_dt = datetime.strptime(data_atual, '%Y-%m-%d')
    primeira_data = datetime.strptime(data[1][0], '%Y-%m-%d')
    primeiro_odo = int(data[1][1])
    alertas = []

    def last_manutencao(nome):
        for linha in reversed(data[1:]):
            if linha[2] == '2' and linha[5] == nome:
                return linha
        return None

    for nome, intervalo in manutencoes.get('por_quilometragem', {}).items():
        ultimo = last_manutencao(nome)
        ref_odo = int(ultimo[1]) if ultimo else primeiro_odo
        km_desde = odometro_atual - ref_odo
        if km_desde >= intervalo:
            alertas.append((legivel(nome, veiculo), f"{km_desde} km atrás ({intervalo} km)"))

    for nome, meses in manutencoes.get('por_tempo_meses', {}).items():
        ultimo = last_manutencao(nome)
        ref_dt = datetime.strptime(ultimo[0], '%Y-%m-%d') if ultimo else primeira_data
        delta_meses = (data_atual_dt.year - ref_dt.year) * 12 + (data_atual_dt.month - ref_dt.month)
        if delta_meses >= meses:
            alertas.append((legivel(nome, veiculo), f"{delta_meses} meses atrás ({meses} meses)"))

    for nome, dias in manutencoes.get('por_tempo_dias', {}).items():
        ultimo = last_manutencao(nome)
        ref_dt = datetime.strptime(ultimo[0], '%Y-%m-%d') if ultimo else primeira_data
        delta_dias = (data_atual_dt - ref_dt).days
        if delta_dias >= dias:
            alertas.append((legivel(nome, veiculo), f"{delta_dias} dias atrás ({dias} dias)"))

    if alertas:
        print("\n--- Manutenções pendentes ---\n")
        for nome_display, info in alertas:
            print(f"  ⚠️  {nome_display}")
            print(f"      {info}")
        print()

def captura_odometro(csv_path):
    ultimo_km = get_last_odometer(csv_path)
    print(f"  Último odômetro: {ultimo_km} km")
    while True:
        odometro = get_int("  Odômetro atual (km): ")
        if odometro >= ultimo_km:
            return odometro
        print(f"❌ Odômetro não pode ser menor que o último registro ({ultimo_km} km)")

def _finalizar(csv_path, json_path, veiculo_nome, data_str, odometro):
    check_manutencoes(csv_path, json_path, odometro, data_str)
    git_sync(csv_path, veiculo_nome, data_str, odometro)
    print("\n✅ Sincronizado!")

def captura_abastecimento(csv_path, json_path, veiculo_nome, data_str, config):
    print("\n--- Abastecimento ---")
    ultimo_odo, _ = get_last_fuel_record(csv_path)
    odometro = captura_odometro(csv_path)
    custo = get_float("  Custo total (R$): ")
    litros = get_float("  Litros: ")

    print()
    combustiveis = config['combustiveis']
    for i, c in enumerate(combustiveis, 1):
        print(f"  {i}. {c}")
    idx = select_index("  Combustível: ", len(combustiveis))
    detalhes = combustiveis[idx - 1] if idx > 0 else "outro"

    save_record(csv_path, [data_str, odometro, 1, f"{custo:.2f}", f"{litros:.2f}", detalhes])

    if ultimo_odo and litros > 0:
        km_percorridos = odometro - ultimo_odo
        print(f"\n  Consumo: {km_percorridos / litros:.2f} km/L ({km_percorridos} km / {litros} L)")

    _finalizar(csv_path, json_path, veiculo_nome, data_str, odometro)

def captura_manutencao_periodica(csv_path, json_path, veiculo_nome, data_str):
    print("\n--- Manutenção Periódica ---")
    veiculo = json_to_dict(json_path)
    opcoes = list(veiculo.get('manutencoes', {}).get('por_quilometragem', {}).keys())

    print()
    for i, nome in enumerate(opcoes, 1):
        print(f"  {i:2}. {legivel(nome, veiculo)}")
    print("   0. Outro")
    print()
    idx = select_index("Manutenção: ", len(opcoes))
    detalhes = input("  Descreva: ").strip().replace(' ', '_').lower() if idx == 0 else opcoes[idx - 1]

    odometro = captura_odometro(csv_path)
    custo = get_float("  Custo (R$): ")

    save_record(csv_path, [data_str, odometro, 2, f"{custo:.2f}", "0.00", detalhes])
    _finalizar(csv_path, json_path, veiculo_nome, data_str, odometro)

def captura_generica(csv_path, json_path, veiculo_nome, categoria_idx, categoria_nome, data_str):
    print(f"\n--- {categoria_nome} ---\n")
    odometro = captura_odometro(csv_path)
    custo = get_float("  Custo (R$): ")
    detalhes = input("  Detalhes: ").strip().replace(' ', '_').lower()

    save_record(csv_path, [data_str, odometro, categoria_idx, f"{custo:.2f}", "0.00", detalhes])
    _finalizar(csv_path, json_path, veiculo_nome, data_str, odometro)


# ==========================================
# ZONA 4: INTERFACE (O Menu Principal)
# Onde o script começa a rodar de verdade.
# ==========================================

def main():
    config = load_config()
    categorias = config['categorias_menu']
    veiculos = list(config['veiculos_index'].keys())

    veiculo_nome = veiculos[0]
    json_path = config['veiculos_index'][veiculo_nome]
    csv_path = json_path.replace('.json', '.csv')
    data_atual = datetime.now().strftime('%Y-%m-%d')

    while True:
        print(f"\n[ {veiculo_nome} | {data_atual} ]")
        for i, cat in enumerate(categorias, 1):
            print(f"  {i}. {cat}")
        print("  0. Sair")

        opcao = select_index("Opção: ", len(categorias))

        if opcao == 0:
            break
        elif opcao == 1:
            captura_abastecimento(csv_path, json_path, veiculo_nome, data_atual, config)
            break
        elif opcao == 2:
            captura_manutencao_periodica(csv_path, json_path, veiculo_nome, data_atual)
            break
        elif 3 <= opcao <= 5:
            captura_generica(csv_path, json_path, veiculo_nome, opcao, categorias[opcao - 1], data_atual)
            break
        elif opcao == 6:
            novo_nome, novo_json, novo_csv = select_veiculo(config)
            if novo_nome:
                veiculo_nome, json_path, csv_path = novo_nome, novo_json, novo_csv
        elif opcao == 7:
            nova_data = input(f"  Nova data YYYY-MM-DD [{data_atual}]: ").strip()
            if nova_data:
                try:
                    datetime.strptime(nova_data, '%Y-%m-%d')
                    data_atual = nova_data
                except ValueError:
                    print("❌ Formato inválido. Use YYYY-MM-DD")

if __name__ == '__main__':
    main()
