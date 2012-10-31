import hyperadmin

from dockitresource.resources import DocumentResource

from hostingservices.services.models import HostedSite, Service, ServicePlan, ServicePlanRequest


class HostedSiteResource(DocumentResource):
    pass
    #environ_link => r/o form representing environ variable

hyperadmin.site.register(HostedSite, HostedSiteResource)

class ServiceResource(DocumentResource):
    pass
    #add_plan_link => create service plan request, schedule task

hyperadmin.site.register(Service, ServiceResource)

class ServicePlanResource(DocumentResource):
    pass
    #remove_plan_link => create service plan request, schedule task

hyperadmin.site.register(ServicePlan, ServicePlanResource)

class ServicePlanRequestResource(DocumentResource):
    pass

hyperadmin.site.register(ServicePlanRequest, ServicePlanRequestResource)

#TODO additionaly make a resource site for the public facing API
