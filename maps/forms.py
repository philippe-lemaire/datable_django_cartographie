from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransportationModesForm(forms.Form):
    velov_used = forms.BooleanField(
        label="Stations vélov",
        required=False,
    )
    trains_used = forms.BooleanField(
        label="Gares ferroviaires",
        required=False,
    )
    cars_used = forms.BooleanField(
        label="Voitures, autopartage et stationnement",
        required=False,
    )
    rhone_buses_used = forms.BooleanField(
        label="Cars du Rhône",
        required=False,
    )
    subway_used = forms.BooleanField(
        label="Métro",
        required=False,
    )

    stop_points_used = forms.BooleanField(
        label="Points d’arrêt Transports en commun",
        required=False,
    )
    taxis_used = forms.BooleanField(
        label="Stations de taxis",
        required=False,
    )
    river_boat_used = forms.BooleanField(
        label="Stations navette fluviale",
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
