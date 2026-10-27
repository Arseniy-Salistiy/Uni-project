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
> ⚠️ **Важно:** Откройте созданный файл `.env` и заполните в нём данные для базы данных (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_NAME`, `POSTGRES_PORT`), а также `SECRET_KEY` (любая длинная случайная строка) и `ALGORITHM=HS256`. Значения `ADMIN/DEAN/TEACHER/STUDENT` должны совпадать с id ролей в таблице `roles` (в тестовых данных 1/2/3/4).

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

Выполните команду ниже (логин, пароль и имя БД берутся из `.env` внутри контейнера):
```bash
docker compose exec app sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" psql -h database -U "$POSTGRES_USER" -d "$POSTGRES_NAME" -f scripts/seed.sql'
```

Тестовые учётные записи (пароль у всех `password123`):

| Роль | Email |
|---|---|
| Администратор | `admin@university.test` |
| Декан | `dean@university.test` |
| Преподаватель | `ivanov.sp@university.test` (и ещё 9, см. `scripts/seed.sql`) |
| Студент | `s01@student.university.test` … `s30@student.university.test` |

---

## 📚 Документация

* `docs/Отчет_тестирование_и_внедрение.docx` — план тестирования, протокол тестирования, руководство пользователя (документы 4–6)
* `docs/Презентация.pptx` — презентация проекта (документ 7)

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
