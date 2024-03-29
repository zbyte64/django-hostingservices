import MySQLdb

from dockit import schema

from hostingservices.services.models import Service, ServicePlan
from hostingservices.utils import passgen


class MysqlService(Service):
    host = schema.CharField()
    port = schema.IntegerField(default=3306)
    admin_user = schema.CharField()
    admin_pass = schema.CharField(blank=True)
    
    def get_admin_connection(self):
        db = MySQLdb.connect(host=self.host, user=self.admin_user, passwd=self.admin_pass, port=self.port)
        return db
    
    def add_plan(self, site, **kwargs):
        """
        Returns a service plan
        """
        password = passgen(16)
        info = {'dbname':site.slug[:16],
                'dbuser':passgen(),
                'dbpass':password,
                'dbhost':self.host,
                'dbport':self.port,}
        commands = ["create database %(dbname)s character set utf8", 
                    "grant all on %(dbname)s.* to '%(dbuser)s'@'%%' identified by '%(dbpass)s'",
                    "flush privileges",]
        
        connection = self.get_admin_connection()
        c = connection.cursor()
        for cmd in commands:
            c.execute(cmd % info)
        
        plan = MysqlServicePlan(service=self,
                              site=site,
                              add_log='',
                              active=True,
                              environ=info,)
        plan.save()
        return plan
    
    def remove_plan(self, plan):
        commands = ["drop database %(dbname)s",
                    "flush privileges",]
        
        connection = self.get_admin_connection()
        c = connection.cursor()
        for cmd in commands:
            c.execute(cmd % plan.environ)
    
    class Meta:
        typed_key = 'mysql_service'

class MysqlServicePlan(ServicePlan):
    def get_service_url(self):
        return 'mysql://%(dbuser)s:%(dbpass)s@%(dbhost)s:%(dbport)s/%(dbname)s' % self.environ
    
    def get_environ(self):
        return {'DATABASE_URL': self.get_service_url()}
    
    def get_db_connection(self):
        db = MySQLdb.connect(host=self.environ['dbhost'], user=self.environ['dbuser'], passwd=self.environ['dbpass'], port=self.environ['dbport'])
        return db
    
    class Meta:
        typed_key = 'mysql_service'

class DatabaseBackup(schema.Document):
    service_plan = schema.ReferenceField(MysqlServicePlan)
    backup = schema.FileField(upload_to='mysql/backups/', blank=True, null=True)
    timestamp = schema.DateTimeField()
    
    def perform_backup(self):
        pass

