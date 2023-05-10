
#!/usr/bin/python3


from datetime import datetime
import pandas as pd 
import json, time, base64, ndjson, requests
from fhirclient.models import patient, questionnaireresponse, consent, researchsubject, researchstudy, condition, observation, medication, medicationrequest, medicationstatement, riskassessment, communicationrequest, fhirdate
from fhirclient import server
from fhirclient.models import fhirabstractbase, resource 
from fhirclient.models import domainresource as dr
from taskmetric import * 
from participant import * 


class Record(object):

    def __init__(self, fhirjson):
        
        resource_type = fhirjson['resourceType']

        self.resource = None 
        self.name       = None
        self.value      = None 
        self.code       = None
        self.date       = None 
        
        # Observation 
        if resource_type == 'Observation':
            self.resource = observation.Observation(fhirjson) 
            self.assignObservation()

        elif resource_type == 'Condition':
            self.resource = condition.Condition(fhirjson)
            self.assignCondition()

        elif resource_type == 'QuestionnaireResponse':
            self.resource = questionnaireresponse.QuestionnaireResponse(fhirjson)
            self.assignQuestionnaireResponse() 

        elif resource_type == 'MedicationRequest':
            self.resource = medicationrequest.MedicationRequest(fhirjson)
            self.assignMedicationRequest()

        elif resource_type == 'Medication':
            self.resource = medication.Medication(fhirjson)
            self.assignMedication()

        elif resource_type == 'MedicationStatement':
            self.resource = medicationstatement.MedicationStatement(fhirjson)
            self.assignMedicationStatement()

        elif resource_type == 'CommunicationRequest':
            self.resource = communicationrequest.CommunicationRequest(fhirjson)
            self.assignCommunicationRequest()

        if isinstance(self.date, datetime):
            self.date = self.date.date()


    @property 
    def resource_type(self): 
        return self.resource.resource_type if self.resource is not None else None

    @property 
    def reference_uri(self):
        if self.resource.subject is not None:
            return self.resource.subject.reference
        else:
            return None


    @property 
    def identifier(self):
        return self.resource.id 

    def __str__(self):
        return f'Record: {self.resource_type}\t{self.date}\t{self.code}\t{self.name}\t{self.value}'

    def as_json(self):
        return {
            'identifier': self.identifier,
            'name': self.name,
            'code': self.code,
            'date': self.date,
            'value': self.value,
            'subject_id': self.reference_uri,
            'resource_type': self.resource_type,
        }

    def assignCondition(self):
        pass 

    def assignQuestionnaireResponse(self):

        self.code = self.resource.identifier.value

        cnt = len(self.resource.item) 
        
        if cnt == 1:
            # only one answer. 
            answer = self.resource.item[0].answer[0] 
            if answer.valueBoolean is not None:
                self.value = answer.valueBoolean
            elif answer.valueQuantity is not None:
                self.value = answer.valueQuantity.value 
            elif answer.valueCoding is not None:
                self.value = answer.valueCoding.code 

        self.date = self.resource.authored.date

        
    def assignObservation(self):
        
        
        self.code = self.resource.code.coding[0].code 
        if self.resource.effectiveDateTime is not None:
            self.date = self.resource.effectiveDateTime.date
        else:
            self.date = self.resource.meta.lastUpdated.date

        labname = self.resource.code.text 
        if labname is not None: 
            self.name = labname
        else:
            self.name = self.code 


        obstype = self.resource.category[0].coding[0].code
        if obstype == 'laboratory':
            self.value = self.resource.valueQuantity.value
        
        if self.code == '55284-4':
            components = self.resource.component 
            self.value = [c.valueQuantity.value for c in components] 

    def assignMedicationRequest(self):

        self.date = self.resource.authoredOn.date
        
        self.name = self.resource.medicationCodeableConcept.text or self.resource.medicationCodeableConcept.coding[0].display

        self.value = 1 

        medcode = self.resource.medicationCodeableConcept.coding 
        if medcode is not None: 
            self.code = medcode[0].code 

    def assignMedicationStatement(self):

        self.name = self.resource.medicationCodeableConcept.text or self.resource.medicationCodeableConcept.coding[0].display

        self.value = 1 

        if self.resource.effectiveDateTime is not None:
            self.date = self.resource.effectiveDateTime.date 
        elif self.resource.effectivePeriod is not None:
            self.date = self.resource.effectivePeriod.start.date 

        medcode = self.resource.medicationCodeableConcept.coding 
        if medcode is not None: 
            self.code = medcode[0].code 

    def assignMedication(self):
        pass 


    def assignCommunicationRequest(self):

       
        self.name = 'Study communication'

        self.date = self.resource.authoredOn.date

        self.code = self.resource.reasonCode[0].coding[0].code




    def assignRiskAssessment(self):

        pass 
