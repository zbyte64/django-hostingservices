import os

from django.template import Context
from django.template.loader import get_template

from dockit import schema

from hostingservices.services.models import Service, ServicePlan
from hostingservices.supervisor_services.app_settings import SUPERVISORD_CONF_DIRECTORY

#TODO this requires sudo; please set it up so no password is required for sudo for task user

class SupervisorService(Service):
    """
    A service where each plan is a supervisor entry
    Extend and set your own template and context functions
    """
    template_name = None
    
    def get_supervisor_conf_directory(self):
        return SUPERVISORD_CONF_DIRECTORY
    
    def get_conf_path(self, site):
        return os.path.join(self.get_supervisor_conf_directory(), '%s.%s.conf' % (site.slug, self.service_type))
    
    def get_service_name(self, site):
        return '%s_%s' % (site.slug, self.service_type)
    
    def get_plan_environ(self, site):
        return {'service_name':self.get_service_name(site),}
    
    def get_conf_context(self, site):
        context = {'site':site,
                   'service':self,}
        context.update(self.get_plan_environ(site))
        return Context(context)
    
    def get_conf_template_name(self):
        return self.template_name
    
    def get_conf_template(self):
        return get_template(self.get_conf_template_name())
    
    def get_service_plan_class(self):
        return ServicePlan
    
    def add_plan(self, site, **kwargs):
        """
        Returns a service plan
        Creates a new supervisor conf file and writes it to the conf directory
        Then reload supervisor
        CONSIDER: perhaps each user should get their own supervisor handler?
        """
        conf_path = self.get_conf_path(site)
        if os.path.exists(conf_path):
            raise TypeError, "Service already exists"
        
        context = self.get_conf_context(site)
        info = self.get_plan_environ(site)
        template = self.get_conf_template()
        
        conf = template.render(context)
        
        conf_file = open(conf_path, 'w')
        conf_file.write(conf)
        conf_file.close()
        
        commands = ['sudo supervisorctl update',
                    'sudo supervisorctl start %(service_name)s',]
        
        shell = self.get_shell()
        for cmd in commands:
            shell.run(cmd % info)
        
        plan_class = self.get_service_plan_class()
        
        plan = plan_class(service=self,
                          site=site,
                          add_log=shell.logger.read_log(),
                          active=True,
                          environ=info,)
        plan.save()
        return plan
    
    def remove_plan(self, plan):
        shell = self.get_shell()
        
        shell.run('sudo supervisorctl stop %(service_name)s' % plan.environ)
        
        conf_file = self.get_conf_path(plan.site)
        shell.run('sudo rm -f "%s"' % conf_file)
        
        shell.run('sudo supervisorctl update')
    
    class Meta:
        proxy = True

