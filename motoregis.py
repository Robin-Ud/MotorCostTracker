import csv
import json
import os
import subprocess
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# ==========================================
# ZONE 1: DATA ENGINES
# ==========================================

def load_json(path: str) -> dict | None:
    try:
        with open(os.path.join(DATA_DIR, path), 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def read_csv(path: str) -> list[list[str]]:
    try:
        with open(os.path.join(DATA_DIR, path), 'r', encoding='utf-8') as f:
            return [row.strip().split(',') for row in f if row.strip()]
    except FileNotFoundError:
        return []

def append_record(path: str, row: list) -> None:
    with open(os.path.join(DATA_DIR, path), 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(row)

def git_sync(vehicle_name: str, date_str: str, odometer: int, config: dict) -> None:
    if not os.path.exists(os.path.join(DATA_DIR, '.git')):
        subprocess.run(['git', '-C', DATA_DIR, 'init'], capture_output=True)
    remote_url = config.get('git_remote', '')
    if remote_url:
        has_remote = subprocess.run(['git', '-C', DATA_DIR, 'remote', 'get-url', 'origin'], capture_output=True)
        if has_remote.returncode != 0:
            subprocess.run(['git', '-C', DATA_DIR, 'remote', 'add', 'origin', remote_url], capture_output=True)
    msg = f"record: {vehicle_name} | {date_str} | {odometer}km"
    subprocess.run(['git', '-C', DATA_DIR, 'add', '.'], capture_output=True)
    result = subprocess.run(['git', '-C', DATA_DIR, 'commit', '-m', msg], capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.run(['git', '-C', DATA_DIR, 'push'], capture_output=True)


# ==========================================
# ZONE 2: VALIDATORS
# ==========================================

def select_index(prompt: str, max_value: int) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value in range(0, max_value + 1):
                return value
            print(f'❌ Entre 0 e {max_value}')
        except ValueError:
            print('❌ Digite um número inteiro')

def get_float(prompt: str) -> float:
    while True:
        entry = input(prompt).strip().replace(',', '.')
        try:
            value = float(entry)
            if value >= 0:
                return value
            print('❌ Valor deve ser maior ou igual a 0')
        except ValueError:
            print('❌ Apenas números')

def get_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if value >= 0:
                return value
            print('❌ Valor deve ser maior ou igual a 0')
        except ValueError:
            print('❌ Digite um número inteiro')


# ==========================================
# ZONE 3: ORCHESTRATION
# ==========================================

def display_name(key: str, vehicle: dict | None = None) -> str:
    if vehicle and 'nomes_display' in vehicle:
        return vehicle['nomes_display'].get(key, ' '.join(key.split('_')).capitalize())
    return ' '.join(key.split('_')).capitalize()

def load_config() -> dict:
    config = load_json('configs.json')
    if config is None:
        print("❌ configs.json não encontrado.")
        exit(1)
    return config

def select_vehicle(config: dict) -> tuple[str | None, str | None, str | None]:
    vehicles = list(config['veiculos_index'].keys())
    print("\n=== Selecionar Veículo ===")
    for i, name in enumerate(vehicles, 1):
        print(f"  {i}. {name}")
    print("  0. Cancelar")
    idx = select_index("Veículo: ", len(vehicles))
    if idx == 0:
        return None, None, None
    name = vehicles[idx - 1]
    json_path = config['veiculos_index'][name]
    return name, json_path, json_path.replace('.json', '.csv')

def get_last_odometer(path: str) -> int:
    data = read_csv(path)
    if len(data) <= 1:
        return 0
    try:
        return int(data[-1][1])
    except (IndexError, ValueError):
        return 0

def get_last_fuel_record(path: str) -> tuple[int | None, float | None, str | None, bool]:
    data = read_csv(path)
    for row in reversed(data[1:]):
        try:
            if row[2] == '1' and float(row[4]) > 0:
                was_full = '|parcial' not in (row[5] if len(row) > 5 else '')
                return int(row[1]), float(row[4]), row[0], was_full
        except (IndexError, ValueError):
            continue
    return None, None, None, True

def check_maintenance(csv_path: str, json_path: str, current_odometer: int, current_date: str) -> None:
    vehicle = load_json(json_path)
    if vehicle is None:
        return
    data = read_csv(csv_path)
    if len(data) <= 1:
        return

    maintenance = vehicle.get('manutencoes', {})
    current_date_dt = datetime.strptime(current_date, '%d/%m/%y')
    first_date = datetime.strptime(data[1][0], '%d/%m/%y')
    first_odometer = int(data[1][1])
    alerts = []

    def last_maintenance(name: str) -> list | None:
        for row in reversed(data[1:]):
            if row[2] == '2' and row[5] == name:
                return row
        return None

    for name, interval in maintenance.get('por_quilometragem', {}).items():
        last = last_maintenance(name)
        ref_odometer = int(last[1]) if last else first_odometer
        km_since = current_odometer - ref_odometer
        if km_since >= interval:
            alerts.append((display_name(name, vehicle), f"{km_since} km atrás (a cada {interval} km)"))

    for name, months in maintenance.get('por_tempo_meses', {}).items():
        last = last_maintenance(name)
        ref_date = datetime.strptime(last[0], '%d/%m/%y') if last else first_date
        delta_months = (current_date_dt.year - ref_date.year) * 12 + (current_date_dt.month - ref_date.month)
        if delta_months >= months:
            alerts.append((display_name(name, vehicle), f"{delta_months} meses atrás (a cada {months} meses)"))

    for name, days in maintenance.get('por_tempo_dias', {}).items():
        last = last_maintenance(name)
        ref_date = datetime.strptime(last[0], '%d/%m/%y') if last else first_date
        delta_days = (current_date_dt - ref_date).days
        if delta_days >= days:
            alerts.append((display_name(name, vehicle), f"{delta_days} dias atrás (a cada {days} dias)"))

    if alerts:
        print("\n--- Manutenções pendentes ---\n")
        for name_display, info in alerts:
            print(f"  ⚠️  {name_display}")
            print(f"      {info}")
        print()

def prompt_odometer(path: str) -> int:
    last_km = get_last_odometer(path)
    print(f"  Último odômetro: {last_km} km")
    while True:
        odometer = get_int("  Odômetro atual (km): ")
        if odometer >= last_km:
            return odometer
        print(f"❌ Odômetro não pode ser menor que o último registro ({last_km} km)")

def _finalize(csv_path: str, json_path: str, vehicle_name: str, date_str: str, odometer: int, config: dict) -> None:
    check_maintenance(csv_path, json_path, odometer, date_str)
    if config.get('git_sync', False):
        git_sync(vehicle_name, date_str, odometer, config)
    print("\n✅ Salvo!")

def record_fuel(csv_path: str, json_path: str, vehicle_name: str, date_str: str, config: dict, full_tank: bool = True) -> None:
    print("\n--- Abastecimento ---")
    last_odo, _, last_date, last_was_full = get_last_fuel_record(csv_path)
    odometer = prompt_odometer(csv_path)
    cost = get_float("  Custo total: ")
    liters = get_float("  Litros: ")

    print()
    fuel_types = config['combustiveis']
    for i, ft in enumerate(fuel_types, 1):
        print(f"  {i}. {ft}")
    idx = select_index("  Combustível: ", len(fuel_types))
    fuel = fuel_types[idx - 1] if idx > 0 else "outro"
    details = f"{fuel}|{'cheio' if full_tank else 'parcial'}"

    append_record(csv_path, [date_str, odometer, 1, f"{cost:.2f}", f"{liters:.2f}", details])

    if last_odo and liters > 0:
        km_driven = odometer - last_odo
        sym = config.get('currency_symbol', 'R$')
        if full_tank and last_was_full:
            print(f"\n  Consumo:      {km_driven / liters:.2f} km/L  ({km_driven} km / {liters:.2f} L)")
            if km_driven > 0:
                print(f"  Custo/100km:  {sym}{cost / km_driven * 100:.2f}  ({sym}{cost:.2f} / {km_driven} km)")
        else:
            print(f"\n  (consumo omitido — abastecimento parcial)")
        if last_date:
            days = (datetime.strptime(date_str, '%d/%m/%y') - datetime.strptime(last_date, '%d/%m/%y')).days
            threshold = config.get('daily_km_threshold', 40)
            if days > 0 and km_driven / days <= threshold:
                print(f"  Custo/dia:    {sym}{cost / days:.2f}  ({sym}{cost:.2f} / {days} dias)")

    _finalize(csv_path, json_path, vehicle_name, date_str, odometer, config)

def record_scheduled_maintenance(csv_path: str, json_path: str, vehicle_name: str, date_str: str, config: dict) -> None:
    print("\n--- Manutenção Preventiva ---")
    vehicle = load_json(json_path)
    options = list(vehicle.get('manutencoes', {}).get('por_quilometragem', {}).keys())

    print()
    for i, name in enumerate(options, 1):
        print(f"  {i:2}. {display_name(name, vehicle)}")
    print("   0. Outra")
    print()
    idx = select_index("Manutenção: ", len(options))
    details = input("  Descreva: ").strip().replace(' ', '_').lower() if idx == 0 else options[idx - 1]

    odometer = prompt_odometer(csv_path)
    cost = get_float("  Custo: ")

    append_record(csv_path, [date_str, odometer, 2, f"{cost:.2f}", "0.00", details])
    _finalize(csv_path, json_path, vehicle_name, date_str, odometer, config)

def setup_sync(config: dict) -> None:
    print("\n=== Configurar Sync ===")
    current = config.get('git_remote') or '(não configurado)'
    print(f"  Remote atual: {current}")
    url = input("  URL do repo privado (vazio para cancelar): ").strip()
    if not url:
        return
    config['git_remote'] = url
    config['git_sync'] = True
    with open(os.path.join(DATA_DIR, 'configs.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    if not os.path.exists(os.path.join(DATA_DIR, '.git')):
        subprocess.run(['git', '-C', DATA_DIR, 'init'], capture_output=True)
    subprocess.run(['git', '-C', DATA_DIR, 'remote', 'remove', 'origin'], capture_output=True)
    subprocess.run(['git', '-C', DATA_DIR, 'remote', 'add', 'origin', url], capture_output=True)
    subprocess.run(['git', '-C', DATA_DIR, 'add', '.'], capture_output=True)
    result = subprocess.run(['git', '-C', DATA_DIR, 'commit', '-m', 'setup: sync inicial'], capture_output=True, text=True)
    if result.returncode == 0:
        push = subprocess.run(['git', '-C', DATA_DIR, 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
        if push.returncode == 0:
            print("\n✅ Sync configurado e push inicial feito!")
        else:
            print("\n⚠️  Remote configurado mas push falhou — verifique acesso SSH/token.")
    else:
        print("\n✅ Sync configurado. Vai sincronizar no próximo registro.")

def record_generic(csv_path: str, json_path: str, vehicle_name: str, category_idx: int, category_name: str, date_str: str, config: dict) -> None:
    print(f"\n--- {category_name} ---\n")
    odometer = prompt_odometer(csv_path)
    cost = get_float("  Custo: ")
    details = input("  Detalhes: ").strip().replace(' ', '_').lower()

    append_record(csv_path, [date_str, odometer, category_idx, f"{cost:.2f}", "0.00", details])
    _finalize(csv_path, json_path, vehicle_name, date_str, odometer, config)


# ==========================================
# ZONE 4: INTERFACE
# ==========================================

def main() -> None:
    config = load_config()
    categories = config['categorias_menu']
    vehicles = list(config['veiculos_index'].keys())

    vehicle_name = vehicles[0]
    json_path = config['veiculos_index'][vehicle_name]
    csv_path = json_path.replace('.json', '.csv')
    current_date = datetime.now().strftime('%d/%m/%y')
    full_tank = True

    while True:
        tank_label = "cheio" if full_tank else "parcial"
        print(f"\n[ {vehicle_name} | {current_date} | tanque: {tank_label} ]")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        print(f"  9. Tanque: {tank_label}")
        print("  8. Configurar Sync")
        print("  0. Sair")

        choice = select_index("Opção: ", len(categories) + 2)

        if choice == 0:
            break
        elif choice == 1:
            record_fuel(csv_path, json_path, vehicle_name, current_date, config, full_tank)
            break
        elif choice == 2:
            record_scheduled_maintenance(csv_path, json_path, vehicle_name, current_date, config)
            break
        elif 3 <= choice <= 5:
            record_generic(csv_path, json_path, vehicle_name, choice, categories[choice - 1], current_date, config)
            break
        elif choice == 6:
            new_name, new_json, new_csv = select_vehicle(config)
            if new_name:
                vehicle_name, json_path, csv_path = new_name, new_json, new_csv
        elif choice == 7:
            today = datetime.now()
            new_str = input(f"  Nova data DD/MM [{current_date}]: ").strip()
            if new_str:
                try:
                    parsed = datetime.strptime(f"{new_str}/{today.year}", '%d/%m/%Y')
                    if parsed.date() > today.date():
                        print("❌ Data não pode ser no futuro")
                    else:
                        current_date = parsed.strftime('%d/%m/%y')
                except ValueError:
                    print("❌ Formato inválido. Use DD/MM")
        elif choice == 8:
            setup_sync(config)
        elif choice == 9:
            full_tank = not full_tank

if __name__ == '__main__':
    main()
