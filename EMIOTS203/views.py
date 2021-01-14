from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Tweet
from .forms import SwingChoiceField

# Create your views here.


def tweetsChartsView(request):
    qs = Tweet.objects.filter(stockchart__isnull=False)
    template_name = 'EMIOTS203/list.html'

    form = SwingChoiceField(request.POST or None)

    if request.method == 'POST':
        if(form.is_valid()):
            selectedSwing = form['swingValues'].value()
            qs = qs.filter(stockchart__maxSwing__gte=selectedSwing)

    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {"page_obj": page_obj,
               "form": form}
    return render(request, template_name, context)
