# Makefile for Docker commands

.PHONY: build up makemigrations migrate user_seed skill_seed language_seed restart rebuild

build:
	docker compose build

up:
	docker compose up

makemigrations:
	docker compose exec api python manage.py makemigrations

migrate:
	docker compose exec api python manage.py migrate

skill_seed:
	docker-compose exec api python manage.py skill_seed

language_seed:
	docker-compose exec api python manage.py language_seed

roles_seed:
	docker compose exec api python manage.py role_seed

user_seed:
	docker-compose exec api python manage.py user_seed

restart:
	docker-compose restart api

rebuild:
	docker-compose up --build