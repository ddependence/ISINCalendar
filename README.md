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

> **Примечание:** Скриншоты временно отсутствуют. Вы можете создать их самостоятельно и разместить в папке `docs/screenshots/`.

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

### 2. Получение доступа к Google Calendar API

### 3. Подготовка файла со списком ISIN

### 4. Запустите скрипт

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


