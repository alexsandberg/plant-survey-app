from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField
from wtforms.validators import DataRequired, URL


# class ShowForm(Form):
#     artist_id = StringField(
#         'artist_id'
#     )
#     venue_id = StringField(
#         'venue_id'
#     )
#     start_time = DateTimeField(
#         'start_time',
#         validators=[DataRequired()],
#         default=datetime.today()
#     )


# class VenueForm(Form):
#     name = StringField(
#         'name', validators=[DataRequired()]
#     )
#     city = StringField(
#         'city', validators=[DataRequired()]
#     )
#     state = SelectField(
#         'state', validators=[DataRequired()],
#         choices=[
#             ('AL', 'AL'),
#             ('AK', 'AK'),
#             ('AZ', 'AZ'),
#             ('AR', 'AR'),
#             ('CA', 'CA'),
#             ('CO', 'CO'),
#             ('CT', 'CT'),
#             ('DE', 'DE'),
#             ('DC', 'DC'),
#             ('FL', 'FL'),
#             ('GA', 'GA'),
#             ('HI', 'HI'),
#             ('ID', 'ID'),
#             ('IL', 'IL'),
#             ('IN', 'IN'),
#             ('IA', 'IA'),
#             ('KS', 'KS'),
#             ('KY', 'KY'),
#             ('LA', 'LA'),
#             ('MA', 'MA'),
#             ('MD', 'MD'),
#             ('ME', 'ME'),
#             ('MI', 'MI'),
#             ('MN', 'MN'),
#             ('MO', 'MO'),
#             ('MS', 'MS'),
#             ('MT', 'MT'),
#             ('NE', 'NE'),
#             ('NV', 'NV'),
#             ('NH', 'NH'),
#             ('NJ', 'NJ'),
#             ('NM', 'NM'),
#             ('NY', 'NY'),
#             ('NC', 'NC'),
#             ('ND', 'ND'),
#             ('OH', 'OH'),
#             ('OK', 'OK'),
#             ('OR', 'OR'),
#             ('PA', 'PA'),
#             ('RI', 'RI'),
#             ('SC', 'SC'),
#             ('SD', 'SD'),
#             ('TN', 'TN'),
#             ('TX', 'TX'),
#             ('UT', 'UT'),
#             ('VT', 'VT'),
#             ('VA', 'VA'),
#             ('WA', 'WA'),
#             ('WV', 'WV'),
#             ('WI', 'WI'),
#             ('WY', 'WY'),
#         ]
#     )
#     address = StringField(
#         'address', validators=[DataRequired()]
#     )
#     phone = StringField(
#         'phone', validators=[DataRequired()]
#     )
#     image_link = StringField(
#         'image_link'
#     )
#     genres = SelectMultipleField(
#         'genres', validators=[DataRequired()],
#         choices=[
#             ('Alternative', 'Alternative'),
#             ('Blues', 'Blues'),
#             ('Classical', 'Classical'),
#             ('Country', 'Country'),
#             ('Electronic', 'Electronic'),
#             ('Folk', 'Folk'),
#             ('Funk', 'Funk'),
#             ('Hip-Hop', 'Hip-Hop'),
#             ('Heavy Metal', 'Heavy Metal'),
#             ('Instrumental', 'Instrumental'),
#             ('Jazz', 'Jazz'),
#             ('Musical Theatre', 'Musical Theatre'),
#             ('Pop', 'Pop'),
#             ('Punk', 'Punk'),
#             ('R&B', 'R&B'),
#             ('Reggae', 'Reggae'),
#             ('Rock n Roll', 'Rock n Roll'),
#             ('Soul', 'Soul'),
#             ('Other', 'Other'),
#         ]
#     )
#     facebook_link = StringField(
#         'facebook_link', validators=[URL()]
#     )
#     website = StringField(
#         'website', validators=[URL()]
#     )
#     seeking_talent = SelectField(
#         'seeking_talent', validators=[DataRequired()],
#         choices=[
#             ('Yes', 'Yes'),
#             ('No', 'No')
#         ]
#     )
#     seeking_description = StringField(
#         'seeking_description'
#     )


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
