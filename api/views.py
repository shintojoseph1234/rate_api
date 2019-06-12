# Django imports
from django.conf import settings
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# REST imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView

# local imports
from api.serializers import *
from .models import Ports, Prices, Regions

# other imports
import os
import csv
import json
import datetime
import pandas as pd

# MongoDB imports
from pymongo import MongoClient


################################## configuration file
# open configuration file
config_file = open(settings.CONFIGURATION_FILE)
# get the configuration data from the file
config_data = json.load(config_file)
# close the config file
config_file.close()

# Configuration of Django mongodb
mongodb_host        = config_data['mongodb']['host']
mongodb_port        = config_data['mongodb']['port']
mongodb_database    = config_data['mongodb']['database']
mongodb_collection  = config_data['mongodb']['collection']


################################# MongoDB connections
# Connecting to mongodb
client = MongoClient(host = mongodb_host, port = mongodb_port)
# database
db = client[mongodb_database]
# collection
collection = db[mongodb_collection]



def get_error_message(error_type, message):

    if error_type == "DATA_ERROR":

        error_status = [{
                        "status": "error",
                        "data": {
                            "http_code": "400 BAD REQUEST",
                            "errors": [{
                                "error_code": 2000,  # FIXME: Suboptimal error format
                                "error_message": message
                                }]
                            }
                        }]
        return Response(error_status, status=status.HTTP_400_BAD_REQUEST)

    elif error_type == "KEY_ERROR":

        error_status = [{
                        "status": "error",
                        "data": {
                                "http_code": "400 BAD REQUEST",
                                "errors": [{
                                            "error_code": 2001,
                                            "error_message": "Key 'request' not found"
                                            }]
                                }
                        }]
        return Response(error_status, status=status.HTTP_400_BAD_REQUEST)

    elif error_type == "SERVER_ERROR":

        error_status = [{
                        "status": "error",
                        "data": {
                            "http_code": "500 INTERNAL SERVER ERROR",
                            "errors": [{
                                "error_code": 2002,
                                "error_message": "Internal server error"
                                }]
                            }
                        }]
        return Response(error_status, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    else:
        error_status = [{
            "status": "error",
            "data": {
                "http_code": "500 INTERNAL SERVER ERROR",
                "errors": [{
                    "error_code": 2003,
                    "error_message": "Unknown Internal server error"
                    }]
                }
            }]

    return Response(error_status, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def slug_to_code(slug):
    # if slug present in parent_slug column enter
    if Ports.objects.filter(parent_slug=slug).exists():
        # filter out the code list for corresponding slug
        code_list = list(Ports.objects.filter(parent_slug=slug).values_list("code", flat=True))
    else:
        # convert slug to a list
        code_list = [slug]

    return code_list


def db_connection():
    # from django.db import connection
    # cursor = connection.cursor()
    # ss = cursor.execute('''SELECT count(*) FROM api_prices''')
    # print (ss)
    # print ( Prices.objects.all().count())
    pass

@api_view(['GET'])
def rates(request, date_from, date_to, origin, destination):
    '''
    curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates/2016-01-01/2016-01-01/CNSGH/north_europe_main/
    '''

    # obtain corresponding code for slugs
    origin      = slug_to_code(slug=origin)
    destination = slug_to_code(slug=destination)

    # Query the model
    filtered_queryset = Prices.objects.filter(
                                        day__range=[date_from, date_to],
                                        orig_code__in=origin,
                                        dest_code__in=destination
                                        )

    if filtered_queryset:
        # retrieving from database and converting into dataframe
        # df = pd.DataFrame(list(filtered_queryset.values('day', 'price')))
        df = pd.DataFrame(list(filtered_queryset.values('day', 'price', 'orig_code', 'dest_code')))
        # find average of same day and convert into integer
        mean_df = df.groupby(df['day']).mean().astype(int)
        # reset index and convert index into column
        mean_df.reset_index(level=0, inplace=True)
        # rename column
        mean_df = mean_df.rename(columns={'price': 'average_price'})
        # convert date to string
        mean_df["day"] = mean_df["day"].astype(str)
        # convert result into list of dictionary
        result_dict = mean_df.to_dict(orient='records')
    else:
        result_dict = []

    success = [{
                "status": "success",
                "data": result_dict
                }]


    return Response(success, status=status.HTTP_200_OK)



@api_view(['GET'])
def rates_null(request, date_from, date_to, origin, destination):
    '''
    curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates_null/2016-01-01/2016-01-01/CNSGH/north_europe_main/
    '''

    # obtain corresponding code for slugs
    origin      = slug_to_code(slug=origin)
    destination = slug_to_code(slug=destination)

    # Query the model
    filtered_queryset = Prices.objects.filter(
                                        day__range=[date_from, date_to],
                                        orig_code__in=origin,
                                        dest_code__in=destination
                                        )
    if filtered_queryset:
        # retrieving from database and converting into dataframe
        df = pd.DataFrame(list(filtered_queryset.values('day', 'price'))).set_index('day')
        # find average of same day and convert into integer
        mean_df = df.groupby(df.index).mean().astype(int)
        # find day in number less than 3
        bool_df = df.groupby('day').count() < 3
        # replace above days value by null
        mean_df[bool_df['price']] = "null"
        # reset index and convert index into column
        mean_df.reset_index(level=0, inplace=True)
        # rename column
        mean_df = mean_df.rename(columns={'price': 'average_price'})
        # convert date to string
        mean_df["day"] = mean_df["day"].astype(str)
        # convert result into list of dictionary
        result_dict = mean_df.to_dict(orient='records')
    else:
        result_dict = []

    success = [{
                "status": "success",
                "data": result_dict
                }]

    return Response(success, status=status.HTTP_200_OK)


################## POST API

class UploadViewSet(GenericAPIView):
    # """
    # # TODO: include docs here
    # """
    queryset = ''
    serializer_class = UploadPricesSerializer

    def post(self, request, *args, **kwargs):

        # obtain the data
        data = request.data
        # check data with serializer
        serializer = UploadPricesSerializer(data=data)
        # if serialiser not valid
        if not serializer.is_valid():
            # return error message
            return get_error_message("DATA_ERROR", str(serializer.errors))

        # inputs from API
        price               = data['price']
        date_to             = data['date_to']
        date_from           = data['date_from']
        origin_code         = data['origin_code']
        destination_code    = data['destination_code']

        # if date length does not match
        if date_from != date_to:
            # generate a list of dates
            date_range = pd.date_range(start=date_from, end=date_to).date.tolist()

        # if generated date length and price doesnt match
        if len(date_range) != len(price):
            # return error response
            return get_error_message("DATA_ERROR", "price and generated date length does not match")

        try:
            # obtain each date and price in list
            for date, price in zip(date_range, price):
                # update if not in model else create new
                prices_obj, created = Prices.objects.update_or_create(
                                                                    orig_code   = origin_code,
                                                                    dest_code   = destination_code,
                                                                    day         = date,
                                                                    defaults={'price': price},
                                                                    )
            # response messages
            saved_status = True
            message = "Data successfully ingested"
            status_code = status.HTTP_201_CREATED

        except:
            # response messages
            saved_status = True
            message = "Failed to ingest data"
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        # response
        success = [{
                    "status": saved_status,
                    "data": {
                            "message": message
                            }
                   }]

        return Response(success, status=status_code)
