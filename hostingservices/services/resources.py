from django.conf.urls.defaults import patterns, url, include

import hyperadmin
from hyperadmin.resources import BaseResource
from hyperadmin.hyperobjects import Link

from dockitresource.resources import DocumentResource

from hostingservices.services.models import HostedSite, Service, ServicePlan, ServicePlanRequest
from hostingservices.services.views import EnvironView, AddPlanView, RemovePlanView
from hostingservices.services.forms import EnvironForm, AddPlanForm, RemovePlanForm


class EnvironResource(BaseResource):
    form_class = EnvironForm
    detail_view = EnvironView
    
    def get_app_name(self):
        return self.parent.app_name
    app_name = property(get_app_name)
    
    def get_resource_name(self):
        return '-environ'
    resource_name = property(get_resource_name)
    
    def get_prompt(self):
        return self.resource_name
    
    def get_form_kwargs(self, **kwargs):
        kwargs['instance'] = self.state['parent']
        return kwargs
    
    def get_urls(self):
        def wrap(view, cacheable=False):
            return self.as_view(view, cacheable)
        
        init = self.get_view_kwargs()
        
        # Admin-site-wide views.
        urlpatterns = self.get_extra_urls()
        urlpatterns += patterns('',
            url(r'^$',
                wrap(self.detail_view.as_view(**init)),
                name='environ'),
        )
        return urlpatterns
    
    def get_absolute_url(self):
        return self.reverse('environ', pk=self.state['parent'].pk)
    
    def get_environ_link(self, form_kwargs=None, **kwargs):
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs = self.get_form_kwargs(**form_kwargs)
        
        link_kwargs = {'url':self.get_absolute_url(),
                       'resource':self,
                       'method':'GET',
                       'form_kwargs':form_kwargs,
                       'form_class': self.get_form_class(),
                       'prompt':'environment variables',
                       'rel':'environ',}
        link_kwargs.update(kwargs)
        environ_link = Link(**link_kwargs)
        return environ_link


class HostedSiteResource(DocumentResource):
    def __init__(self, **kwargs):
        super(HostedSiteResource, self).__init__(**kwargs)
        self.environ_resource = EnvironResource(self.resource_adaptor, self.site, parent_resource=self)
    
    def get_extra_urls(self):
        def wrap(view, cacheable=False):
            return self.as_view(view, cacheable)
        
        init = self.get_view_kwargs()
        
        # Admin-site-wide views.
        base_name = self.get_base_url_name()
        urlpatterns = super(HostedSiteResource, self).get_extra_urls()
        urlpatterns += patterns('',
            url(r'^(?P<pk>\w+)/environ/',
                include(self.environ_resource.urls)),
        )
        return urlpatterns
    
    def get_item_outbound_links(self, item):
        links = super(HostedSiteResource, self).get_item_outbound_links(item)
        environ = self.environ_resource.fork_state(parent=item.instance)
        links.append(environ.get_resource_link(link_factor='LO'))
        return links

hyperadmin.site.register(HostedSite, HostedSiteResource)

class ServiceResource(DocumentResource):
    add_plan_view = AddPlanView
    add_plan_form_class = AddPlanForm
    
    def get_extra_urls(self):
        def wrap(view, cacheable=False):
            return self.as_view(view, cacheable)
        
        init = self.get_view_kwargs()
        
        # Admin-site-wide views.
        base_name = self.get_base_url_name()
        urlpatterns = super(ServiceResource, self).get_extra_urls()
        urlpatterns += patterns('',
            url(r'^(?P<pk>\w+)/add-plan/$',
                wrap(self.add_plan_view.as_view(**init)),
                name='%saddplan' % base_name),
        )
        return urlpatterns
    
    def get_add_plan_url(self, item):
        return self.reverse('%saddplan' % self.get_base_url_name(), pk=item.instance.pk)
    
    def get_add_plan_form_class(self):
        return self.add_plan_form_class
    
    def get_add_plan_link(self, item, form_kwargs=None, **kwargs):
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs = self.get_form_kwargs(item, **form_kwargs)
        
        link_kwargs = {'url':self.get_add_plan_url(item),
                       'resource':self,
                       'method':'POST',
                       'on_submit': self.handle_add_plan_submission,
                       'form_kwargs':form_kwargs,
                       'form_class': self.get_add_plan_form_class(),
                       'prompt':'add plan',
                       'rel':'add-plan',}
        link_kwargs.update(kwargs)
        addplan_link = Link(**link_kwargs)
        return addplan_link
    
    def get_service_plan_request_resource(self):
        return self.site.registry[ServicePlanRequest]
    
    def get_item_outbound_links(self, item):
        links = super(ServiceResource, self).get_item_outbound_links(item)
        links.append(self.get_add_plan_link(item, link_factor='LO'))
        return links
    
    def handle_add_plan_submission(self, link, submit_kwargs):
        form = link.get_form(**submit_kwargs)
        if form.is_valid():
            instance = form.save()
            resource = self.get_service_plan_request_resource()
            resource_item = resource.get_resource_item(instance)
            return self.on_add_plan_success(resource_item)
        return link.clone(form=form)
    
    def on_add_plan_success(self, item):
        return item.get_item_link()

