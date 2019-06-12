# django imports
from rest_framework import serializers



class UploadPricesSerializer(serializers.Serializer):

    origin_code         = serializers.CharField(max_length=200)
    destination_code    = serializers.CharField(max_length=200)
    date_from           = serializers.DateField()
    date_to             = serializers.DateField()
    price               = serializers.ListField(child=serializers.IntegerField(required=False))


    def validate(self, data):
        """
        Check that date_from is less than date_to
        """

        if data['date_from'] > data['date_to']:
            raise serializers.ValidationError("date_from must be less than or equal to date_to")

        return data



class UploadUsdPricesSerializer(serializers.Serializer):

    origin_code         = serializers.CharField(max_length=200)
    destination_code    = serializers.CharField(max_length=200)
    date_from           = serializers.DateField()
    date_to             = serializers.DateField()
    price               = serializers.ListField(child=serializers.IntegerField(required=False))
    currency_code       = serializers.CharField(max_length=200)


    def validate(self, data):
        """
        Check that date_from is less than date_to
        """

        if data['date_from'] > data['date_to']:
            raise serializers.ValidationError("date_from must be less than or equal to date_to")

        return data
