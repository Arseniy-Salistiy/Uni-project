# Университетская система (FastAPI + Docker)

Минимальное руководство по локальному запуску приложения в Docker-контейнерах.

## 🛠 Требования
* [Docker](https://docker.com) и [Docker Compose](https://docker.com)

---

## 🚀 Быстрый запуск

### 1. Настройка окружения
Создайте файл переменных окружения `.env` на основе примера:
```bash
cp .env.example .env
```
> ⚠️ **Важно:** Откройте созданный файл `.env` и заполните в нём данные для базы данных (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_NAME`, `POSTGRES_PORT`).

### 2. Сборка и запуск контейнеров
Запустите Docker Compose в фоновом режиме (бэкенд автоматически дождется готовности базы данных благодаря healthcheck):
```bash
docker compose up --build -d
```

### 3. Запуск фронтенда
После того как подняли Docker нужно запустить сервер в терминале в корне проекта командой:
```bash
python -m http.server 5500
```

После этого:
* **API бэкенда** будет доступно по адресу: `http://localhost:8000`
* **Интерактивная документация (Swagger)**: `http://localhost:8000/docs`
* **Схема API для фронтенда**: `http://localhost:8000/openapi.json`

---

## 📊 Заполнение базы данных (Сидирование)

После успешного запуска контейнеров необходимо вручную применить тестовые данные из папки `scripts/`. 

Выполните команду ниже (замените `user_name` и `db_name` на те значения, которые вы указали в вашем `.env` файле):
```bash
docker compose exec app psql -h database -U user_name -d db_name -f scripts/seed.sql
```

---

## 🐳 Полезные команды

* **Посмотреть логи приложения:**
  ```bash
  docker compose logs -f app
  ```
* **Остановить контейнеры:**
  ```bash
  docker compose down
  ```
* **Остановить контейнеры с полной очисткой данных БД:**
  ```bash
  docker compose down -v
  ```
