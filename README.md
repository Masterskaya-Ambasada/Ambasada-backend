# "Ambasada za urbanizam" project

Django DRF backend for website 


## 🛠️ Local Development with Docker

### Environment Setup:
```shell
  cp .env.example .env
```

### Start services.

_If there are no local  `docker images` - they will be pulled from DockerHub or builded._
```shell
  docker compose up -d
```

### 3. Apply database migrations and create superuser:
```shell
  docker compose exec -it web python backend/manage.py migrate
  docker compose exec -it web python backend/manage.py createsuperuser
```
### Access Application
- Open [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) in browser

## ✅ Check code Quality and formatting

Format code:
```shell
docker compose run --rm -it web ruff format
```

Make all checks and tests like in production deploy:
```shell
docker compose run --rm -it web bash ./docker/django/ci.sh
```


## 🔄 Maintenance Commands
Rebuild Container (when requirements change or  some issues occur):

```shell
docker compose build web
docker compose up -d
```

Clean Project (removes volumes including database):
```shell
docker compose down -v
```