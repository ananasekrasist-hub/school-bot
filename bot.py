import os
import sys
import requests
from datetime import datetime, timedelta
import pytz

# Токен и ID берутся автоматически из секретных настроек GitHub
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Координаты Хотимска (Могилевская область)
LAT = 53.4083
LON = 32.5794

# Расписание по дням недели (0 - Понедельник ... 4 - Пятница)
SCHEDULE = {
    0: (
        "📚 *Расписание на Понедельник:*\n"
        "1. 08:00 — Английский язык\n"
        "2. 09:00 — История Беларуси в контексте всемирной истории\n"
        "3. 10:00 — Математика\n"
        "4. 11:00 — Информатика\n"
        "5. 12:00 — Физическая культура и здоровье\n"
        "6. 13:00 — Химия"
    ),
    1: (
        "📚 *Расписание на Вторник:*\n"
        "1. 08:00 — Беларуская мова\n"
        "2. 09:00 — Математика\n"
        "3. 10:00 — Беларуская літаратура\n"
        "4. 11:00 — Физика\n"
        "5. 12:00 — Физическая культура и здоровье\n"
        "6. 13:00 — Черчение\n"
        "7. 14:00 — География"
    ),
    2: (
        "📚 *Расписание на Среду:*\n"
        "1. 08:00 — Химия\n"
        "2. 09:00 — Биология\n"
        "3. 10:00 — Русский язык\n"
        "4. 11:00 — Русская литература\n"
        "5. 12:00 — История Беларуси в контексте всемирной истории\n"
        "6. 13:00 — Английский язык"
    ),
    3: (
        "📚 *Расписание на Четверг:*\n"
        "1. 08:00 — Классный час\n"
        "2. 09:00 — Английский язык\n"
        "3. 10:00 — Обществоведение\n"
        "4. 11:00 — Английский язык\n"
        "5. 12:00 — Математика\n"
        "6. 13:00 — Беларуская літаратура\n"
        "7. 14:00 — Допризывная и медицинская подготовка"
    ),
    4: (
        "📚 *Расписание на Пятницу (ко 2-му уроку):*\n"
        "1. 08:00 — *СМГ (не идешь)*\n"
        "2. 09:00 — Физика\n"
        "3. 10:00 — Русский язык\n"
        "4. 11:00 — Математика\n"
        "5. 12:00 — Биология\n"
        "6. 13:00 — Обществоведение"
    ),
}

WEATHER_CODES = {
    0: "Ясно ☀️",
    1: "Преимущественно ясно 🌤",
    2: "Переменная облачность ⛅️",
    3: "Пасмурно ☁️",
    45: "Туман 🌫",
    48: "Изморозь 🌫",
    51: "Легкая морось 🌧",
    53: "Морось 🌧",
    55: "Сильная морось 🌧",
    56: "Ледяная морось 🌧",
    57: "Сильная ледяная морось 🌧",
    61: "Небольшой дождь 🌧",
    63: "Дождь 🌧",
    65: "Сильный дождь 🌧",
    66: "Ледяной дождь 🌧",
    67: "Сильный ледяной дождь 🌧",
    71: "Небольшой снег ❄️",
    73: "Снег ❄️",
    75: "Сильный снег ❄️",
    77: "Снежные зерна ❄️",
    80: "Небольшой ливень 🌦",
    81: "Ливень 🌧",
    82: "Сильный ливень ⛈",
    85: "Небольшой снегопад 🌨",
    86: "Сильный снегопад 🌨",
    95: "Гроза ⚡️",
    96: "Гроза с градом ⛈",
    99: "Сильная гроза с градом ⛈",
}

def get_tomorrow_morning_weather(tomorrow_weekday):
    tz = pytz.timezone("Europe/Minsk")
    tomorrow_str = (datetime.now(tz) + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # В пятницу (день 4) идешь к 09:00, в остальные дни к 08:00
    hour_str = "09:00" if tomorrow_weekday == 4 else "08:00"
    default_idx = 9 if tomorrow_weekday == 4 else 8
    target_time = f"{tomorrow_str}T{hour_str}"

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}&hourly=temperature_2m,weathercode"
        f"&timezone=Europe%2FMinsk&start_date={tomorrow_str}&end_date={tomorrow_str}"
    )

    try:
        res = requests.get(url, timeout=10).json()
        times = res["hourly"]["time"]
        temps = res["hourly"]["temperature_2m"]
        codes = res["hourly"]["weathercode"]

        idx = times.index(target_time) if target_time in times else default_idx
        temp = round(temps[idx])
        code = codes[idx]

        desc = WEATHER_CODES.get(code, "Обычная погода")

        # Совет по одежде
        if temp < 5:
            advice = "Одевай бомбер и **обязательно шапку**, утром будет дубак! 🧣🧢"
        elif temp < 15:
            advice = "Самое то для **бомбера** (шапку можно не брать). 🧥"
        else:
            advice = "Довольно тепло! Можно в легкой кофте или накинуть легкий бомбер. 👕"

        # Проверка на осадки
        if code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99]:
            advice += "\n☔️ *Захвати зонт, возможен дождь!*"

        sign = "+" if temp > 0 else ""
        return (
            f"🌡 *Погода в Хотимске завтра в {hour_str}:*\n"
            f"{desc}, температура: *{sign}{temp}°C*\n"
            f"💡 *Совет:* {advice}"
        )
    except Exception as e:
        return f"⚠️ Не удалось загрузить прогноз погоды ({e})."

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload, timeout=10)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "schedule"
    tz = pytz.timezone("Europe/Minsk")
    now = datetime.now(tz)
    weekday = now.weekday()  # 0 - Пн, 1 - Вт, 2 - Ср, 3 - Чт, 4 - Пт, 5 - Сб, 6 - Вс

    if mode == "homework":
        # Напоминание только с Пн (0) по Чт (3)
        if weekday in [0, 1, 2, 3]:
            send_telegram_message("Делай уроки")
    elif mode == "schedule":
        # Отправляем расписание в Вс (6), Пн (0), Вт (1), Ср (2), Чт (3)
        if weekday in [6, 0, 1, 2, 3]:
            tomorrow_weekday = (weekday + 1) % 7
            schedule_text = SCHEDULE.get(tomorrow_weekday, "")
            weather_text = get_tomorrow_morning_weather(tomorrow_weekday)
            full_message = f"{schedule_text}\n\n{weather_text}"
            send_telegram_message(full_message)

if __name__ == "__main__":
    main()
