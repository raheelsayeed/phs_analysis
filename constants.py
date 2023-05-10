_PPMG_TAG_DEBUG = 'people-heart-study-debug'
_PPMG_TAG_PROD = 'people-heart-study'


def PPMG_TAG_PROD():
    return _PPMG_TAG_PROD

def PPMG_TAG_DEBUG():
    return _PPMG_TAG_DEBUG


# =================================================================================


_AWS_REGION = 'us-east-1'
def AWS_REGION():
    return _AWS_REGION

# HealthLake

_HEALTHLAKE_DATASTORE_ID = '<>'
_HEALTHLAKE_DATASTORE_ENDPOINT = f'https://healthlake.{_AWS_REGION}.amazonaws.com/datastore/{_HEALTHLAKE_DATASTORE_ID}/r4/'
_HEALTHLAKE_DATA_ACCESS_ROLE = ''

# 


def HEALTHLAKE_DATASTORE_ID():
    return _HEALTHLAKE_DATASTORE_ID

def HEALTHLAKE_DATASTORE_ENDPOINT():
    return _HEALTHLAKE_DATASTORE_ENDPOINT

def HEALTHLAKE_DATA_ACCESS_ROLE():
    return _HEALTHLAKE_DATA_ACCESS_ROLE
