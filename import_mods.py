import requests
from supabase import create_client, Client

SUPABASE_URL = "https://hdwzrycohldvxjesakrf.supabase.co"
SUPABASE_KEY = "sb_publishable_MQGUsNu7H_4dzARZo5Gu2g_MKc2QSmi"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Стоп-слова для проверки на стороне скрипта (англ.)
FORBIDDEN_WORDS = [
    "lgbt", "pride", "queer", "lesbian", "gay", 
    "bisexual", "transgender", "nonbinary"
]

def is_forbidden(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return any(word in text_lower for word in FORBIDDEN_WORDS)

def fetch_and_save_mods(limit=100):
    print("Запрос популярных модов с Modrinth...")
    
    url = f"https://api.modrinth.com/v2/search?limit={limit}&facets=[[\"project_type:mod\"]]"
    headers = {"User-Agent": "CowMods-Platform/1.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка получения данных с Modrinth: {response.status_code}")
        return

    hits = response.json().get("hits", [])
    saved = 0
    blocked = 0

    for item in hits:
        mod_id = item.get("project_id")
        title = item.get("title", "")
        description = item.get("description", "")

        # 1. Проверка скриптом
        if is_forbidden(title) or is_forbidden(description):
            print(f"⛔ Блокировка (стоп-слово): {title}")
            blocked += 1
            continue

        # 2. Попытка записи в Supabase (второй барьер — триггер в БД)
        try:
            supabase.table("mods").upsert({
                "id": mod_id,
                "title": title,
                "description": description
            }).execute()
            print(f"✅ Добавлен: {title}")
            saved += 1
        except Exception as err:
            print(f"⚠️ Ошибка или заблокировано базой [{title}]: {err}")
            blocked += 1

    print(f"\nЗавершено! Успешно сохранено: {saved}, Заблокировано: {blocked}")

if __name__ == "__main__":
    fetch_and_save_mods(limit=100)
