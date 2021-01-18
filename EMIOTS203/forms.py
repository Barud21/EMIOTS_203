from django import forms
from django.db.models import Max

from .models import StockChart
from .widgets import FengyuanChenDatePickerInput


class FilteringForm(forms.Form):

    maxOfMaxSwing = StockChart.objects.aggregate(Max('maxSwing'))['maxSwing__max']
    swingChoicesList = [(x, x) for x in range(1, int(maxOfMaxSwing)+1)]
    swingChoicesList.insert(0, ('', '----'))
    swingValues = forms.ChoiceField(choices=swingChoicesList,
                                    label='Stock change greater than X percent:',
                                    required=False)

    startDate = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=FengyuanChenDatePickerInput(),
        label='From date:',
        required=False
    )

    # TODO: Create a custom date picker field to avoid copy pasting
    endDate = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=FengyuanChenDatePickerInput(),
        label='To date:',
        required=False
    )
