# YouTube Service

Сервис для управления YouTube каналами, загрузки видео, сбора статистики и парсинга контента через YouTube Data API v3.

## Описание

YouTube Service - это полнофункциональный микросервис на FastAPI, который предоставляет REST API для:
- Аутентификации пользователей через Google OAuth 2.0
- Управления YouTube каналами
- Парсинга видео с каналов
- Загрузки видео на YouTube
- Сбора и анализа статистики видео
- Поиска видео на YouTube

## Архитектура

Проект использует микросервисную архитектуру с разделением на:
- **API сервер** (FastAPI) - обработка HTTP запросов
- **Consumer сервис** - асинхронная обработка задач через Redis Pub/Sub
- **PostgreSQL** - основное хранилище данных
- **Redis** - кеширование и брокер сообщений

## Структура проекта

```
youtube_service/
├── app.py                      # Главный файл приложения FastAPI
├── config.py                   # Конфигурация (Redis, OAuth)
├── requirements.txt            # Зависимости Python
├── Dockerfile                  # Docker образ приложения
├── docker-compose.yml          # Docker Compose конфигурация
├── run_consumer.py            # Запуск consumer сервиса
│
├── routers/                    # API роутеры
│   ├── auth.py                # Аутентификация (OAuth)
│   ├── channel.py             # Управление каналами
│   ├── parser.py              # Парсинг и поиск видео
│   ├── post.py                # Управление постами/видео
│   ├── stats.py               # Статистика видео
│   └── upload.py              # Загрузка видео
│
├── db/                         # Работа с базой данных
│   ├── models.py              # SQLAlchemy модели
│   ├── engine.py              # Настройка движка БД
│   ├── connection.py          # Управление соединениями
│   ├── config.py              # Конфигурация БД
│   └── handler/               # CRUD операции
│       ├── create.py
│       ├── get.py
│       ├── update.py
│       └── delete.py
│
├── consumer/                   # Consumer сервис
│   ├── consumer.py            # Основной consumer
│   ├── consumer_class/
│   │   └── redis_consumer.py  # Redis Pub/Sub consumer
│   └── cunsumer_func/         # Обработчики сообщений
│       ├── download_video.py  # Скачивание видео
│       ├── upload_video.py    # Загрузка на YouTube
│       ├── save_video.py      # Сохранение в БД
│       └── remove_video.py    # Удаление файлов
│
├── services/                   # Бизнес-логика
│   ├── scheduler/
│   │   ├── scheduler_stats.py # Планировщик сбора статистики
│   │   └── scheduler_upload.py # Планировщик загрузки
│   └── youtube/
│       ├── stats_service.py   # Сервис статистики
│       └── upload_service.py # Сервис загрузки
│
├── tasks/                      # Фоновые задачи
│   └── parse_video_channel.py # Парсинг видео канала
│
├── shemas/                     # Pydantic схемы
│   ├── channel.py
│   ├── parser.py
│   └── upload.py
│
├── exception/                  # Кастомные исключения
│   └── database.py
│
└── alembic/                    # Миграции базы данных
    └── versions/
```

## Технологический стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** (async) - ORM для работы с БД
- **PostgreSQL** - реляционная БД
- **Redis** - кеширование и брокер сообщений
- **Alembic** - миграции БД
- **Google API Python Client** - работа с YouTube Data API v3
- **APScheduler** - планировщик задач
- **Docker & Docker Compose** - контейнеризация

## Модели данных

### Channel
Хранит информацию о YouTube каналах пользователей:
- `account_id` - уникальный ID аккаунта в системе
- `user_id` - ID пользователя
- `platform_user_id` - ID канала на YouTube
- `credentials` - OAuth credentials (JSON)
- Статистика: подписчики, видео, просмотры
- Метаданные: название, описание, thumbnail

### Post
Хранит информацию о загруженных видео:
- `post_id` - уникальный ID поста
- `channel_id` - связь с каналом
- `youtube_video_id` - ID видео на YouTube
- Метаданные: заголовок, описание, теги
- `published_at` - дата публикации

### Statistic
Хранит статистику видео по времени:
- `stats_id` - уникальный ID записи
- `post_id` - связь с постом
- `capture_date` - дата сбора статистики
- Метрики: просмотры, лайки, комментарии, избранное

### YoutubeChannel
Хранит информацию о подписанных каналах:
- `youtube_channel_id` - уникальный ID
- `platform_channel_id` - ID на YouTube
- Статистика канала

### Video
Хранит информацию о видео с подписанных каналов:
- `video_id` - уникальный ID
- `youtube_video_id` - ID на YouTube
- `type` - тип видео (long/short)
- Статистика и метаданные

### Subscription
Связь пользователей с подписанными каналами:
- `subscription_id` - уникальный ID
- `user_id` - ID пользователя
- `youtube_channel_id` - ID канала

## API Endpoints

### Аутентификация (`/auth`)
- `GET /auth/login/{user_id}` - получение URL для OAuth авторизации
- `GET /auth/callback` - обработка OAuth callback, создание/обновление канала

### Каналы (`/channel`)
- `GET /channel/all/{user_id}` - получить все каналы пользователя
- `GET /channel/{account_id}` - получить канал по ID

### Парсинг (`/parser`)
- `GET /parser/search` - поиск видео на YouTube
  - Параметры: `account_id`, `query`, `max_results`, `order`
- `GET /parser/channels/{user_id}` - получить подписанные каналы пользователя
- `GET /parser/channel/{channel_id}` - получить канал с видео
- `POST /parser/channel` - добавить канал для парсинга

### Посты (`/post`)
- `GET /post/all/{channel_id}` - получить все посты канала
- `GET /post/{post_id}` - получить пост по ID

### Загрузка (`/upload`)
- `POST /upload/videos` - загрузить видео на YouTube
  - Принимает список аккаунтов с медиа-файлами
  - Асинхронная обработка через Redis

### Статистика (`/stats`)
- `GET /stats/{channel_id}/{video_id}` - получить статистику видео
- `GET /stats/{user_id}` - получить последнюю статистику всех видео пользователя

## Поток загрузки видео

1. **Запрос на загрузку** (`POST /upload/videos`)
   - API получает список видео с URL
   - Публикует сообщение в Redis канал `download_video`

2. **Скачивание** (Consumer: `download_video`)
   - Скачивает видео по URL
   - Сохраняет в директорию `videos/`
   - Публикует сообщение в канал `upload_video`

3. **Загрузка на YouTube** (Consumer: `upload_video`)
   - Получает credentials из Redis/БД
   - Загружает видео на YouTube через API
   - Публикует сообщения в каналы `remove_video` и `save_video`

4. **Сохранение в БД** (Consumer: `save_video`)
   - Сохраняет информацию о видео в таблицу `Post`

5. **Удаление файла** (Consumer: `remove_video`)
   - Удаляет временный файл после загрузки

## Планировщик задач

### Сбор статистики
- Запускается каждые 5 часов
- Собирает статистику всех загруженных видео
- Сохраняет в таблицу `Statistic`

