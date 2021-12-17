# Tomography API

Backend for accessing tomography data built using FastAPI.

To start, go to `app` directory and then run 
```
uvicorn main:app --reload
```
which by default will start local development server in http://127.0.0.1:8000

You can find the OpenAPI documentation in `/docs`


## Deployment

To deploy, build the tomo-api container and then run with `--add-host` flag
```
docker container rm -f tomo-api
docker build -t tomo-api .
docker run -d --name tomo-api -p 8080:80 --add-host host.docker.internal:host-gateway tomo-api
```