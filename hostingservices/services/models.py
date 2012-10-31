import datetime

from dockit import schema


class HostedSite(schema.Document):
    slug = schema.SlugField()
    api_key = schema.CharField()
    
    def get_environ(self):
        environ = dict()
        plans = ServicePlan.objects.filter(site=self, active=True)
        for plan in plans:
            environ.update(plan.get_environ())
        return environ
    
    def __unicode__(self):
        return self.slug

HostedSite.objects.index('slug').commit()

class Service(schema.Document):
    #CONSIDER the following should be ran in a task
    #however they will be triggered by an API call, do we need an intermediate object?
    # /api/services/myrds/add_plan/ -> service request -> service plan
    def add_plan(self, site, **kwargs):
        """
        Returns a service plan
        """
        raise NotImplementedError
    
    def remove_plan(self, plan):
        raise NotImplementedError
    
    def execute_plan_request(self, plan_request):
        if plan_request.action == 'add':
            plan = self.add_plan(plan_request.site, **plan_request.params)
            plan_request.plan = plan
            plan_request.save()
            return plan
        if plan_request.action == 'remove':
            plan_request.relase()
            self.remove_plan(plan_request.plan)
        raise TypeError, 'Unrecognized Action: %s' % plan_request.action
    
    def get_shell(self, logger=None, cwd=None, **popen_kwargs):
        from hostingservices.utils import TaskLogger, ShellSession
        if logger is None:
            logger = TaskLogger()
        return ShellSession(logger, cwd=cwd, **popen_kwargs)
    
    class Meta:
        typed_field = 'service_type'

class ServicePlan(schema.Document):
    site = schema.ReferenceField(HostedSite)
    active = schema.BooleanField(default=True)
    service = schema.ReferenceField(Service)
    environ = schema.DictField()
    
    add_log = schema.TextField(blank=True)
    remove_log = schema.TextField(blank=True)
    
    add_date = schema.DateTimeField(default=datetime.datetime.now)
    remove_date = schema.DateTimeField(null=True, blank=True)
    
    def get_environ(self):
        return self.environ
    
    def release(self):
        self.remove_date = datetime.datetime.now()
        self.active = False
        self.save()
    
    class Meta:
        typed_field = 'service_plan_type'

ServicePlan.objects.index('site', 'active').commit()

class ServicePlanRequest(schema.Document):
    '''
    Represents a request to change a service plan
    '''
    site = schema.ReferenceField(HostedSite)
    pending = schema.BooleanField(default=True)
    service = schema.ReferenceField(Service)
    action = schema.CharField()
    plan = schema.ReferenceField(ServicePlan, blank=True, null=True)
    params = schema.DictField()
    log = schema.TextField(blank=True)
    failure_log = schema.TextField(blank=True)
    
    def execute_request(self):
        self.pending = False
        self.save()
        try:
            return self.service.execute_plan_request(self)
        except Exception as error:
            self.failure_log = str(error)
            #TODO include stack trace
            self.save()
    
    def schedule(self):
        from hostingservices.services.tasks import process_service_plan_request
        process_service_plan_request.delay(self.pk)

ServicePlanRequest.objects.index('pending').commit()

