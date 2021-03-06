from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from django.views.generic import ListView

from .models import WorkerType, WorkerInstance, HeartBeat


class BlinkyHealth(View):

    def get(self, request):
        from .tasks import health_check
        result = health_check.apply_async()
        result.get(timeout=float(request.GET.get('timeout', 5)))
        return HttpResponse('ok')


class WorkerTypeHealth(View):

    model = WorkerType

    def get(self, request, workertype_pk):
        try:
            workertype = self.model.objects.get(pk=workertype_pk)
            if workertype.is_online():
                return HttpResponse('ok')
            return HttpResponseNotFound('not ok')
        except self.model.DoesNotExist:
            return HttpResponseNotFound('not ok')


class WorkerTypeList(ListView):
    model = WorkerType
    ordering = ('worker_friendly_name', 'worker_name')


class WorkerInstanceList(ListView):
    model = WorkerInstance
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super(WorkerInstanceList, self).get_queryset()
        return queryset.filter(worker_type=self.kwargs['workertype_pk'])

    def get_context_data(self, **kwargs):
        context = super(WorkerInstanceList, self).get_context_data(
            **kwargs)
        context['workertype'] = WorkerType.objects.get(
            pk=self.kwargs['workertype_pk'])
        return context


class HeartBeatList(ListView):
    model = HeartBeat
    ordering = '-created_at'
    paginate_by = 30

    def get_queryset(self):
        queryset = super(HeartBeatList, self).get_queryset()
        workertype = WorkerType.objects.get(pk=self.kwargs['workertype_pk'])
        workerinstance = workertype.workerinstance_set.get(
            pk=self.kwargs['workerinstance_pk'])
        return queryset.filter(worker_type=workertype,
                               worker_instance=workerinstance)

    def get_context_data(self, **kwargs):
        context = super(HeartBeatList, self).get_context_data(
            **kwargs)
        workertype = WorkerType.objects.get(pk=self.kwargs['workertype_pk'])
        context['workertype'] = workertype
        context['workerinstance'] = workertype.workerinstance_set.get(
            pk=self.kwargs['workerinstance_pk'])
        return context
