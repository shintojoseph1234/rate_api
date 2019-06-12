# django imports
from django.contrib.auth.models import User
from rest_framework import serializers

# local imports
from api.collections import *

# mongoengine imports
from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer

#### Upload API serializer
class UploadSerializer(DocumentSerializer):

    class Meta:
        model = Upload
        fields = '__all__'
        depth = 2
