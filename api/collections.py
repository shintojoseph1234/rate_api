
from mongoengine import *



class Upload(Document):

    date_from           = StringField(required=True)
    date_to             = StringField(required=True)
    origin_code         = FloatField(required=True)
    destination_code    = FloatField(required=True)
    price               = FloatField(required=True)
