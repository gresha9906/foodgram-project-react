## For the Review:
### domain: final-project.myddns.me
### Auth information for test project:
#### login: *admin@ad.ru*
#### password: *admin*
<br>

# Foodgram

Foodgram is a study project to learn Django backend.

The website allows users to publish recipes, subscribe to other users' publications, add favorite recipes to the "Favorites" list, and download a consolidated list of ingredients needed for selected dishes before going to the store.

## Stack of technologies

- React
- Django
- Django REST Framework
- PostgreSQL
- Docker
- nginx
- CI/CD

### Installation

Clone the repository.

Make your own .env file and fill it like this:
```
POSTGRES_DB=your db name
POSTGRES_USER=your db user
POSTGRES_PASSWORD=your db password
DB_HOST=your db host
DB_PORT=5432 for example
SECRET_KEY=django-secret-key
DEBUG=maybe false or true
ALLOWED_HOSTS=your host
```
Install Docker and Docker Compose.
Run the following command to build the project's Docker containers:

To run the project locally:

```console
docker-compose up --build -d
```
After that run the following command in the backend container to make migrations:

```console
python manage.py makemigrations
python manage.py migrate
```
To launch the project with CI/CD 

In this case we use Github Actions, so to use workflow we need to create Secrets for Actions:
```
SECRET_KEY              # secret key Django
DOCKER_PASSWORD         # Docker Hub password
DOCKER_USERNAME         # Docker Hub login
HOST                    # target server IP
USER                    # server username
PASSPHRASE              # passphrase for ssh
SSH_KEY                 # private ssh key
TELEGRAM_TO             # your telegram account ID
TELEGRAM_TOKEN          # token of your telegram bot
```
```
Each push in master branch will start:
- Test backend and frontend
- build and push docker image to docker hub
- deploy on remote server
- send message to telegram bot
```
After successful deploy you need to create superuser in backend docker container:
```console
python manage.py createsuperuser
```


## Features

Foodgram offers the following main features:

1.  **Homepage**: Displays a list of the six latest recipes sorted by publication date, with pagination for accessing more recipes.
2.  **Recipe Page**: Provides a detailed view of a recipe, including its description. Authenticated users can add the recipe to their favorites or shopping list and subscribe to the recipe's author.
3.  **User Profile Page**: Shows the user's name, all recipes published by the user, and an option to subscribe to the user.
4.  **Author Subscription**: Authenticated users can subscribe to authors by visiting their profile page or recipe page and clicking the "Subscribe to Author" button. The user can then view their subscribed authors' recipes on the "My Subscriptions" page, sorted by publication date.
5.  **Favorites List**: Authenticated users can add recipes to their favorites list by clicking the "Add to Favorites" button. They can view their personal list of favorite recipes on the "Favorites List" page.
6.   **Shopping List**: Authenticated users can add recipes to their shopping list by clicking the "Add to Shopping List" button. They can access the "Shopping List" page, which provides a downloadable file containing a consolidated list of ingredients required for all the recipes saved in the shopping list.
7.  **Tag Filtering**: Clicking on a tag name displays a list of recipes tagged with that specific tag. Multiple tags can be selected to filter the recipes.
8.  **User Registration and Authentication**: The project includes a user management system, allowing users to register and authenticate themselves.
