from django.utils import timezone


def year(request):
    now = timezone.now()
    year = now.strftime('%Y')
    return {
        'year': year,
    }
