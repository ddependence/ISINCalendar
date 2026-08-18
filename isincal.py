import sys
import requests
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Проверка аргумента командной строки ---
if len(sys.argv) < 2:
    print("Использование: python add_coupons_to_calendar.py <файл_со_списком_ISIN.txt>")
    sys.exit(1)

file_path = sys.argv[1]

# --- Чтение ISIN из файла ---
with open(file_path, 'r', encoding='utf-8') as f:
    isin_list = [line.strip() for line in f if line.strip()]

if not isin_list:
    print("Файл пуст или не содержит ISIN.")
    sys.exit(1)

print(f"Найдено {len(isin_list)} ISIN для обработки.")

# --- Функции для работы с API Мосбиржи ---

def find_security_id(isin):
    """Поиск инструмента по ISIN, возвращает secid и название."""
    url = "https://iss.moex.com/iss/securities.json"
    params = {
        "q": isin,
        "iss.meta": "off",
        "securities.columns": "secid,shortname,isbn"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("securities", {}).get("data", [])
    for row in rows:
        if len(row) >= 3 and row[2] == isin:
            return row[0], row[1]
    return None, None

def get_coupons(secid):
    """Получить список купонов для бумаги по secid."""
    url = f"https://iss.moex.com/iss/securities/{secid}/coupons.json"
    params = {
        "iss.meta": "off",
        "coupons.columns": "couponvalue,coupondate"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("coupons", {}).get("data", [])
    coupons = []
    for row in rows:
        if len(row) >= 2:
            value = row[0]
            date_str = row[1]
            coupons.append((value, date_str))
    return coupons

# --- Настройка Google Calendar ---

SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)
calendar_id = 'primary'

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С КАЛЕНДАРЁМ ---

def get_all_coupon_events():
    """
    Возвращает словарь: {event_id: (isin, summary, date)}
    для всех событий, созданных этим скриптом (содержат ISIN в description).
    """
    events_dict = {}
    page_token = None
    while True:
        events = service.events().list(
            calendarId=calendar_id,
            pageToken=page_token,
            timeMin=datetime.datetime(2000, 1, 1).isoformat() + 'Z',
            timeMax=datetime.datetime(2100, 1, 1).isoformat() + 'Z',
            maxResults=2500
        ).execute()
        
        for event in events.get('items', []):
            description = event.get('description', '')
            # Ищем ISIN в description (формат: "ISIN: RU000...")
            if 'ISIN: ' in description:
                # Извлекаем ISIN
                for line in description.split('\n'):
                    if line.startswith('ISIN: '):
                        isin = line.replace('ISIN: ', '').strip()
                        events_dict[event['id']] = {
                            'isin': isin,
                            'summary': event.get('summary', ''),
                            'date': event.get('start', {}).get('date', '')
                        }
                        break
        
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    
    return events_dict

def delete_event(event_id):
    """Удалить событие по ID."""
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return True
    except HttpError as e:
        print(f"  Ошибка при удалении: {e}")
        return False

def create_event(isin, name, value, date_str):
    """Создать событие в календаре."""
    event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    summary = f"Купон {name} {value:.2f} ₽"
    
    event_body = {
        'summary': summary,
        'start': {'date': event_date.isoformat()},
        'end': {'date': (event_date + datetime.timedelta(days=1)).isoformat()},
        'description': f"ISIN: {isin}\nРазмер купона: {value:.2f} ₽",
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 24 * 60}],
        },
    }
    
    try:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return True
    except HttpError as e:
        print(f"  Ошибка при создании: {e}")
        return False

# --- ОСНОВНАЯ ЛОГИКА ---

# 1. Получаем все события, созданные скриптом
print("\n➜ Получаем существующие события в календаре...")
existing_events = get_all_coupon_events()
print(f"  Найдено {len(existing_events)} событий, созданных скриптом.")

# 2. Формируем набор ISIN, которые должны остаться
target_isins = set(isin_list)

# 3. Удаляем события для ISIN, которых уже нет в файле
events_to_delete = []
for event_id, event_data in existing_events.items():
    if event_data['isin'] not in target_isins:
        events_to_delete.append(event_id)

if events_to_delete:
    print(f"\n➜ Удаляем {len(events_to_delete)} событий для ISIN, отсутствующих в файле...")
    for event_id in events_to_delete:
        if delete_event(event_id):
            print(f"  ✓ Удалено событие: {existing_events[event_id]['summary']}")

# 4. Собираем актуальные данные для всех ISIN из файла
print("\n➜ Получаем актуальные данные по купонам...")
coupons_to_add = []  # список (isin, name, value, date_str)

for isin in isin_list:
    print(f"\n  Обработка {isin}...")
    secid, name = find_security_id(isin)
    if not secid:
        print(f"    ✗ Бумага не найдена на Мосбирже.")
        continue
    
    print(f"    ✓ Найдено: {name} ({secid})")
    coupons = get_coupons(secid)
    if not coupons:
        print(f"    ✗ Нет данных по купонам.")
        continue
    
    # Оставляем только будущие купоны
    today = datetime.date.today()
    future_count = 0
    for value, date_str in coupons:
        try:
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date >= today:
                coupons_to_add.append((isin, name, value, date_str))
                future_count += 1
        except:
            continue
    
    print(f"    ✓ Найдено {future_count} будущих купонов.")

# 5. Добавляем новые события (которых ещё нет)
print(f"\n➜ Добавляем новые события...")
added_count = 0
for isin, name, value, date_str in coupons_to_add:
    # Проверяем, есть ли уже такое событие в календаре
    event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    summary = f"Купон {name} {value:.2f} ₽"
    
    # Быстрый поиск среди существующих событий
    already_exists = False
    for event_data in existing_events.values():
        if (event_data['isin'] == isin and 
            event_data['summary'] == summary and
            event_data['date'] == event_date.isoformat()):
            already_exists = True
            break
    
    if already_exists:
        # Если событие уже есть, но было удалено на шаге 3? В этом случае оно не в existing_events.
        # Проверяем ещё раз через API напрямую
        time_min = event_date.isoformat() + 'T00:00:00+03:00'
        time_max = (event_date + datetime.timedelta(days=1)).isoformat() + 'T00:00:00+03:00'
        search_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            q=summary
        ).execute()
        if search_result.get('items'):
            already_exists = True
    
    if already_exists:
        print(f"  Пропускаем (уже есть): {summary} на {date_str}")
        continue
    
    if create_event(isin, name, value, date_str):
        print(f"  ✓ Добавлено: {summary} на {date_str}")
        added_count += 1

print(f"\n✅ Готово!")
print(f"  Добавлено событий: {added_count}")
print(f"  Удалено событий: {len(events_to_delete)}")
print(f"  Всего в календаре теперь: {len(existing_events) - len(events_to_delete) + added_count} событий")