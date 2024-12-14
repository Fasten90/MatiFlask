from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired


class MatiAdatbazisFeltoltes(FlaskForm):
    # Result not needed to here

    def __init__(self, default_values):
        super().__init__()

        self.jarat = StringField('Járat (szám)', default_values['line'], validators=[DataRequired()])
        self.min_hour = IntegerField('min_hour', default_values['min_hour'], validators=[DataRequired()])
        self.max_hour = IntegerField('max_hour',  default_values['max_hour'], validators=[DataRequired()])
        self.jaratsuruseg_minute = IntegerField('Járatsűrűség hétköznap',  default_values['jaratsuruseg_minute'], validators=[DataRequired()])
        self.start_minute = IntegerField('Indulási időpont',  default_values['start_minute'], validators=[DataRequired()])
        self.station = StringField('Megálló (station)',  default_values['station'], validators=[DataRequired()])
        self.jarat_tipus = SelectField('Járat típus',  default_values['line_type'], choices=['VCAF', 'VCOM', 'VGANZ', 'VTATRA', 'M', 'H', 'BUSZ', 'BUSZTROLI', 'ÉJSZAKAI', 'VOLÁNBUSZ', 'DHAJO', 'VONAT'])
        self.jaratsuruseg_hetvege = IntegerField('Járatsűrűség hétvégén',  default_values['jaratsuruseg_hetvege'])
        #varos - not used, use de default
        self.low_floor = StringField('Alacsonypadlós: (alacsonypadlósok száma/magas padlósok száma arányban kell beírni, pl. "2_1")',  default_values['low_floor'])
        self.is_edit = default_values['is_edit']
