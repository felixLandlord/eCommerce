# MiniShop

## FastAPI eCommerce API

MiniShop is a simple eCommerce API built with FastAPI. It includes features for user authentication, product management, cart functionality, and email notifications.

## Features

- **User Authentication:** Register, login, and manage users with JWT tokens.
- **Product Management:** Create, update, and delete products.
- **Cart Functionality:** Add products to the cart, update quantity, and view cart contents.
- **Email Notifications:** Sends order confirmation and other notifications via email.

## Tech Stack

- **FastAPI** - Web framework for building APIs.
- **Tortoise ORM** - Object Relational Mapper for interacting with the Sqlite database.
- **Sqlite** - Relational database for storing product, user, and order data.
- **Uvicorn** - ASGI server for running the FastAPI app.
- **Docker** - Containerization for the API and database services.
- **Docker Compose** - Tool for defining and running multi-container Docker applications.

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/felixLandlord/eCommerce.git
cd eCommerce
```

2. **Set up environment variables**:

```makefile
EMAIL=""
PASS="" 
SECRET=""
````
PASS is your gmail App password
SECRET is a random generated token using the secrets library in python

3. **Install dependencies**:
```bash
poetry install
poetry shell
```

4. **Build and run the Docker containers**:
```bash
docker-compose up -d
```

5. **Access the API**:
```bash
fastapi dev
```
- The FastAPI app will be available at http://localhost:8000.