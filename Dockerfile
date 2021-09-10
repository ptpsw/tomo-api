FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /app
RUN python3 -m pip install -r requirements.txt