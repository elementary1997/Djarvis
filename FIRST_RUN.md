# 🎯 Инструкция для первого запуска Djarvis

## Быстрый старт (3 команды)

```bash
# 1. Остановить и очистить предыдущие контейнеры (если были)
docker-compose down -v

# 2. Пересобрать образы с новым кодом
docker-compose build

# 3. Запустить все сервисы (автоматически создаст миграции)
docker-compose up -d
```

## Ждем готовности (30-60 секунд)

```bash
# Смотрим логи web сервиса
docker-compose logs -f web

# Должны увидеть:
# ✅ Migrations created
# ✅ Migrations applied
# ✅ Static files collected
# 🚀 Starting Gunicorn...
```

## Проверяем статус

```bash
# Все контейнеры должны быть running
docker-compose ps

# Вывод должен быть примерно таким:
# djarvis_db             running
# djarvis_redis          running  
# djarvis_web            running
# djarvis_celery_worker  running
# djarvis_celery_beat    running
# djarvis_nginx          running
```

## Создаем суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser

# Введите:
# Email: admin@example.com
# Username: admin
# Password: (ваш пароль)
```

## Загружаем демо-данные

```bash
docker-compose exec web python manage.py loaddata fixtures/demo_data.json
```

## 🎉 Готово! Открываем приложение

- **Frontend**: http://localhost
- **Admin Panel**: http://localhost/admin
- **API**: http://localhost/api/
- **API Docs**: http://localhost/api/docs/

---

## ⚠️ Если что-то пошло не так

### Web контейнер не запускается

```bash
# Смотрим подробные логи
docker-compose logs web

# Перезапускаем
docker-compose restart web
```

### База данных не готова

```bash
# Проверяем статус БД
docker-compose logs db

# Ждем пока БД будет ready
docker-compose exec db pg_isready -U djarvis_user
```

### Полный сброс и перезапуск

```bash
# ВНИМАНИЕ: Удалит ВСЕ данные!
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 После первого успешного запуска

Можно удалить `docker-compose.override.yml` если хотите:

```bash
rm docker-compose.override.yml
```

Этот файл нужен только для первого запуска, чтобы автоматически создать миграции.
В дальнейшем миграции будут применяться автоматически при `docker-compose up`.

---

## 🎓 Следующие шаги

1. **Войдите в админку**: http://localhost/admin
2. **Создайте свои модули** через админ-панель
3. **Зарегистрируйте студента** на http://localhost
4. **Начните обучение!**

---

## 📞 Нужна помощь?

- GitHub Issues: https://github.com/elementary1997/Djarvis/issues
- Email: elipashev2023@yandex.ru
