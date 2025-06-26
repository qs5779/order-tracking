# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION} AS builder

ARG POETRY_VERSION=2.1.3

#RUN apt-get update && apt-get install -y libpq-dev python3-dev

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

RUN pip install poetry==${POETRY_VERSION}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /orders

COPY poetry.lock pyproject.toml ./
RUN touch README.md LICENSE
RUN poetry sync --only main && rm -rf $POETRY_CACHE_DIR


FROM python:${PYTHON_VERSION}-slim AS runtime

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=1000
ARG ENV_STATE=prod

# need curl for healthcheck
RUN apt-get update && apt-get install -y curl

RUN echo "UID: ${UID}"
RUN echo "ENV_STATE: ${ENV_STATE}"
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Switch to the non-privileged user to run the application.
USER appuser

ENV ENV_STATE=${ENV_STATE}
ENV VIRTUAL_ENV=/orders/.venv \
    PATH="/orders/.venv/bin:$PATH"

WORKDIR /orders

# Copy the source code into the container.
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY runtime_env.${ENV_STATE} ./.env
# COPY wsgi.py .
COPY app ./app
COPY templates ./templates
COPY static ./static

# Expose the port that the application listens on.
EXPOSE 5000

# Run idle for testing
# CMD ["tail", "-f", "/dev/null"]

# Run the application.
CMD uvicorn app.main:app --host=0.0.0.0 --port=5000
