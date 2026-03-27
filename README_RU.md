# ChessBot

Шахматный бот на основе нейросети, играющий на Lichess. Бот использует 3D CNN, обученную на PGN-партиях, для предсказания ходов и играет через Lichess Board API.

## Структура проекта

```
chessbot/
├── main.py                 # Точка входа — игровой цикл и логика бота
├── converter.py            # Конвертация FEN в тензор и индексация UCI-ходов
├── network/                # Нейросеть
│   ├── net.py              # Архитектура 3D CNN (Conv3d → FC → 4672 хода)
│   ├── bot.py              # Обёртка для инференса (загрузка весов, вероятности ходов)
│   └── train.py            # Обучение на PGN-данных
├── game_services/          # Интеграция с платформами
│   ├── service.py          # Базовый интерфейс сервиса
│   ├── lichess/            # Интеграция с Lichess (Board API)
│   │   ├── client.py       # Низкоуровневый HTTP-клиент
│   │   └── service.py      # Высокоуровневый игровой сервис
│   └── chesscom/           # Интеграция с Chess.com (Playwright)
│       └── service.py
├── game_brain/             # Шахматная логика
│   ├── game.py             # Основной класс игры (python-chess)
│   └── client.py           # Обёртка для управления игрой
└── requirements.txt
```

## Архитектура

### Нейросеть

Сеть (`network/net.py`) — 3D CNN, принимающая представление доски и выдающая вероятности для 4672 возможных ходов:

- **Вход**: тензор `(1, 17, 8, 8)` — 12 плоскостей фигур (6 белых + 6 чёрных), 4 плоскости прав на рокировку, 1 плоскость взятия на проходе
- **Слои**: 3x Conv3d + BatchNorm + MaxPool → FC(512) → Dropout(0.7) → FC(4672)
- **Выход**: распределение вероятностей по всем возможным UCI-ходам (64x64 базовых хода + превращения)

Конвертер (`converter.py`) отвечает за преобразование FEN → тензор и UCI-ход → индекс.

### Игровой цикл

1. Создание игры против Stockfish AI через `/api/challenge/ai`
2. Стриминг состояния игры через `/api/board/game/stream/{id}`
3. На каждом ходу: FEN → тензор → вероятности ходов → маскировка нелегальных → сэмплирование хода → отправка через `/api/board/game/{id}/move/{move}`

На данный момент бот играет только за белых.

### Интеграция с Lichess

Используется **Board API** (для обычных аккаунтов, контроль времени Rapid+). Основные эндпоинты:
- `POST /api/challenge/ai` — начать игру против Stockfish (уровни 1-8)
- `GET /api/board/game/stream/{id}` — стрим событий игры
- `POST /api/board/game/{id}/move/{move}` — сделать ход

## Установка

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Конфигурация

Создайте файл `.env` в корне проекта:

```env
LICHESS_TOKEN=ваш_токен_lichess
```

### Получение токена Lichess

1. Перейдите на https://lichess.org/account/oauth/token
2. Создайте токен с правами: `board:play`, `challenge:read`, `challenge:write`

## Использование

### Игра против Stockfish

```bash
python main.py
```

Настройки в `main.py`:
- `OPPONENT` — `"stockfish"` или имя бота
- `STOCKFISH_LEVEL` — от 1 до 8
- `CLOCK_LIMIT` — время в секундах (минимум 480 для Board API)
- `WEIGHTS_FILE` — имя файла весов из `network/weights/`

### Обучение на PGN-данных

```bash
python -m network.train
```

В `network/train.py` можно настроить путь к PGN-файлу и параметры обучения (эпохи, размер батча, learning rate).

## Зависимости

- **python-chess** — шахматная логика и валидация ходов
- **torch** — нейросеть (3D CNN)
- **numpy** — операции с тензорами
- **requests** — HTTP-клиент для Lichess API
- **python-dotenv** — загрузка переменных окружения
- **playwright** — автоматизация браузера для Chess.com (опционально)

## Лицензия

MIT License
