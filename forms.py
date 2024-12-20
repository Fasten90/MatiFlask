""" Forms for MatiFlask - MatiGO database uploading """

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField
# TextAreaField, SubmitField, PasswordField,
from wtforms.validators import DataRequired


class MatiAdatbazisFeltoltes(FlaskForm):
    """ MatiFlask - MatiGo - upload form """
    # Result not needed to here
    jarat = StringField('Járat (szám)', validators=[DataRequired()])
    min_hour = IntegerField('min_hour', validators=[DataRequired()])
    max_hour = IntegerField('max_hour', validators=[DataRequired()])
    jaratsuruseg_minute = IntegerField('Járatsűrűség hétköznap', validators=[DataRequired()])
    start_minute = IntegerField('Indulási időpont', validators=[DataRequired()])
    station = StringField('Megálló (station)', validators=[DataRequired()])
    jarat_tipus = SelectField('Járat típus',
        choices=['VCAF', 'VCOM', 'VGANZ', 'VTATRA',
                 'M', 'H', 'BUSZ', 'BUSZTROLI', 'ÉJSZAKAI',
                 'VOLÁNBUSZ', 'DHAJO', 'VONAT'])
    jaratsuruseg_hetvege = IntegerField('Járatsűrűség hétvégén', default=0)
    #varos - not used, use de default
    low_floor = StringField('Alacsonypadlós: (alacsonypadlósok száma/magas padlósok száma arányban kell beírni, pl. "2_1")')  # pylint: disable=line-too-long
    is_edit = BooleanField('is_edit', default=False)
