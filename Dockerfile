FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry lock && \
    poetry install --only main --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]


# docker build -t minishop .
# docker run -d --name miniShop -p 8000:8000 minishop