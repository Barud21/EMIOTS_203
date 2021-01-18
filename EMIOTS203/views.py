from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime

from .models import Tweet
from .forms import FilteringForm

# Create your views here.


def tweetsChartsView(request):
    qs = Tweet.objects.filter(stockchart__isnull=False)
    template_name = 'EMIOTS203/list.html'

    form = FilteringForm(request.POST or None)

    if request.method == 'POST':
        if(form.is_valid()):
            if form['swingValues'].value() != '':
                selectedSwing = form['swingValues'].value()
                qs = qs.filter(stockchart__maxSwing__gte=selectedSwing)

            if form['startDate'].value() != '':
                startDate = form['startDate'].value()
                dateTimeStartDate = datetime.datetime.strptime(startDate, '%d/%m/%Y')
                dateTimeStartDate = dateTimeStartDate.replace(hour=0, minute=0, second=0, tzinfo=datetime.timezone.utc)

                qs = qs.filter(date__gte=dateTimeStartDate)

            # TODO: Think of clever way to handle these 2 datetime values processing
            if form['endDate'].value() != '':
                endDate = form['endDate'].value()
                dateTimeEndDate = datetime.datetime.strptime(endDate, '%d/%m/%Y')
                dateTimeEndDate = dateTimeEndDate.replace(hour=23, minute=59, second=59, tzinfo=datetime.timezone.utc)

                qs = qs.filter(date__lte=dateTimeEndDate)

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
