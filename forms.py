from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField
from wtforms.validators import DataRequired, URL


class PlantForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    latin_name = StringField(
        'latin_name', validators=[DataRequired()]
    )
    description = StringField(
        'description', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )


class ObservationForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    date = DateTimeField(
        'date',
        validators=[DataRequired()],
        default=datetime.now()
    )
    plant_id = StringField(
        'plant_id', validators=[DataRequired()]
    )
    notes = StringField('notes')
