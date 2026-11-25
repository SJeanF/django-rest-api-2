FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Adicionando o ambiente virtual ao PATH
ENV PATH="$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Atualizado: Puxa o Poetry 2.0+ para suportar a tag [project]
RUN pip install "poetry>=2.0.0"

WORKDIR $PYSETUP_PATH

# Copia os arquivos de lock e config
COPY poetry.lock pyproject.toml ./

# O --no-root garante que ele baixe as libs (Django, DRF, etc) sem tentar instalar o seu app "bookstore" ainda
# Removemos o --without dev para ele instalar o pytest também
RUN poetry install --no-root

WORKDIR /app

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]