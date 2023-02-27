from django.shortcuts import render
from .gen_maps import gen_maps, MAP_PATH
from django.views.generic import TemplateView
from .forms import TransportationModesForm

# Create your views here.


class IndexView(TemplateView):
    template_name = "maps/index.html"


def display_map(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = TransportationModesForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # retrieve the values from the form
            own_bike_used = form.cleaned_data["own_bike_used"]
            velov_used = form.cleaned_data["velov_used"]
            trains_used = form.cleaned_data["trains_used"]
            cars_used = form.cleaned_data["cars_used"]
            rhone_buses_used = form.cleaned_data["rhone_buses_used"]
            public_transports_used = form.cleaned_data["public_transports_used"]
            taxis_used = form.cleaned_data["taxis_used"]
            river_boat_used = form.cleaned_data["river_boat_used"]
            pmr_used = form.cleaned_data["pmr_used"]

            m = gen_maps(
                own_bike_used=own_bike_used,
                velov_used=velov_used,
                trains_used=trains_used,
                cars_used=cars_used,
                rhone_buses_used=rhone_buses_used,
                public_transports_used=public_transports_used,
                taxis_used=taxis_used,
                river_boat_used=river_boat_used,
                pmr_used=pmr_used,
            )

            # return render(request, "maps/display_map.html", context={'map': m._repr_html_()})
            return render(request, "maps/full_map.html")

    # if a GET (or any other method) we'll create a blank form
    else:
        context = {"form": TransportationModesForm()}
        return render(request, "maps/form_before_map.html", context)
