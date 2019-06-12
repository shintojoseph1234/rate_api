# Django imports
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
import csv
import os
import datetime
import pandas as pd


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

    date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()


    origin      = slug_to_code(slug=origin)
    destination = slug_to_code(slug=destination)


    filtered_queryset = Prices.objects.filter(
                                        day__range=[date_from, date_to],
                                        orig_code__in=origin,
                                        dest_code__in=destination
                                        )

    # retrieving from database and converting into dataframe
    df = pd.DataFrame(list(filtered_queryset.values('day', 'price')))
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

    success = [{
                "status": "success",
                "data": result_dict
                }]


    return Response(success, status=status.HTTP_200_OK)



@api_view(['GET'])
def rates_null(request, date_from, date_to, origin, destination):

    date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()

    origin      = slug_to_code(slug=origin)
    destination = slug_to_code(slug=destination)


    filtered_queryset = Prices.objects.values_list('day','price').filter(
                                        day__range=[date_from, date_to],
                                        orig_code__in=origin,
                                        dest_code__in=destination
                                        )

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
    serializer_class = UploadSerializer

    def post(self, request, *args, **kwargs):

        if 'request' not in request.data:
            # if key request not found return error message
            return get_error_message("KEY_ERROR", "Key 'request' not found")

        if not serializer.is_valid():
            # if serialiser not valid return error message
            return get_error_message("DATA_ERROR", str(serializer.errors))

        serializer = UploadSerializer(data=data)
        data = request.data['request']

        # success response to be displayed
        success = [{
                    "status": "success",
                    "data": {
                            "State": "Successfully initiated"
                            }
                   }]

        return Response(success, status=status.HTTP_200_OK)


        # try:
        #
        #     t = threading.Thread(target=fire_API, args=[data])
        #     # Daemon mode,the thread will stop after complete
        #     t.setDaemon(True)
        #     t.start()
        #
        #     # fire_API(data)
        #
        #
        #     # success response to be displayed
        #     success = [{
        #                 "status": "success",
        #                 "data": {
        #                         "State": "Successfully initiated"
        #                         }
        #                }]
        #
        #     return Response(success, status=status.HTTP_200_OK)
        # except Exception as ex:
        #     # raise ex
        #     # TODO: Log this exception
        #     return get_error_message(DATA_ERROR, "You may have not done the Risk Questionnaire/Unsatisfied constraints")
