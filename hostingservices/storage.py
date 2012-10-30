from storages.backends.s3 import S3Storage, DEFAULT_ACL

from django.conf import settings

class UnicodeSafeS3Storage(S3Storage):
    def _clean_name(self, name):
        #herp derp in python 2.7 plus someone prematurely closing an issue: https://bitbucket.org/david/django-storages/issue/64/unicode-filenames-problem-with-rackspace
        return str(super(UnicodeSafeS3Storage, self)._clean_name(name))

class StaticS3FileStorage(UnicodeSafeS3Storage):
    """
Standard file system storage for static files.
"""
    def __init__(self, bucket=settings.AWS_STATIC_STORAGE_BUCKET_NAME, acl=DEFAULT_ACL):
        super(StaticS3FileStorage, self).__init__(bucket=bucket, acl=acl)
        settings.STATIC_URL = self.generator.make_bare_url(bucket)
        
        self.connection.create_bucket(bucket)
    
    def listdir(self, name):
        raise OSError

    def write(self, name, content):
        return self._put_file(name, content)
    
    def get_available_name(self, name):
        return name
    
    #TODO update by timestamp detection and possibly checksum


