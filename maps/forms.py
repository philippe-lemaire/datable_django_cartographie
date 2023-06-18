from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransportationModesForm(forms.Form):
    own_bike_used = forms.BooleanField(
        label="🚲 J’utilise mon vélo (aménagement cyclables + stationnement cyclable)",
        required=False,
    )
    velov_used = forms.BooleanField(
        label="🚲 J’utilise les Vélov’ (aménagement cyclables + stations Vélov’)",
        required=False,
    )
    trains_used = forms.BooleanField(
        label="🚂 Je prends le train (emplacement des gares)",
        required=False,
    )
    cars_used = forms.BooleanField(
        label="🚗 Je prends une voiture (stations autopartages, parkings et parcs relais)",
        required=False,
    )
    taxis_used = forms.BooleanField(
        label="🚕 Je prends le taxi (emplacement des stations de taxis)",
        required=False,
    )
    pmr_used = forms.BooleanField(
        label="👩‍🦽 J’utilise les emplacements de stationnements PMR",
        required=False,
    )
    rhone_buses_used = forms.BooleanField(
        label="🚍 J’utilise les cars du département du Rhône",
        required=False,
    )
    public_transports_used = forms.BooleanField(
        label="🚇 J’utilise les transports en commun TCL (métro, bus, tramway)",
        required=False,
    )
    river_boat_used = forms.BooleanField(
        label="🛥️ J’utilise la navette fluviale (emplacement des stations)",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_id = "id-exampleForm"
        # self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "display_map"
        self.helper.add_input(Submit("submit", "Voir ma carte"))
