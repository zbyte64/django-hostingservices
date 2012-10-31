from dockit import schema

from hostingservices.services.models import Service, ServicePlan
from hostingservices.utils import passgen


class RabbitmqService(Service):
    host = schema.CharField()
    port = schema.IntegerField(default=5672)
    
    def add_plan(self, site, **kwargs):
        """
        Returns a service plan
        """
        password = passgen(16)
        info = {'name':site.slug[:16],
                'user':passgen(),
                'pass':password,
                'host':self.host,
                'port':self.port,}
        commands = ['sudo rabbitmqctl add_user %(user)s %(pass)s',
                    'sudo rabbitmqctl add_vhost %(name)s',
                    'sudo rabbitmqctl set_permissions -p %(name)s %(user)s ".*" ".*" ".*"',]
        
        shell = self.get_shell()
        for cmd in commands:
            shell.run(cmd % info)
        
        plan = RabbitmqServicePlan(service=self,
                              site=site,
                              add_log=shell.logger.read_log(),
                              active=True,
                              environ=info,)
        plan.save()
        return plan
    
    def remove_plan(self, plan):
        commands = ['sudo rabbitmqctl delete_user %(user)s',
                    'sudo rabbitmqctl delete_vhost %(name)s',]
        
        shell = self.get_shell()
        for cmd in commands:
            shell.run(cmd % plan.environ)
    
    class Meta:
        typed_key = 'rabbitmq_service'

class RabbitmqServicePlan(ServicePlan):
    def get_service_url(self):
        return 'amqp://%(user)s:%(pass)s@%(host)s:%(port)s/%(name)s' % self.environ
    
    def get_environ(self):
        return {'BROKER_URL': self.get_service_url()}
    
    class Meta:
        typed_key = 'rabbitmq_service'

