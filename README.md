# Djarvis - Interactive Ansible Learning Platform

## 🎯 Описание

Djarvis - это современная интерактивная платформа для изучения Ansible с практическими заданиями, автоматической проверкой и системой прогресса.

## ✨ Основные возможности

- 📚 **Структурированные модули** - от базового до продвинутого уровня
- 💻 **Интерактивный редактор кода** - Monaco Editor для написания Ansible playbooks
- 🐳 **Изолированная среда выполнения** - Docker-контейнеры для безопасного запуска кода
- ✅ **Автоматическая проверка** - тесты правильности выполнения заданий
- 💡 **Система подсказок** - прогрессивные hints для студентов
- 📊 **Трекинг прогресса** - отслеживание успехов и достижений
- 🔐 **Аутентификация** - безопасная система регистрации/авторизации
- 👨‍💼 **Admin-панель** - управление контентом, пользователями и заданиями

## 🏗️ Архитектура

### Технологический стек

**Backend:**
- Django 5.0+ / Django REST Framework
- PostgreSQL 15
- Redis (Celery broker + caching)
- Celery (асинхронные задачи)

**Frontend:**
- React 18
- Monaco Editor
- Material-UI / Ant Design
- Axios / React Query

**Infrastructure:**
- Docker / Docker Compose
- Nginx (reverse proxy)
- Docker-in-Docker (sandbox execution)

### Микросервисы

```
├── web (Django API)
├── db (PostgreSQL)
├── redis (Cache + Message Broker)
├── celery_worker (Task execution)
├── celery_beat (Scheduled tasks)
└── nginx (Reverse proxy + Static files)
```

## 🚀 Быстрый старт

### Требования

- Docker 24.0+
- Docker Compose 2.0+
- 4GB RAM минимум
- 10GB свободного места на диске

### Установка

1. **Клонирование репозитория:**
```bash
git clone https://github.com/elementary1997/Djarvis.git
cd Djarvis
```

2. **Настройка переменных окружения:**
```bash
cp backend/.env.example backend/.env
# Отредактируйте backend/.env под ваши нужды
```

3. **Запуск приложения:**
```bash
docker-compose up -d --build
```

4. **Создание суперпользователя:**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Загрузка демо-данных (опционально):**
```bash
docker-compose exec web python manage.py loaddata fixtures/demo_data.json
```

### Доступ к приложению

- **Frontend:** http://localhost
- **API:** http://localhost/api/
- **Admin Panel:** http://localhost/admin/
- **API Documentation:** http://localhost/api/docs/

## 📖 Структура проекта

```
Djarvis/
├── backend/
│   ├── apps/
│   │   ├── accounts/          # Аутентификация и профили
│   │   ├── courses/           # Модули и уроки
│   │   ├── exercises/         # Практические задания
│   │   ├── sandbox/           # Выполнение кода в контейнерах
│   │   └── progress/          # Трекинг прогресса
│   ├── config/                # Настройки Django
│   ├── utils/                 # Утилиты
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
├── docker-compose.yml
└── README.md
```

## 🎓 Модули обучения

### 1. Базовый уровень
- Введение в Ansible
- Установка и настройка
- Ad-hoc команды
- Inventory файлы
- Основы Playbooks

### 2. Средний уровень
- Variables и Facts
- Jinja2 Templates
- Handlers и Notifications
- Roles и Collections
- Ansible Vault

### 3. Продвинутый уровень
- Dynamic Inventory
- Custom Modules
- Ansible Tower/AWX
- CI/CD интеграция
- Cloud Providers (AWS, Azure, GCP)

## 🔧 Разработка

### Локальная разработка Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Локальная разработка Frontend

```bash
cd frontend
npm install
npm start
```

### Запуск тестов

```bash
# Backend tests
docker-compose exec web python manage.py test

# Frontend tests
cd frontend && npm test
```

## 🔒 Безопасность

- Изоляция контейнеров студентов
- Rate limiting для API
- CORS настройки
- Валидация и санитизация ввода
- Ограничения на выполнение команд
- Resource limits для контейнеров

## 📊 Мониторинг

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web

# Статистика контейнеров
docker stats
```

## 🤝 Contributing

Мы приветствуем contributions! Пожалуйста, создавайте Pull Requests.

## 📝 Лицензия

MIT License

## 👥 Авторы

- **Павел** - *Initial work* - [elementary1997](https://github.com/elementary1997)

## 📞 Поддержка

Если у вас возникли вопросы:
- Создайте Issue в репозитории
- Email: elipashev2023@yandex.ru
