from celery.task import task

from hostingservices.services.models import ServicePlanRequest


@task(ignore_result=True)
def process_service_plan_request(pk):
    request = ServicePlanRequest.objects.get(pk=pk)
    request.execute_request()
