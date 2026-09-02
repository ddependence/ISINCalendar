import sys
import requests
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Константы ---
ISIN_FILE = "isin_list.txt"  # Имя файла со списком ISIN (фиксированное)

# --- Проверка наличия файла ISIN ---
if not os.path.exists(ISIN_FILE):
    print(f"❌ Ошибка: Файл '{ISIN_FILE}' не найден в текущей папке.")
    print("   Создайте файл и укажите в нём ISIN облигаций по одному на строку.")
    print("   Пример файла: https://github.com/ddependence/ISINCalendar/blob/main/examples/ISIN_example.txt")
    sys.exit(1)

# --- Чтение ISIN из файла ---
try:
    with open(ISIN_FILE, 'r', encoding='utf-8') as f:
        isin_list = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"❌ Ошибка при чтении файла: {e}")
    sys.exit(1)

if not isin_list:
    print(f"❌ Ошибка: Файл '{ISIN_FILE}' пуст или не содержит ISIN.")
    sys.exit(1)

print(f"✅ Найдено {len(isin_list)} ISIN для обработки.")

# --- Функции для работы с API Мосбиржи ---

def find_security_id(isin):
    """
    Поиск инструмента по ISIN, возвращает secid и название.
    Возвращает (secid, shortname) или (None, None) при ошибке.
    """
    url = "https://iss.moex.com/iss/securities.json"
    params = {
        "q": isin,
        "iss.meta": "off",
        "securities.columns": "secid,shortname,isin"  # isin = ISIN
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("securities", {}).get("data", [])
        for row in rows:
            if len(row) >= 3 and row[2] == isin:
                return row[0], row[1]
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"    ⚠️ Ошибка запроса к Мосбирже для ISIN {isin}: {e}")
    return None, None

def get_coupons(secid):
    """
    Получить список купонов для бумаги по secid.
    Возвращает список кортежей (value, date_str).
    """
    url = f"https://iss.moex.com/iss/securities/{secid}/coupons.json"
    params = {
        "iss.meta": "off",
        "coupons.columns": "couponvalue,coupondate"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
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
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"    ⚠️ Ошибка запроса купонов для {secid}: {e}")
        return []

# --- Настройка Google Calendar ---

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Проверка наличия credentials.json
if not os.path.exists('credentials.json'):
    print("❌ Ошибка: Файл credentials.json не найден.")
    print("   Скачайте его из Google Cloud Console и поместите в папку со скриптом.")
    sys.exit(1)

# Авторизация
creds = None
if os.path.exists('token.json'):
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception as e:
        print(f"⚠️ Ошибка чтения token.json: {e}. Будет выполнена повторная авторизация.")

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"⚠️ Ошибка обновления токена: {e}. Выполняется полная авторизация.")
            creds = None
    if not creds:
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            # Добавляем подсказку для самой частой причины (403 access_denied)
            print("   Возможная причина: ваше приложение в Google Cloud Console находится в тестовом режиме,")
            print("   а ваш аккаунт не добавлен в список тестовых пользователей.")
            print("   Добавьте свой Gmail в разделе 'OAuth consent screen' → 'Test users' и повторите попытку.")
            sys.exit(1)
    # Убедимся, что creds не None перед записью
    if creds:
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    else:
        print("❌ Критическая ошибка: не удалось получить учётные данные.")
        sys.exit(1)

try:
    service = build('calendar', 'v3', credentials=creds)
except Exception as e:
    print(f"❌ Ошибка создания сервиса Google Calendar: {e}")
    sys.exit(1)

calendar_id = 'primary'

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С КАЛЕНДАРЁМ ---

def get_all_coupon_events():
    """
    Возвращает словарь: {event_id: {'isin': isin, 'summary': summary, 'date': date}}
    для всех событий, созданных этим скриптом (содержат ISIN в description).
    """
    events_dict = {}
    page_token = None
    try:
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
                if 'ISIN: ' in description:
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
    except HttpError as e:
        print(f"⚠️ Ошибка получения событий из календаря: {e}")
    return events_dict

def delete_event(event_id):
    """Удалить событие по ID."""
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return True
    except HttpError as e:
        print(f"  ⚠️ Ошибка при удалении: {e}")
        return False

def create_event(isin, name, value, date_str):
    """Создать событие в календаре."""
    try:
        event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"  ⚠️ Некорректный формат даты: {date_str}")
        return False

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
        print(f"  ⚠️ Ошибка при создании события: {e}")
        return False

# --- ОСНОВНАЯ ЛОГИКА ---

print("\n➜ Получаем существующие события в календаре...")
existing_events = get_all_coupon_events()
print(f"  Найдено {len(existing_events)} событий, созданных скриптом.")

# Формируем набор ISIN, которые должны остаться
target_isins = set(isin_list)

# Удаляем события для ISIN, которых уже нет в файле
events_to_delete = []
for event_id, event_data in existing_events.items():
    if event_data['isin'] not in target_isins:
        events_to_delete.append(event_id)

if events_to_delete:
    print(f"\n➜ Удаляем {len(events_to_delete)} событий для ISIN, отсутствующих в файле...")
    for event_id in events_to_delete:
        if delete_event(event_id):
            print(f"  ✓ Удалено событие: {existing_events[event_id]['summary']}")

# Собираем актуальные данные для всех ISIN из файла
print("\n➜ Получаем актуальные данные по купонам...")
coupons_to_add = []

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
    
    today = datetime.date.today()
    future_count = 0
    for value, date_str in coupons:
        try:
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date >= today:
                coupons_to_add.append((isin, name, value, date_str))
                future_count += 1
        except ValueError:
            continue
    
    print(f"    ✓ Найдено {future_count} будущих купонов.")

# Добавляем новые события
print(f"\n➜ Добавляем новые события...")
added_count = 0
for isin, name, value, date_str in coupons_to_add:
    try:
        event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        continue

    summary = f"Купон {name} {value:.2f} ₽"
    
    # Проверяем, существует ли уже такое событие
    already_exists = False
    for event_data in existing_events.values():
        if (event_data['isin'] == isin and 
            event_data['summary'] == summary and
            event_data['date'] == event_date.isoformat()):
            already_exists = True
            break
    
    if already_exists:
        # Дополнительная проверка через API (на случай, если событие было создано вручную)
        time_min = event_date.isoformat() + 'T00:00:00Z'
        time_max = (event_date + datetime.timedelta(days=1)).isoformat() + 'T00:00:00Z'
        try:
            search_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q=summary
            ).execute()
            if search_result.get('items'):
                already_exists = True
        except HttpError:
            pass
    
    if already_exists:
        print(f"  Пропускаем (уже есть): {summary} на {date_str}")
        continue
    
    if create_event(isin, name, value, date_str):
        print(f"  ✓ Добавлено: {summary} на {date_str}")
        added_count += 1

print(f"\n✅ Готово!")
print(f"  Добавлено событий: {added_count}")
print(f"  Удалено событий: {len(events_to_delete)}")
total_events = len(existing_events) - len(events_to_delete) + added_count
print(f"  Всего в календаре теперь: {total_events} событий")