FROM python:3.11

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .
COPY README.md .
COPY rstore_example_api rstore_example_api

RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "-m", "rstore_example_api"]
