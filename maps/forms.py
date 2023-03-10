from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransportationModesForm(forms.Form):
    own_bike_used = forms.BooleanField(
        label="Vous utilisez votre vélo",
        required=False,
    )
    velov_used = forms.BooleanField(
        label="Vous utilisez le service Vélov’",
        required=False,
    )
    trains_used = forms.BooleanField(
        label="Gares ferroviaires",
        required=False,
    )
    cars_used = forms.BooleanField(
        label="Voitures, autopartage et stationnement auto",
        required=False,
    )
    pmr_used = forms.BooleanField(
        label="Stationnements Personnes à Mobilité Réduite",
        required=False,
    )
    rhone_buses_used = forms.BooleanField(
        label="Cars du Rhône",
        required=False,
    )
    public_transports_used = forms.BooleanField(
        label="Transports en commun (métro, bus, tramway)",
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
