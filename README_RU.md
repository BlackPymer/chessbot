# ChessBot

Нейросетевой шахматный бот для игры против онлайн-ботов на Lichess и Chess.com. Проект создан в образовательных целях для тренировки и разработки шахматного ИИ.

## Структура проекта

```
chessbot/
├── game_services/          # Интеграция с шахматными платформами
│   ├── service.py          # Базовый интерфейс сервиса
│   ├── chesscom/           # Интеграция с Chess.com (автоматизация браузера)
│   │   └── service.py
│   └── lichess/            # Интеграция с Lichess (API)
│       ├── service.py      # Высокоуровневый игровой сервис
│       └── client.py       # Низкоуровневый API клиент
├── game_brain/             # Шахматная логика и управление партией
│   ├── game.py             # Основной класс игры
│   └── client.py           # Обёртка для управления игрой
├── network/                # Компоненты нейросети
│   └── test.py
├── main.py                 # Точка входа
└── requirements.txt        # Зависимости Python
```

## Архитектура

### Слой игровых сервисов

Модуль `game_services` предоставляет интеграцию с шахматными платформами:

- **LichessService** - Использует Lichess Bot API для официальной игры ботами
- **ChesscomService** - Использует автоматизацию браузера (Playwright) для Chess.com

Оба сервиса наследуются от базового класса `Service`, обеспечивая единый интерфейс.

### Слой игровой логики

Модуль `game_brain` обрабатывает шахматную логику:

- **ChessGame** - Основная игровая логика с использованием библиотеки `python-chess`
- **GameClient** - Высокоуровневая обёртка для операций с игрой

Возможности:
- Валидация ходов (формат UCI: `e2e4`, `e7e8q`)
- Отслеживание состояния игры (ход, шах, окончание)
- Экспорт в FEN/PGN
- Генерация списка легальных ходов

## Установка

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Установить браузеры Playwright (для Chess.com)
playwright install
```

## Конфигурация

Создайте файл `.env` в корне проекта:

```env
# Lichess (обязательно для игры ботами)
LICHESS_TOKEN=ваш_токен_lichess

# Chess.com (опционально, для автоматизации браузера)
CHESSCOM_LOGIN=ваш_email
CHESSCOM_PASSWORD=ваш_пароль
```

### Получение токена Lichess

1. Обновите аккаунт до BOT на https://lichess.org/account/upgrade
2. Создайте токен на https://lichess.org/account/oauth/token
3. Выберите права: `bot:play`, `challenge:read`, `challenge:write`

## Использование

### Интеграция с Lichess

```python
from game_services.lichess.service import LichessService

service = LichessService()

# Получить информацию об аккаунте
account = service.get_account()
print(f"Аккаунт: {account['username']}")

# Получить список ботов онлайн
bots = service.get_online_bots()

# Вызвать бота на игру
service.challenge_bot("StockfishLevel1", clock_limit=60)

# Ждать начала игры
game = service.wait_for_game_start()

# Получить текущую позицию
board = service.get_board()

# Сделать ход (формат UCI)
service.make_move("e2e4")
```

### Игровая логика

```python
from game_brain.client import GameClient

client = GameClient()
client.new_game()

# Проверить валидность хода
if client.is_valid_move("e2e4"):
    client.make_move("e2e4")

# Получить состояние игры
print(f"Ход: {client.get_turn()}")
print(f"Игра окончена: {client.is_game_over()}")
print(f"Результат: {client.get_result()}")

# Получить позицию
print(f"FEN: {client.get_fen()}")
print(f"Легальные ходы: {client.get_legal_moves()}")
```

## Зависимости

- **python-chess** - Шахматная логика и валидация ходов
- **requests** - HTTP-клиент для Lichess API
- **playwright** - Автоматизация браузера для Chess.com
- **torch** - Фреймворк для нейросетей (для будущей разработки)
- **numpy** - Численные вычисления

## Лицензия

MIT License
