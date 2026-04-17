"""
MotoRegis — Vehicle Cost Tracker
---------------------------------------------------------
Design principles:
1. KISS (Keep It Simple, Stupid): Prefer fewer lines and no unnecessary packages.
2. DRY (Don't Repeat Yourself): Input capture and validation functions are generic.
3. Low friction: Optimized for fast daily use in a terminal environment.
4. Portability: Data stored in CSV so the user owns their information.
5. Interface agnosticism: Validation logic is isolated from input capture,
   enabling future migration to TUI/GUI.

License: GNU GPLv3
---------------------------------------------------------
"""

import csv
import json
import os
import subprocess
from datetime import datetime

DATA_DIR = os.path.join(os.path.expanduser("~"), ".motoregis")


# ==========================================
# ZONE 1: DATA ENGINES (JSON and CSV)
# Dumb functions. They only read and write, they don't make decisions.
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

def git_sync(csv_path: str, vehicle_name: str, date_str: str, odometer: int) -> None:
    msg = f"record: {vehicle_name} | {date_str} | {odometer}km"
    subprocess.run(['git', '-C', DATA_DIR, 'add', csv_path], capture_output=True)
    result = subprocess.run(['git', '-C', DATA_DIR, 'commit', '-m', msg], capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.run(['git', '-C', DATA_DIR, 'push'], capture_output=True)


# ==========================================
# ZONE 2: VALIDATORS
# Ensure the user doesn't type text where a number is expected, etc.
# ==========================================

def select_index(prompt: str, max_value: int) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value in range(0, max_value + 1):
                return value
            print(f'❌ Enter a value between 0 and {max_value}')
        except ValueError:
            print('❌ Please enter an integer')

def get_float(prompt: str) -> float:
    while True:
        entry = input(prompt).strip().replace(',', '.')
        try:
            value = float(entry)
            if value >= 0:
                return value
            print('❌ Enter a value greater than or equal to 0')
        except ValueError:
            print('❌ Numbers only')

def get_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if value >= 0:
                return value
            print('❌ Enter a value greater than or equal to 0')
        except ValueError:
            print('❌ Please enter an integer')


# ==========================================
# ZONE 3: ORCHESTRATION
# Combine validators and route data to the engines.
# ==========================================

def display_name(key: str, vehicle: dict | None = None) -> str:
    if vehicle and 'nomes_display' in vehicle:
        return vehicle['nomes_display'].get(key, ' '.join(key.split('_')).capitalize())
    return ' '.join(key.split('_')).capitalize()

def load_config() -> dict:
    config = load_json('configs.json')
    if config is None:
        print("❌ Error: configs.json not found.")
        print(f"\nFirst-time setup:")
        print(f"  1. Create the data directory:  mkdir -p ~/.motoregis/veiculos")
        print(f"  2. Copy the example config:    cp configs.example.json ~/.motoregis/configs.json")
        print(f"  3. Copy the example vehicle:   cp veiculos/example_vehicle.json ~/.motoregis/veiculos/")
        print(f"  4. Edit both files with your vehicle's details.")
        exit(1)
    return config

def select_vehicle(config: dict) -> tuple[str | None, str | None, str | None]:
    vehicles = list(config['veiculos_index'].keys())
    print("\n=== Select Vehicle ===")
    for i, name in enumerate(vehicles, 1):
        print(f"  {i}. {name}")
    print("  0. Cancel")
    idx = select_index("Vehicle: ", len(vehicles))
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

def get_last_fuel_record(path: str) -> tuple[int | None, float | None]:
    data = read_csv(path)
    for row in reversed(data[1:]):
        try:
            if row[2] == '1' and float(row[4]) > 0:
                return int(row[1]), float(row[4])
        except (IndexError, ValueError):
            continue
    return None, None

def check_maintenance(csv_path: str, json_path: str, current_odometer: int, current_date: str) -> None:
    vehicle = load_json(json_path)
    if vehicle is None:
        return

    data = read_csv(csv_path)
    if len(data) <= 1:
        return

    maintenance = vehicle.get('manutencoes', {})
    current_date_dt = datetime.strptime(current_date, '%Y-%m-%d')
    first_date = datetime.strptime(data[1][0], '%Y-%m-%d')
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
            alerts.append((display_name(name, vehicle), f"{km_since} km ago ({interval} km)"))

    for name, months in maintenance.get('por_tempo_meses', {}).items():
        last = last_maintenance(name)
        ref_date = datetime.strptime(last[0], '%Y-%m-%d') if last else first_date
        delta_months = (current_date_dt.year - ref_date.year) * 12 + (current_date_dt.month - ref_date.month)
        if delta_months >= months:
            alerts.append((display_name(name, vehicle), f"{delta_months} months ago ({months} months)"))

    for name, days in maintenance.get('por_tempo_dias', {}).items():
        last = last_maintenance(name)
        ref_date = datetime.strptime(last[0], '%Y-%m-%d') if last else first_date
        delta_days = (current_date_dt - ref_date).days
        if delta_days >= days:
            alerts.append((display_name(name, vehicle), f"{delta_days} days ago ({days} days)"))

    if alerts:
        print("\n--- Pending maintenance ---\n")
        for name_display, info in alerts:
            print(f"  ⚠️  {name_display}")
            print(f"      {info}")
        print()

def prompt_odometer(path: str) -> int:
    last_km = get_last_odometer(path)
    print(f"  Last odometer: {last_km} km")
    while True:
        odometer = get_int("  Current odometer (km): ")
        if odometer >= last_km:
            return odometer
        print(f"❌ Odometer cannot be lower than the last record ({last_km} km)")

def _finalize(csv_path: str, json_path: str, vehicle_name: str, date_str: str, odometer: int, config: dict) -> None:
    check_maintenance(csv_path, json_path, odometer, date_str)
    if config.get('git_sync', False):
        git_sync(csv_path, vehicle_name, date_str, odometer)
    print("\n✅ Saved!")

def record_fuel(csv_path: str, json_path: str, vehicle_name: str, date_str: str, config: dict) -> None:
    print("\n--- Fuel ---")
    last_odo, _ = get_last_fuel_record(csv_path)
    odometer = prompt_odometer(csv_path)
    cost = get_float("  Total cost: ")
    liters = get_float("  Liters: ")

    print()
    fuel_types = config['combustiveis']
    for i, ft in enumerate(fuel_types, 1):
        print(f"  {i}. {ft}")
    idx = select_index("  Fuel type: ", len(fuel_types))
    details = fuel_types[idx - 1] if idx > 0 else "other"

    append_record(csv_path, [date_str, odometer, 1, f"{cost:.2f}", f"{liters:.2f}", details])

    if last_odo and liters > 0:
        km_driven = odometer - last_odo
        print(f"\n  Consumption: {km_driven / liters:.2f} km/L ({km_driven} km / {liters} L)")

    _finalize(csv_path, json_path, vehicle_name, date_str, odometer, config)

def record_scheduled_maintenance(csv_path: str, json_path: str, vehicle_name: str, date_str: str, config: dict) -> None:
    print("\n--- Scheduled Maintenance ---")
    vehicle = load_json(json_path)
    options = list(vehicle.get('manutencoes', {}).get('por_quilometragem', {}).keys())

    print()
    for i, name in enumerate(options, 1):
        print(f"  {i:2}. {display_name(name, vehicle)}")
    print("   0. Other")
    print()
    idx = select_index("Maintenance: ", len(options))
    details = input("  Describe: ").strip().replace(' ', '_').lower() if idx == 0 else options[idx - 1]

    odometer = prompt_odometer(csv_path)
    cost = get_float("  Cost: ")

    append_record(csv_path, [date_str, odometer, 2, f"{cost:.2f}", "0.00", details])
    _finalize(csv_path, json_path, vehicle_name, date_str, odometer, config)

def record_generic(csv_path: str, json_path: str, vehicle_name: str, category_idx: int, category_name: str, date_str: str, config: dict) -> None:
    print(f"\n--- {category_name} ---\n")
    odometer = prompt_odometer(csv_path)
    cost = get_float("  Cost: ")
    details = input("  Details: ").strip().replace(' ', '_').lower()

    append_record(csv_path, [date_str, odometer, category_idx, f"{cost:.2f}", "0.00", details])
    _finalize(csv_path, json_path, vehicle_name, date_str, odometer, config)


# ==========================================
# ZONE 4: INTERFACE (Main Menu)
# Entry point where the script starts running.
# ==========================================

def main() -> None:
    config = load_config()
    categories = config['categorias_menu']
    vehicles = list(config['veiculos_index'].keys())

    vehicle_name = vehicles[0]
    json_path = config['veiculos_index'][vehicle_name]
    csv_path = json_path.replace('.json', '.csv')
    current_date = datetime.now().strftime('%Y-%m-%d')

    while True:
        print(f"\n[ {vehicle_name} | {current_date} ]")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        print("  0. Exit")

        choice = select_index("Option: ", len(categories))

        if choice == 0:
            break
        elif choice == 1:
            record_fuel(csv_path, json_path, vehicle_name, current_date, config)
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
            new_date = input(f"  New date YYYY-MM-DD [{current_date}]: ").strip()
            if new_date:
                try:
                    datetime.strptime(new_date, '%Y-%m-%d')
                    current_date = new_date
                except ValueError:
                    print("❌ Invalid format. Use YYYY-MM-DD")

if __name__ == '__main__':
    main()
