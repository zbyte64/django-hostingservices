from django.views.generic import View
from django import http

from hyperadmin.resources.views import ResourceViewMixin
from hyperadmin.resources.crud.views import CRUDView

from dockitresource.views import DocumentDetailMixin


class EnvironViewMixin(ResourceViewMixin):
    def get_parent(self):
        if not hasattr(self, '_parent'):
            queryset = self.resource.parent.get_queryset(self.request.user)
            self._parent = queryset.get(pk=self.kwargs['pk'])
        return self._parent
    
    def get_state_data(self):
        state = super(EnvironViewMixin, self).get_state_data()
        state['parent'] = self.get_parent()
        return state
    
    def get_environ_link(self, **form_kwargs):
        #form_kwargs.update(self.get_form_kwargs())
        return self.resource.get_resource_link(form_kwargs=form_kwargs)


class EnvironView(EnvironViewMixin, View):
    view_class = 'change_form'
    
    def get(self, request, *args, **kwargs):
        return self.generate_response(self.get_environ_link())

class AddPlanMixin(DocumentDetailMixin):
    def get_add_plan_link(self, form_kwargs=None, **link_kwargs):
        item = self.get_item()
        if form_kwargs is None: form_kwargs = dict()
        form_kwargs = self.get_form_kwargs(**form_kwargs)
        link_kwargs.update({'form_kwargs': form_kwargs,
                            'item':item})
        link_kwargs = self.get_link_kwargs(**link_kwargs)
        return self.resource.get_add_plan_link(**link_kwargs)

class AddPlanView(AddPlanMixin, CRUDView):
    view_class = 'change_form'
    
    def get(self, request, *args, **kwargs):
        return self.generate_response(self.get_add_plan_link(use_request_url=True))
    
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.can_change(self.object):
            return http.HttpResponseForbidden(_(u"You may not modify that object"))
        
        form_kwargs = self.get_request_form_kwargs()
        form_link = self.get_add_plan_link(form_kwargs=form_kwargs, use_request_url=True)
        response_link = form_link.submit()
        return self.generate_response(response_link)
    
    post = put

class RemovePlanMixin(DocumentDetailMixin):
    def get_remove_plan_link(self, form_kwargs=None, **link_kwargs):
        item = self.get_item()
        if form_kwargs is None: form_kwargs = dict()
        form_kwargs = self.get_form_kwargs(**form_kwargs)
        link_kwargs.update({'form_kwargs': form_kwargs,
                            'item':item})
        link_kwargs = self.get_link_kwargs(**link_kwargs)
        return self.resource.get_remove_plan_link(**link_kwargs)

class RemovePlanView(RemovePlanMixin, CRUDView):
    view_class = 'change_form'
    
    def get(self, request, *args, **kwargs):
        return self.generate_response(self.get_remove_plan_link(use_request_url=True))
    
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.can_change(self.object):
            return http.HttpResponseForbidden(_(u"You may not modify that object"))
        
        form_kwargs = self.get_request_form_kwargs()
        form_link = self.get_remove_plan_link(form_kwargs=form_kwargs, use_request_url=True)
        response_link = form_link.submit()
        return self.generate_response(response_link)
    
    post = put

