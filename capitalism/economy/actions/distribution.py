from ..helpers import get_economy_view_context
from django.http import HttpResponse
from django.template import loader
def revenue(request):
    template = loader.get_template('economy/economy.html')
    context = get_economy_view_context({})
    return HttpResponse(template.render(context, request))

def accumulate(request):
    template = loader.get_template('economy/economy.html')
    context = get_economy_view_context({})
    return HttpResponse(template.render(context, request))

  