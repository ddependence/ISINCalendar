# 💰 Купонный Календарь (ISIN Calendar)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Google Calendar API](https://img.shields.io/badge/Google%20Calendar-API-yellow)](https://developers.google.com/calendar)
[![MOEX API](https://img.shields.io/badge/MOEX-API-orange)](https://iss.moex.com/)

Скрипт для автоматического добавления купонных выплат по облигациям в Google Календарь.  
Вы просто передаёте список ISIN облигаций, а скрипт:

- Получает актуальные данные по купонам с Московской биржи (MOEX);
- Добавляет события в ваш Google Календарь с названием, датой и суммой купона;
- Удаляет события по облигациям, которых больше нет в вашем списке;
- Не создаёт дубликаты при повторных запусках.

> Подходит для владельцев портфелей облигаций, которые хотят всегда видеть график купонных выплат в своём календаре.

---

## 📸 Скриншоты

### Пример события в Google Календаре

<p align="center">
  <img src="docs/screenshots/calendar_event_example.png" alt="Пример события в календаре" width="600">
  <br>
  <em>Событие с названием облигации, суммой купона и напоминанием за 24 часа</em>
</p>

### Процесс настройки Google Cloud Console

| Шаг | Описание | Скриншот |
|-----|----------|----------|
| 1 | Включение Google Calendar API | <img src="docs/screenshots/enable_api.png" alt="Включение API" width="200"> |
| 2 | Создание OAuth 2.0 Client ID | <img src="docs/screenshots/create_oauth.png" alt="Создание OAuth" width="200"> |
| 3 | Скачивание `credentials.json` | <img src="docs/screenshots/download_credentials.png" alt="Скачивание credentials" width="200"> |


---

## 🎥 Видео-туториал

> 🎬 **Видео-инструкция по настройке и использованию планируется к выпуску.**  
> Следите за обновлениями в репозитории или подпишитесь на канал [Название канала] (ссылка появится позже).

Примерный план видео:
1. Установка Python и зависимостей.
2. Настройка Google Cloud Console (пошагово).
3. Создание файла со списком ISIN.
4. Первый запуск скрипта и авторизация.
5. Демонстрация работы — добавление событий в календарь.
6. Обновление списка и повторный запуск.

---

## 🚀 Быстрый старт

### 1. Установите зависимости

Скрипт написан на Python 3.8+. Установите необходимые библиотеки:
```bash
pip install -r requirements.txt
```
Или вручную:
```bash
pip install requests==2.31.0 google-auth==2.23.4 google-auth-oauthlib==1.0.0 google-auth-httplib2==0.1.1 google-api-python-client==2.108.0
```

### 2. Получение доступа к Google Calendar API
Чтобы скрипт мог добавлять события в ваш календарь, нужно создать OAuth 2.0 клиент в Google Cloud Console.

1. Перейдите в Google Cloud Console.

2. Создайте новый проект (или выберите существующий).

3. Включите Google Calendar API:

    - Перейдите в раздел "Библиотека"

    - Найдите "Google Calendar API" и нажмите "Включить".

4. Создайте OAuth 2.0 Client ID:

    - Перейдите в раздел "Учётные данные";

    - Нажмите "Создать учётные данные" → "ID клиента OAuth";

    - Выберите тип приложения "Десктопное приложение" (Desktop app);

    - Укажите название и нажмите "Создать".

5. Скачайте файл с учётными данными:

    - Напротив созданного клиента нажмите значок скачивания (↓);

    - Сохраните файл как credentials.json в папку со скриптом.

### 3. Подготовка файла со списком ISIN
Создайте текстовый файл (например, isin_list.txt) и укажите в нём ISIN облигаций по одному на строку:
```text
RU000A10D2Y6
RU000A10D3S6
RU000A10DQ68
RU000A1097S8
```
Сохраните файл в ту же папку, где находится скрипт. Пример файла [ISIN_example.txt](https://github.com/ddependence/ISINCalendar/blob/main/examples/ISIN_example.txt)

### 4. Запустите скрипт
```bash
isin_calendar.py isin_list.txt
```
При первом запуске откроется браузер с запросом на авторизацию в Google. Войдите в свой аккаунт и дайте разрешение на доступ к календарю. После этого будет создан файл token.json — он хранит ваш доступ и позволяет запускать скрипт без повторной авторизации.

---

## 📁 Структура проекта


---

## ⚙️ Как это работает

---

## 📝 Пример использования

### Исходные данные
### Запуск
### Что произойдёт
### Вывод в консоли

---

### 🔄 Обновление списка облигаций

---

### 🧩 Требования

---


