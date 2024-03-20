FROM python:3.8.12-slim

COPY ml_logic ml_logic
COPY api api
COPY requirements.txt requirements.txt
COPY setup.py setup.py
COPY credentials/the-mdr-project.json credentials/the-mdr-project.json

#RUN pip install -r requirements.txt
RUN pip install -e .
RUN mkdir models
RUN mkdir raw_data


# Local
#CMD uvicorn api.fast:app --host 0.0.0.0

# Production
CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
