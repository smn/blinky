from django.views.generic import ListView

from .models import WorkerType, WorkerInstance, HeartBeat


class WorkerTypeList(ListView):
    model = WorkerType


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
