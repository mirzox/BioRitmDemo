from .models import PId


def my_cron_job():
    if not PId.objects.all().count():
        PId.objects.create(p_id=1)
    PId.objects.filter(pk=1).update(p_id=1)



