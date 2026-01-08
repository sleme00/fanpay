# FanPay веб-аналитика

Веб-приложение собирает снапшоты цен/продаж и помогает сравнить категории, чтобы понять,
что выгоднее фармить и продавать.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Настройте переменные окружения:

```bash
export FANPAY_DATA_SOURCE="mock"
export FANPAY_SAMPLE_DATA="fanpay_bot/data/sample_data.json"
```

Запуск приложения:

```bash
python -m fanpay_bot.web_app
```

Откройте в браузере: `http://localhost:8000`.

## Заметки

Сейчас подключен mock-источник данных. Для подключения реального FanPay нужно добавить
адаптер данных (например, через неофициальный API/скрапинг) и указать
`FANPAY_DATA_SOURCE`.
