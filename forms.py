from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField
# TextAreaField, SubmitField, PasswordField,
from wtforms.validators import DataRequired


class MatiAdatbazisFeltoltes(FlaskForm):
    # Result not needed to here
    jarat = StringField('Járat (szám)', validators=[DataRequired()])
    min_hour = IntegerField('min_hour', validators=[DataRequired()])
    max_hour = IntegerField('max_hour', validators=[DataRequired()])
    jaratsuruseg_minute = IntegerField('Járatsűrűség hétköznap', validators=[DataRequired()])
    start_minute = IntegerField('Indulási időpont', validators=[DataRequired()])
    station = StringField('Megálló (station)', validators=[DataRequired()])
    jarat_tipus = SelectField('Járat típus', choices=['VCAF', 'VCOM', 'VGANZ', 'VTATRA', 'M', 'H', 'BUSZ', 'BUSZTROLI', 'ÉJSZAKAI', 'VOLÁNBUSZ', 'DHAJO', 'VONAT'])
    jaratsuruseg_hetvege = IntegerField('Járatsűrűség hétvégén', default=0)
    #varos - not used, use de default
    low_floor = StringField('Alacsonypadlós: (alacsonypadlósok száma/magas padlósok száma arányban kell beírni, pl. "2_1")')
    is_edit = BooleanField('is_edit', default=False)

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
        self.is_edit = BooleanField('is_edit', default=default_values['is_edit'])

