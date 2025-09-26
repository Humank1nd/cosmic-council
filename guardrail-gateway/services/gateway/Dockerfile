FROM python:3.11-slim
WORKDIR /app
COPY services/gateway/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY services/gateway/app ./app
EXPOSE 8080
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
