from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, next_page):
    query = context['request'].GET.copy().urlencode()

    # if there is only a 'page' param or there are no params at all
    if (len(context['request'].GET.copy()) == 1 and 'page=' in query) or len(context['request'].GET.copy()) == 0:
        return f'page={next_page}'

    # if 'page' param is one of many params
    if '&page=' in query:
        url = query.rpartition('&page=')[0]
    else:
        url = query

    return f'{url}&page={next_page}'
