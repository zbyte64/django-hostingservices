from dockit import schema

from hostingservices.services.models import Service, ServicePlan
from hostingservices.utils import passgen


class RDSService(Service):
    host = schema.CharField()
    admin_user = schema.CharField()
    admin_pass = schema.CharField()
    
    #TODO we should not pass a password as an argument, could show up in ps -A. We should connect directly with a mysql connection object
    
    def add_plan(self, site, **kwargs):
        """
        Returns a service plan
        """
        password = passgen(16)
        info = {'dbname':site.slug[:16],
                'dbuser':passgen(),
                'dbpass':password,
                'dbhost':self.host,}
        all_params = dict(info)
        all_params.update({
            'host':self.host,
            'admin_user': self.admin_user,
            'admin_pass': self.admin_pass,})
        cmd = '''echo "create database %(dbname)s character set utf8; grant all on %(dbname)s.* to '%(dbuser)s@'%%' identified by '%(dbpass)s'; flush privileges;" | mysql -u %(admin_user)s -p %(admin_pass)s -h %(host)s'''
        
        shell = self.get_shell()
        response = shell.run(cmd % all_params)
        response.join()
        active = not response.returncode
        
        plan = RDSServicePlan(service=self,
                              site=site,
                              add_log=shell.logger.read_log(),
                              active=active,
                              environ=info,)
        plan.save()
        return plan
    
    def remove_plan(self, plan):
        all_params = {
            'dbname':plan.environ['dbname'],
            'host':self.host,
            'admin_user': self.admin_user,
            'admin_pass': self.admin_pass,}
        cmd = '''echo "drop database %(dbname)s; flush privileges;" | mysql -u %(admin_user)s -p %(admin_pass)s -h %(host)s'''
        
        shell = self.get_shell()
        response = shell.run(cmd % all_params)
        response.join()
        
        plan.remove_log = shell.logger.read_log()
        plan.save()
    
    class Meta:
        typed_key = 'rds_service'

class RDSServicePlan(ServicePlan):
    def get_service_url(self):
        return 'mysql://%(dbuser)s:%(dbpass)s@%(dbhost)s/%(dbname)s' % self.enviorn
    
    def get_environ(self):
        return {'DATABASE_URL': self.get_service_url()}
    
    class Meta:
        typed_key = 'rds_service'

