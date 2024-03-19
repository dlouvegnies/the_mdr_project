import os
import numpy as np

##################  VARIABLES  ##################
GCP_PROJECT = os.environ.get('GCP_PROJECT')
GCP_DB = os.environ.get('GCP_DB')
CAT_TABLE = os.environ.get('CAT_TABLE')
NEWS_TABLE = os.environ.get('NEWS_TABLE')
USER_TABLE = os.environ.get('USER_TABLE')

CREDENTIAL_NAME = os.environ.get('CREDENTIAL_NAME')
USER_ID = os.environ.get('USER_ID')

##################  CONSTANTS  #####################
CREDENTIAL_PATH = os.path.join("credentials", CREDENTIAL_NAME)
CATEGORIES_ID = [1, 3, 5]
