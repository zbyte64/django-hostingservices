from django.conf import settings

SUPERVISORD_CONF_DIRECTORY = getattr(settings, 'SUPERVISORD_CONF_DIRECTORY', '/etc/supervisor/conf.d')
