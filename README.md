# Foodgram
Адрес проекта: https://arsakitty.ru/

Адреса документации:
https://arsakitty.ru/api/schema/swagger-ui/ и 
https://arsakitty.ru/api/schema/redoc/

## Описание
Проект Foodgram - сайт, на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других
авторов. Пользователям также будет доступна возможность скачать «Список
покупок».

## Стек технологий
Python 3.9, Django REST Framework, Nginx, PostgresSQL, Docker, GitHub Actions

## Установка
Для развертывания проекта, используйте `docker-compose.yml`. Убедитесь, что у вас [установлен Docker](#установка-docker) и Docker Compose.

Запустите Docker Compose с этой конфигурацией на своём компьютере

- Выполнить:
```
sudo docker compose -f docker-compose.yml up -d
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/static/. /static/static/
sudo docker compose -f docker-compose.yml exec backend python manage.py load_ingredients
```

Для создания суперпользователя нужно:
- Зайти на удаленный сервер.
- Перейти в папку с docker-compose.yml
- Выполнить:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```

- Настроить Nginx.

## Примеры запроса в Postman:

### 1 Пример:
```
http://localhost/api/recipes/
```
```
{
  "ingredients": [
    {
      "id": 4380,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

### 2 Пример:

```
http://localhost/api/auth/token/login/
```
```
{
"email": "22221@yandex.ru",
"password": "Qwerty123"
}
```