hyperadmin.site.register(Service, ServiceResource)

class ServicePlanResource(DocumentResource):
    remove_plan_view = RemovePlanView
    remove_plan_form_class = RemovePlanForm
    
    def get_extra_urls(self):
        def wrap(view, cacheable=False):
            return self.as_view(view, cacheable)
        
        init = self.get_view_kwargs()
        
        # Admin-site-wide views.
        base_name = self.get_base_url_name()
        urlpatterns = super(ServicePlanResource, self).get_extra_urls()
        urlpatterns += patterns('',
            url(r'^(?P<pk>\w+)/remove-plan/$',
                wrap(self.remove_plan_view.as_view(**init)),
                name='%sremoveplan' % base_name),
        )
        return urlpatterns
    
    def get_remove_plan_url(self, item):
        return self.reverse('%sremoveplan' % self.get_base_url_name(), pk=item.instance.pk)
    
    def get_remove_plan_form_class(self):
        return self.remove_plan_form_class
    
    def get_remove_plan_link(self, item, form_kwargs=None, **kwargs):
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs = self.get_form_kwargs(item, **form_kwargs)
        
        link_kwargs = {'url':self.get_remove_plan_url(item),
                       'resource':self,
                       'method':'POST',
                       'on_submit': self.handle_remove_plan_submission,
                       'form_kwargs':form_kwargs,
                       'form_class': self.get_remove_plan_form_class(),
                       'prompt':'remove plan',
                       'rel':'remove-plan',}
        link_kwargs.update(kwargs)
        removeplan_link = Link(**link_kwargs)
        return removeplan_link
    
    def get_item_outbound_links(self, item):
        links = super(ServicePlanResource, self).get_item_outbound_links(item)
        if item.instance.active:
            links.append(self.get_remove_plan_link(item, link_factor='LO'))
        return links
    
    def get_service_plan_request_resource(self):
        return self.site.registry[ServicePlanRequest]
    
    def handle_remove_plan_submission(self, link, submit_kwargs):
        form = link.get_form(**submit_kwargs)
        if form.is_valid():
            instance = form.save()
            resource = self.get_service_plan_request_resource()
            resource_item = resource.get_resource_item(instance)
            return self.on_remove_plan_success(resource_item)
        return link.clone(form=form)
    
    def on_remove_plan_success(self, item):
        return item.get_item_link()

hyperadmin.site.register(ServicePlan, ServicePlanResource)

class ServicePlanRequestResource(DocumentResource):
    def get_service_plan_resource(self):
        return self.site.registry[ServicePlan]
    
    def get_item_outbound_links(self, item):
        links = super(ServicePlanRequestResource, self).get_item_outbound_links(item)
        if item.instance.plan:
            resource = self.get_service_plan_resource()
            item = resource.get_resource_item(item.instance.plan)
            links.append(resource.get_item_link(item, link_factor='LO'))
        return links
    
    #TODO link for re-executing request

hyperadmin.site.register(ServicePlanRequest, ServicePlanRequestResource)

#TODO additionaly make a resource site for the public facing API
