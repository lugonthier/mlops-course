FROM python:3.12-slim-bullseye

WORKDIR /app


COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py server.py

ENTRYPOINT ["python", "server.py"] 

EXPOSE 8080