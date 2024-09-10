FROM python:3.12.6-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Setando o diretório principal
WORKDIR $APP_HOME

# Copiando arquivos
COPY uv.lock pyproject.toml .python-version src ./

# Atualizando e configurando localização
RUN apt-get update
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/'        /etc/locale.gen \
    && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen
ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8

# Instalando o uv
RUN pip install uv==0.4.8

# Sincronizando as bibliotecas com o uv e instalando gunicorn
RUN uv sync --frozen
RUN uv add gunicorn

# Comando ao iniciar o container
CMD uv run gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 app:server