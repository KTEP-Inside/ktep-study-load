# ktep-study-load

- 1 Изменить `CSRF_TRUSTED_ORIGINS`и `ALLOWED_HOSTS` см. settings.py в файле
- 2 Добавить почту для подключения смены пароля. см. settings.py
- 3 Сделать `git clone` на сервере
- 4 Сделать`env` и `env.prod.db`, заполнить по примеру
- 5 Установить `DEBUG=0` перед запуском
- 6`docker compose -f docker-compose.prod.yml up -d --build`
- 7`docker compose exec web python manage.py migrate` (см. **Примечания**)
- 8`docker compose exec web python manage.py loaddata course.json exam.json semester.json typeload.json`
- 9`docker compose exec web python manage.py collectstatic`
- 10`docker compose exec web python manage.py createsuperuser`


### Примечания 
- Приложение стартует раньше базы -> нужно немного подождать перед migrate
  - можно исправить, используя скрипт ожидания старта базы данных
- Для разработки в файле dockerfile и docker-compose(не prod !) скорее всего придется изменить пути
- можно добавить `favicon.ico`