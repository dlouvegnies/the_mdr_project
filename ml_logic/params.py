import os
import numpy as np

##################  VARIABLES  ##################
GCP_PROJECT = os.environ.get('GCP_PROJECT')
GCP_DB = os.environ.get('GCP_DB')
CAT_TABLE = os.environ.get('CAT_TABLE')
NEWS_TABLE = os.environ.get('NEWS_TABLE')
USER_TABLE = os.environ.get('USER_TABLE')
REVIEW_TABLE = os.environ.get('REVIEW_TABLE')

CREDENTIAL_NAME = os.environ.get('CREDENTIAL_NAME')
#USER_ID = int(os.environ.get('USER_ID'))

MODE = os.environ.get('MODE')

MODEL_NEWS_BATCH_SIZE = int(os.environ.get('MODEL_NEWS_BATCH_SIZE'))
MODEL_MAX_FEATURES    = int(os.environ.get('MODEL_MAX_FEATURES'))
CACHE_VALIDATION_DURATION = int(os.environ.get('CACHE_VALIDATION_DURATION'))

##################  CONSTANTS  #####################
CREDENTIAL_PATH = os.path.join("credentials", CREDENTIAL_NAME)
CATEGORIES_ID = [6, 8]

CAT_TABLE_ID=f'{GCP_PROJECT}.{GCP_DB}.{CAT_TABLE}'
NEWS_TABLE_ID=f'{GCP_PROJECT}.{GCP_DB}.{NEWS_TABLE}'
USER_TABLE_ID = f'{GCP_PROJECT}.{GCP_DB}.{USER_TABLE}'
REVIEW_TABLE_ID = f'{GCP_PROJECT}.{GCP_DB}.{REVIEW_TABLE}'

SERVICE_URL = 'https://mdr-gzqmj6mx3q-ew.a.run.app/'
LOCAL_URL = 'http://127.0.0.1:8000'

##################  BDD  #####################
DB_SERVER=os.environ.get('DB_SERVER')
USER_DB=os.environ.get('USER_DB')
PASSWORD_DB=os.environ.get('PASSWORD_DB')
DB_NAME=os.environ.get('DB_NAME')
