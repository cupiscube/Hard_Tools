import requests
import csv
import os

print("🔧 Toggl Клиенты: Автоматическая обработка CSV")

# Получаем API токен
api_token = input("🔑 Введите ваш Toggl API токен: ").strip()
auth = (api_token, "api_token")

# Получаем workspace_id
print("📡 Получаем workspace ID...")
me_response = requests.get("https://api.track.toggl.com/api/v9/me", auth=auth)
if me_response.status_code != 200:
    print("❌ Ошибка при получении информации. Проверьте API токен.")
    exit(1)

workspace_id = me_response.json().get("default_workspace_id")
print(f"✅ Workspace ID: {workspace_id}")

# Загружаем CSV-файл
file_name = "Cl_N.csv"
if not os.path.exists(file_name):
    print(f"❌ Файл {file_name} не найден. Положите его рядом с этим .exe")
    exit(1)

print(f"📄 Загружаем файл: {file_name}")
with open(file_name, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Получаем список всех клиентов
# clients_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients"
clients_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
clients_response = requests.get(clients_url, auth=auth)
existing_clients = clients_response.json() if clients_response.status_code == 200 else []

client_map = {client['name']: client['id'] for client in existing_clients}

# Обработка каждой строки из CSV
for row in rows:
    old_name = row.get("old_name", "").strip()
    new_name = row.get("new_name", "").strip()

    # 1. Добавление
    if not old_name and new_name:
        if new_name in client_map:
            print(f"⚠️ Клиент уже существует: {new_name}")
        else:
            response = requests.post(clients_url, auth=auth, json={"name": new_name})
            if response.status_code == 200:
                print(f"✅ Клиент добавлен: {new_name}")
            else:
                print(f"❌ Ошибка при добавлении {new_name}: {response.status_code} - {response.text}")

    # 2. Удаление
    elif old_name and not new_name:
        if old_name in client_map:
            client_id = client_map[old_name]
            delete_url = f"{clients_url}/{client_id}"
            response = requests.delete(delete_url, auth=auth)
            if response.status_code == 200:
                print(f"🗑️ Клиент удалён: {old_name}")
            else:
                print(f"❌ Ошибка при удалении {old_name}: {response.status_code} - {response.text}")
        else:
            print(f"⚠️ Не найден клиент для удаления: {old_name}")

    # 3. Переименование
    elif old_name and new_name:
        if old_name in client_map:
            client_id = client_map[old_name]
            update_url = f"{clients_url}/{client_id}"
            response = requests.put(update_url, auth=auth, json={"name": new_name})
            if response.status_code == 200:
                print(f"🔁 Клиент переименован: {old_name} → {new_name}")
            else:
                print(f"❌ Ошибка при переименовании {old_name}: {response.status_code} - {response.text}")
        else:
            print(f"⚠️ Клиент для переименования не найден: {old_name}")

print("\n🏁 Готово!")
input("Нажмите Enter для выхода...")
