# FanPay веб-аналитика

Веб-приложение собирает снапшоты цен/продаж и помогает сравнить категории, чтобы понять,
что выгоднее фармить и продавать.

## Быстрый старт (Windows CMD, одна команда)

Открой CMD в папке проекта и запусти:

```bat
run.cmd
```

Скрипт создаст виртуальное окружение, установит зависимости и запустит приложение.

## Ручной запуск

```bash
python -m venv .venv
```

Активировать окружение:

- Windows CMD:

```bat
.venv\Scripts\activate.bat
```

- Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

- Mac/Linux:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
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
