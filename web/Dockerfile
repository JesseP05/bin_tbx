# syntax=docker/dockerfile:1

FROM python:3.11-slim

RUN echo "bleep boop, starting webserver.."
WORKDIR /app

# geen pycache in container
ENV PYTHONDONTWRITEBYTECODE=1

# install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# flask naar container
COPY . .

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]

