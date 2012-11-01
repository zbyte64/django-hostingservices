from dockit import schema

from hostingservices.services.models import ServicePlan
from hostingservices.supervisor_services.models import SupervisorService


class MemcacheService(SupervisorService):
    host_name = schema.CharField(default='localhost')
    memory_size = schema.IntegerField(help_text='Number of megabytes to allocate')
    start_port = schema.IntegerField(default=11211)
    end_port = schema.IntegerField()
    active_ports = schema.SetField(schema.IntegerField(), editable=False, blank=True)
    
    template_name = 'memcache_services/supervisor.conf'
    
    def get_service_plan_class(self):
        return MemcacheServicePlan
    
    def get_plan_environ(self, site):
        environ = super(MemcacheService, self).get_plan_environ(site)
        environ['host'] = self.host_name
        ports = set(range(self.start_port-1, self.end_port))
        ports -= self.active_ports
        environ['port'] = list(ports)[0]
        return environ
    
    def add_plan(self, site, **kwargs):
        plan = super(MemcacheService, self).add_plan(site, **kwargs)
        self.active_ports.add(plan.environ['port'])
        self.save()
        return plan
    
    def remove_plan(self, plan):
        super(MemcacheService, self).remove_plan(plan)
        self.active_ports.remove(plan.environ['port'])
        self.save()
    
    class Meta:
        typed_key = 'memcache_service'

class MemcacheServicePlan(ServicePlan):
    def get_service_url(self):
        return 'memcache://%(host)s:%(port)s/' % self.environ
    
    def get_environ(self):
        return {'CACHE_URL': self.get_service_url()}
    
    class Meta:
        typed_key = 'memcache_serviceplan'
