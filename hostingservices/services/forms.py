from django import forms

from dockit.forms.fields import SchemaChoiceField

from hostingservices.services.models import ServicePlanRequest, HostedSite

class EnvironForm(forms.Form):
    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(EnvironForm, self).__init__(**kwargs)
        for key, value in self.instance.get_environ().iteritems():
            self.fields[key] = forms.CharField()
            self.initial[key] = value

class AddPlanForm(forms.Form):
    site = SchemaChoiceField(HostedSite.objects.all())
    
    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(AddPlanForm, self).__init__(**kwargs)
    
    def get_service_plan_request_kwargs(self):
        return {'site': self.cleaned_data['site'],
                'service':self.instance,
                'action':'add'}
    
    def save(self):
        request = ServicePlanRequest(**self.get_service_plan_request_kwargs())
        request.save()
        request.schedule()
        return request

class RemovePlanForm(forms.Form):
    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(RemovePlanForm, self).__init__(**kwargs)
    
    def get_service_plan_request_kwargs(self):
        return {'site': self.instance.site,
                'service':self.instance.service,
                'plan':self.instance,
                'action':'remove'}
    
    def save(self):
        request = ServicePlanRequest(**self.get_service_plan_request_kwargs())
        request.save()
        request.schedule()
        return request

