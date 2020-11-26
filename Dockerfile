FROM python:3.8

ENV POETRY_VERSION=1.0.3 \
    POETRY_HOME="/opt/poetry" \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Setup poetry cli
RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR frosch_test
COPY poetry.lock pyproject.toml ./

# Run tests
RUN poetry install
COPY . ./

RUN poetry run python -m pylint frosch --fail-under 9.2
RUN poetry run python -m pytest tests
