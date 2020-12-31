from django.views.generic import ListView

from .models import Tweet


# Create your views here.

class TweetListView(ListView):
    queryset = Tweet.objects.filter(stockchart__isnull=False)
    context_object_name = 'tweets'
    paginate_by = 5
    template_name = 'EMIOTS203/list.html'
