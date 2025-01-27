## Database

Postgresql

# Getting Started

## Prerequisites

* Docker and Docker Compose
* Postman (for API testing)

## Installation and Setup

* docker-compose build
* docker-compose up
* docker network create shared_network
* docker-compose exec api python manage.py makemigrations
* docker-compose exec api python manage.py migrate
* docker-compose exec api python manage.py user_seed
* docker-compose exec api python manage.py skill_seed
* docker-compose exec api python manage.py language_seed
* docker-compose restart api
* docker-compose up --build
* docker-compose build api
* docker-compose exec api python manage.py startapp connection

## Installation and Setup Explained

* Build the Docker Containers:
  docker-compose build

* Run the Containers:
  docker-compose up

* Database Migrations:
  docker-compose exec api python manage.py migrate

* Seed the User Data:
  docker-compose exec api python manage.py user_seed

* Rebuild container
  docker-compose up --build
    

