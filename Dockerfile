FROM python

RUN apt-get update && apt-get install -y ffmpeg

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python -

COPY poetry.lock pyproject.toml ./

ENV PATH=/root/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN poetry install --no-root

COPY . .

CMD ["python", "main.py"]




