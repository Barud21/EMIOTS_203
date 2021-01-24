from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from urllib.parse import urlencode
import datetime

from .models import Tweet
from .forms import FilteringForm

# Create your views here.


def createDictWithPostParams(request):
    params = {}

    selectedSwing = request.POST.get('swingValue', '')
    if selectedSwing != '':
        params['swingValue'] = selectedSwing

    startDate = request.POST.get('startDate', '')
    if startDate != '':
        params['startDate'] = startDate

    endDate = request.POST.get('endDate', '')
    if endDate != '':
        params['endDate'] = endDate

    return params


# main view that list pairs of tweet and stockchart
def tweetsChartsView(request):
    template_name = 'EMIOTS203/list.html'

    form = FilteringForm(request.POST or None)

    if request.method == 'POST':
        if(form.is_valid()):
            params = createDictWithPostParams(request)

            base_url = reverse(tweetsChartsView)
            queryString = urlencode(params)

            if len(queryString) > 0:
                url = '{}?{}'.format(base_url, queryString)
            else:
                url = base_url

            return redirect(url)

    qs = Tweet.objects.filter(stockchart__isnull=False)

    # TODO: Maybe some refactor in this part?
    getSelectedSwing = request.GET.get('swingValue', '')
    if getSelectedSwing != '':
        try:
            qs = qs.filter(stockchart__maxSwing__gte=int(getSelectedSwing))
        except ValueError:
            pass
        else:
            form.fields['swingValue'].initial = getSelectedSwing

    getSelectedStartDate = request.GET.get('startDate', '')
    if getSelectedStartDate != '':
        try:
            dateTimeStartDate = datetime.datetime.strptime(getSelectedStartDate, '%d/%m/%Y')
            dateTimeStartDate = dateTimeStartDate.replace(hour=0, minute=0, second=0, tzinfo=datetime.timezone.utc)
            qs = qs.filter(date__gte=dateTimeStartDate)
        except ValueError:
            pass
        else:
            form.fields['startDate'].initial = getSelectedStartDate

    getSelectedEndDate = request.GET.get('endDate', '')
    if getSelectedEndDate != '':
        try:
            dateTimeEndDate = datetime.datetime.strptime(getSelectedEndDate, '%d/%m/%Y')
            dateTimeEndDate = dateTimeEndDate.replace(hour=23, minute=59, second=59, tzinfo=datetime.timezone.utc)
            qs = qs.filter(date__lte=dateTimeEndDate)
        except ValueError:
            pass
        else:
            form.fields['endDate'].initial = getSelectedEndDate

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
