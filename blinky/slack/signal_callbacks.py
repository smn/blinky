def on_worker_online(sender, worker_type, **kwargs):
    print 'worker %s came online!' % (worker_type,)


def on_worker_offline(sender, worker_type, **kwargs):
    print 'worker %s went offline!' % (worker_type,)


def on_worker_capacity_change(sender, worker_type, **kwargs):
    print 'capacity for %s changed' % (worker_type,)
