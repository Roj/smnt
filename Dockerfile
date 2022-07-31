FROM python:3.8

ENV PATH="/root/.local/bin:$PATH"
ENV PATH="/root/.local/pipx/venvs/poetry/bin/:$PATH"


RUN pip install pipx
RUN pipx install poetry==1.1.6
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /smnt/
WORKDIR /smnt
RUN poetry install --no-interaction --no-root

COPY . /smnt
RUN poetry install --no-interaction

