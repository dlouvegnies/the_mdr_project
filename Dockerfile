FROM python:3.8.12-slim

COPY models models
COPY ml_logic ml_logic
COPY requirements.txt requirements.txt
COPY setup.py setup.py

#RUN pip install -r requirements.txt
RUN pip install -e .

# Local
CMD uvicorn package_folder.api_file:app --host 0.0.0.0

# Production
#CMD uvicorn package_folder.api_file:app --host 0.0.0.0 --port $PORT
