from django import forms
from django.db.models import Max

from .models import StockChart
from .widgets import FengyuanChenDatePickerInput


class SwingChoiceField(forms.Form):

    maxValue = StockChart.objects.aggregate(Max('maxSwing'))['maxSwing__max']
    swingValues = forms.ChoiceField(choices=[(x, x) for x in range(1, int(maxValue)+1)])

    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'], 
        widget=FengyuanChenDatePickerInput()
    )
