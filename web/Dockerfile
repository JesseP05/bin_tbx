# syntax=docker/dockerfile:1

FROM python:3.11-slim

RUN echo "bleep boop, starting webserver.."
WORKDIR /app

# geen pycache in container
ENV PYTHONDONTWRITEBYTECODE=1

# install requirements
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy shared code and flask app
COPY shared ./shared
COPY web/. .

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]

