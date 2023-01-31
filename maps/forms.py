from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransportationModesForm(forms.Form):
    velov_used = forms.BooleanField(
        label="Utilisez-vous les vélov’ ?",
        required=False,
    )
    trains_used = forms.BooleanField(
        label="On garde les trains ?",
        required=False,
    )
    cars_used = forms.BooleanField(
        label="On utilise les infos stationnement ?",
        required=False,
    )
    rhone_buses_used = forms.BooleanField(
        label="On utilise les cars du Rhône ?",
        required=False,
    )
    subway_used = forms.BooleanField(
        label="On utilise le métro ?",
        required=False,
    )

    stop_points_used = forms.BooleanField(
        label="On garde les points d'arrêt ?",
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
