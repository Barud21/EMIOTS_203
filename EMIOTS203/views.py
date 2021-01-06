from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Tweet

# Create your views here.


def tweetsChartsView(request):
    qs = Tweet.objects.filter(stockchart__isnull=False)
    template_name = 'EMIOTS203/list.html'
    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {"page_obj": page_obj}
    return render(request, template_name, context)
