from requests_auth_aws_sigv4 import  AWSSigV4
import requests
from requests.utils import requote_uri
import json, time, base64, ndjson, requests
from healthrecords import *



def get_json_array(fn, resource_type):
    fn = 'output/' + fn
    fhirresources = []
    with open (fn, 'r') as file_:
        for line in file_:
            json_ = json.loads(line)
            if resource_type is None:
                fhirresources.append(json_)
            else:
                fhirresources.append(resource_type(json_))
    return fhirresources if len(fhirresources) > 0 else None


# param: save_to_filename: NDJSON Formatted file saved locally
# param2: query: full length `GET` query
# param3: Auth signature 
def request_data(save_to_filename, query, auth=None):

    save_to_filename = 'output/' + save_to_filename
    url = requote_uri(query)
    print(f'\nQuery: {query}')
    request_result = requests.request('GET', url, auth=auth)
    count = 0
    json_objects = []
    with open(save_to_filename, 'w') as file_: 
        while True: 
            if request_result.status_code != 200:
                print(f'Request aborted: {request_result.status_code}')
                print(request_result.headers)

                break
            
            print('.', end='', flush=True)
            data = request_result.json()
            if data['resourceType'] != 'Bundle':
                file_.write(json.dumps(data) + '')
                break 

            if 'entry' not in data:
                print(f' {count}\t| {save_to_filename}')
                return json_objects
                break

            for entry in data['entry']:
                count += 1
                resource = entry['resource']
                json_objects.append(resource)
                file_.write(json.dumps(entry['resource']) + '\n')

            if 'link' not in data:
                print(f' {count}\t| {save_to_filename}')
                return json_objects
                break

            next_url = None 
            for lnk in data['link']:
                rel = lnk['relation']
                if rel == 'next':
                    next_url = lnk['url']
            
            if next_url is None:
                print(f' {count}\t| {save_to_filename}')
                return json_objects
                break 

            next_url = next_url[:-1] + '%3D' if next_url.endswith('=') else next_url

            # wait 1 second before querying again
            time.sleep(1)
            request_result = requests.request('GET', next_url, auth=auth)



# ======================================================================
# Make health record objects
def make_records_from_ndjsonfiles(file_list, participant_reference=None):
    data_records = []
    for fn in file_list: 
        with open('output/' + fn) as file_:
            for line in file_:
                record = Record(json.loads(line))
                data_records.append(record)
                # add method to sort.
    return data_records if len(data_records) > 0 else None 

def all_study_data_records():
    return make_records_from_ndjsonfiles([
        'Observation.ndjson',
        'QuestionnaireResponse.ndjson',
        'MedicationStatement.ndjson',
        'MedicationRequest.ndjson',
        'Medication.ndjson',
        'Condition.ndjson',
        'DocumentReference.ndjson',
        'CommunicationRequest.ndjson'
        ])
