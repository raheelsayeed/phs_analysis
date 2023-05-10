#!/usr/bin/python3

class TaskAttempt(object):
    
    Code = 'taskattemptv2'

    def __init__(self, observation) -> None:

        if observation.code.coding[0].code != TaskAttempt.Code:
            return None
        
        components = observation.component
        for comp in components:
            code = comp.code.coding[0].code
            if code == 'task-period':
                self.start = comp.valuePeriod.start.date
                self.end   = comp.valuePeriod.end.date
            elif code == 'task-result-status':
                self.result = comp.valueString
            elif code == 'task-identifier':
                self.task_id = comp.valueString
        
        self.resource = observation
        self.reference_uri = observation.subject.reference
        



    
    def as_dict(self):
        return {
            'task_id': self.task_id,
            'task_elapsed_time': self.elapsed,
            'task_begin': self.start,
            'task_end': self.end,
            'task_result': self.result,
            'subject': self.reference_uri
        }

    @classmethod
    def from_observation(cls, observation):
        pass

    
    @property
    def elapsed(self):
        if None == self.end:
            return None
        duration = self.end - self.start
        return duration.total_seconds()
    
    @classmethod 
    def TaskmetricObservations(cls, observations):
        return [obs for obs in observations if obs.code.coding[0].code == cls.Code]

    @classmethod
    def Observations(cls, observations):
        attempts = [cls.from_observation(o) for o in observations]
        return attempts if len(attempts) > 0 else None

