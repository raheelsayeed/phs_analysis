#!/usr/bin/python3


import pandas as pd 
import json, time, base64, ndjson, requests
from fhirclient.models import patient, questionnaireresponse, consent, researchsubject, researchstudy, condition, observation, medicationrequest, riskassessment, communicationrequest, fhirdate, documentreference
from fhirclient import server
from fhirclient.models import fhirabstractbase
from taskmetric import * 
from participant import * 
from healthrecords import *
from datetime import date


class SubStatus(object):

    def __init__(self, sub=researchsubject.ResearchSubject):
        self.subject = sub 

    @property
    def status(self):
        return self.subject.status 

    @property 
    def time(self):
        tm = self.subject.meta.lastUpdated.date
        return tm 

    def __str__(self):
        return f'{self.status}\t{self.time}'

class Participant(object):
    
    def __init__(self, fhirpatient=patient.Patient, res_subjects=None,  consentresource=consent.Consent, taskattempts=[TaskAttempt]):
        
        # Enrollment
        self.fhirpatient = fhirpatient
        
        self.rsubjects = None 
        
        if res_subjects is not None:
            sortedsubjects = sorted(res_subjects, key=lambda x: x.time)
            self.rsubjects = sortedsubjects

        self.consent_resource = None

        # task 1
        self._gender = None 
        self._race   = None 
        self._birthdate = None 
        self.demographics_resource = None 

        # task 2
        self.records = None

        self.ppmg_report = None




        self.reference_uri = self.get_reference_uri()

        self.attempts = taskattempts
    
        

    @property
    def identifier(self):
        """The participant identifier property."""
        return self.fhirpatient.identifier[0].value


    @property 
    def enrolledDate(self):
        return self.fhirpatient.meta.lastUpdated.date 

    @property 
    def status(self): 
        """Most recent status of study participant"""
        if self.rsubjects is not None:
            return self.rsubjects[0].status
        return None

    @property 
    def name(self):
        nam = self.fhirpatient.name[0]
        fname = nam.given[0] 
        lname = nam.family 
        return fname + ' ' + lname

    def data_row(self):
        row = [self.identifier, self.name, self.enrolledDate, self.status]
        if self.attempts is not None:
            
            pass

        return row
                
    @staticmethod
    def make_dataframe(participants):
        array_of_participants = [p.data_row() for p in participants] 
        return pd.DataFrame(array_of_participants, columns=['id', 'name', 'enrollment_date', 'enrollment_status'])


    def get_reference_uri(self):
        return f'Patient/{self.fhirpatient.id}'

    def assign_healthrecord(self, records=[Record]):
        recs = list(filter(lambda r: r.reference_uri == self.reference_uri, records))
        self.records = recs if len(recs) > 0 else None
        return self.records


    def assign_consent_status(self, consent_list=[consent.Consent], rs_list=[researchsubject.ResearchSubject], attempts=None):
        self.get_consent(consent_list)
        self.assign_researchsubjects(rs_list)
        if attempts:
            self.assign_attempts(attempts)
    
    def assign_attempts(self, attempts=[TaskAttempt]):
        self.attempts = list(filter(lambda a: a.reference_uri == self.reference_uri, attempts))
        return self.attempts


    def get_consent(self, consent_list):
        self.consent_resource =  next(filter(lambda c: c.patient.reference == self.reference_uri, consent_list))
        return self.consent_resource

    def assign_researchsubjects(self, researchsubject_list):
        consent_ref = f'Consent/{self.consent_resource.id}'
        rsubs = list(filter(lambda rs: rs.individual.reference == self.reference_uri and rs.consent.reference == consent_ref, researchsubject_list))
        if len(rsubs) > 0:
            statuses = [SubStatus(rs) for rs in rsubs]
            sortedsubjects = sorted(statuses, key=lambda x: x.time, reverse=True)
            self.rsubjects = sortedsubjects

    def assign_report(self, document_ref_list):
        self.ppmg_report = next(filter(lambda c: c.subject.reference == self.reference_uri, document_ref_list))
        return self.ppmg_report




    def assign_demographics(self, survey_response=questionnaireresponse.QuestionnaireResponse):

        for itm in survey_response.item:
            link_id = itm.linkId 
            ans = itm.answer[0]

            if link_id == '/54126-8/21112-8':
                self._birthdate = ans.valueDate.date
            elif link_id == '/54126-8/54131-8':
                self._gender = ans.valueCoding.code 
            elif link_id == 'race':
                self._race = ans.valueCoding



    @property
    def age(self):
        if self._birthdate:
            today = date.today()
            _age = today.year - self._birthdate.year - ((today.month, today.day) < (self._birthdate.month, self._birthdate.day))
            return _age

    @property
    def gender(self):
        if self._gender:
            return 'male' if self._gender == 'LA2-8' else 'female'

    @property
    def race(self):
        if self._race:
            return self._race.display
    



    def attempts_dataframe(self):
        task1 = 'task1_demographics'
        task2 = 'tasl2_healthrecords'
        task3 = 'task3_riskfactors'
        task4 = 'task4_recommendations'
        task5 = 'task5_followup'







