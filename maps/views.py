from django.shortcuts import render
from .gen_maps import gen_maps, MAP_PATH
from django.views.generic import TemplateView

# Create your views here.


class IndexView(TemplateView):
    template_name = "maps/index.html"


def display_map(request):
    gen_maps()
    return render(request, "maps/full_map.html")
