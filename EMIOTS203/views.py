from django.shortcuts import render

from .models import Tweet


# Create your views here.
def list_view(request):
    qs = Tweet.objects.filter(stockchart__isnull=False)
    template_name = 'EMIOTS203/list.html'
    context = {"tweet_list": qs}
    return render(request, template_name, context)
