# Django imports
from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# REST imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView

# local imports
from api.serializers import *
from api.models import Ports, Prices, Regions

# other imports
import os
import json
import requests
import datetime
import pandas as pd


################################## configuration file
# open configuration file
config_file = open(settings.CONFIGURATION_FILE)
# get the configuration data from the file
config_data = json.load(config_file)
# close the config file
config_file.close()

# Configuration of exchange rate API
exchange_rates_url  = config_data['exchange_rates']['url']
exchange_app_id     = config_data['exchange_rates']['app_id']


def get_error_message(error_type, message):
    '''
    Checks the error type and message,
    and returns error message with error code

    Parameters:
        error_type (str)    : The error type.
        message (dict)      : The response message from serializer.

    Returns:
        list: returns error message with error code
    '''

    if error_type == "DATA_ERROR":

        error_status = [{
                        "status": "error",
                        "data": {
                            "http_code": "400 BAD REQUEST",
                            "errors": [{
                                "error_code": 2000,
                                "error_message": message
                                }]
                            }
                        }]
        return Response(error_status, status=status.HTTP_400_BAD_REQUEST)

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
    '''
    Takes slug as input and
    finds code from the database

    Parameters:
        slug (str)  : The slug.

    Returns:
        list: returns list of codes

    '''

    # if slug present in parent_slug column enter
    if Ports.objects.filter(parent_slug=slug).exists():
        # filter out the code list for corresponding slug
        code_list = list(Ports.objects.filter(parent_slug=slug).values_list("code", flat=True))
    else:
        # convert slug to a list
        code_list = [slug]

    return code_list

def db_query(sql_query, input):
    '''
    Takes the sql_query and the inputs,
    and query the database

    Parameters:
        sql_query (str) : The sql_query.
        input (tuple)   : The inputs for the sql_query.

    Returns:
        list: returns list of dictionary with columns as keys
    '''
    # connecting to database
    with connection.cursor() as cursor:
        # execute query along with inputs
        cursor.execute(sql_query, input)
        # make cursor response data into list of dictionaries
        query_data = cursor_fetch_all(cursor)

    return query_data

def cursor_fetch_all(cursor):
    '''
    Takes cursor object as input and
     combines the rows and columns into list of dictionary

    Parameters:
        cursor (object) : The cursor object.

    Returns:
        list: returns list of dictionary with columns as keys
            and rows as values
    '''

    # obtain the column names
    column_names = [col[0] for col in cursor.description]
    # initialize empty list
    result_list = list()
    # for each rows in response data
    for row in cursor.fetchall():
        # convert into
        result_dict = dict(zip(column_names, row))
        # append to result_list
        result_list.append(result_dict)

    return result_list

def exchange_rates(amount, currency_code):
    '''
    Convert amount into USD

    Parameters:
        amount (int)        : The amount to convert.
        currency_code (str) : The currency of the input amount.

    Returns:
        float: returns amount converted into USD
    '''
    # parameters to GET
    PARAMS = {'app_id':exchange_app_id}
    # base url
    URL = exchange_rates_url
    # GET request
    r = requests.get(url = URL, params = PARAMS)
    # extracting data in json format
    data = r.json()
    # USD rate of corresponding currency
    USD_rate = data['rates'][currency_code.upper()]
    # convert amount into USD
    usd_amount = amount/USD_rate

    return usd_amount


@api_view(['GET'])
def rates(request, date_from, date_to, origin, destination):
    '''
    API endpoint that returns a list with the average prices for each day
    on a route between Port Codes origin and destination.

    Parameters:
        date_from (date)    : The from date.
        date_to (date)      : The to date.
        origin (str)        : The origin port.
        destination (str)   : The destination port.


    Returns:
        list: returns a list with the average prices for each day
            on a route between Port Codes origin and destination

    Curl:
        curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates/2016-01-01/2016-01-01/CNSGH/north_europe_main/
    '''

    # converting data into dictionary format to serialiser
    data = {"date_from":date_from,
            "date_to":date_to,
            "origin":origin,
            "destination":destination
            }

    # check data with serializer
    serializer = RatesSerializer(data=data)

    # if serialiser not valid
    if not serializer.is_valid():
        # return error message
        return get_error_message("DATA_ERROR", str(serializer.errors))

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
    API endpoint that returns a list with the average prices for each day
    on a route between Port Codes origin and destination,
    except null values for days on which
    there are less than 3 prices in total.

    Parameters:
        date_from (date)    : The from date.
        date_to (date)      : The to date.
        origin (str)        : The origin port.
        destination (str)   : The destination port.


    Returns:
        list: returns a list with the average prices for each day
            on a route between Port Codes origin and destination

    Curl:
        curl -X GET -H 'Content-Type: application/json' http://localhost:8000/api/rates_null/2016-01-01/2016-01-01/CNGGZ/EETLL/
    '''

    # converting data into dictionary format to serialiser
    data = {"date_from":date_from,
            "date_to":date_to,
            "origin":origin,
            "destination":destination
            }

    # check data with serializer
    serializer = RatesSerializer(data=data)

    # if serialiser not valid
    if not serializer.is_valid():
        # return error message
        return get_error_message("DATA_ERROR", str(serializer.errors))


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


@api_view(['GET'])
def rates_sql(request, date_from, date_to, origin, destination):
    '''
    API endpoint that returns a list with the average prices for each day
    on a route between Port Codes origin and destination,
    using raw SQL instead of using ORM querying tool.

    Parameters:
        date_from (date)    : The from date.
        date_to (date)      : The to date.
        origin (str)        : The origin port.
        destination (str)   : The destination port.


    Returns:
        list: returns a list with the average prices for each day
            on a route between Port Codes origin and destination

    Curl:
        curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates_sql/2016-01-01/2016-01-01/CNSGH/north_europe_main/
    '''

    # converting data into dictionary format to serialiser
    data = {"date_from":date_from,
            "date_to":date_to,
            "origin":origin,
            "destination":destination
            }

    # check data with serializer
    serializer = RatesSerializer(data=data)

    # if serialiser not valid
    if not serializer.is_valid():
        # return error message
        return get_error_message("DATA_ERROR", str(serializer.errors))

    # obtain corresponding code for slugs
    origin      = slug_to_code(slug=origin)
    destination = slug_to_code(slug=destination)

    # inputs to be given to cursor along with query
    input = (date_from, date_to)
    # format origin and destination into tuple like string structure ie: ('CNGGZ')
    origin = str(origin).replace("[","(").replace("]",")")
    destination = str(destination).replace("[","(").replace("]",")")

    # sql query
    sql_query = ''' SELECT  orig_code, dest_code, day, price
                    FROM api_prices
                    WHERE ( day BETWEEN %s AND %s AND orig_code IN {0} AND dest_code IN {1} )
                    '''.format( origin, destination)

    # query data after querying
    query_data = db_query(sql_query, input)

    # if query_data is not empty enter
    if query_data:
        # retrieving from database and converting into dataframe
        df = pd.DataFrame(query_data)
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


class UploadPriceViewSet(GenericAPIView):
    """
    API endpoint where you can upload a list of prices between
    date_from and date_to

    Parameters:
        price (list)            : The list of integer prices.
        date_from (date)        : The from date.
        date_to (date)          : The to date.
        origin_code (str)       : The origin port.
        destination_code (str)  : The destination port.

    Returns:
        list: returns a success or failure message

    Curl:
        curl -X POST -d '''{"date_from": "2016-01-01",
                            "date_to": "2016-01-02",
                            "origin_code": "CNGGZ",
                            "destination_code": "EETLL",
                            "price": [217, 315]}''' -H "Content-Type: application/json" http://localhost:8000/api/upload_price/

    """

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
        prices              = data['price']
        date_to             = data['date_to']
        date_from           = data['date_from']
        origin_code         = data['origin_code']
        destination_code    = data['destination_code']

        # if date length does not match
        if date_from != date_to:
            # generate a list of dates
            date_range = pd.date_range(start=date_from, end=date_to).date.tolist()

        # if generated date length and price doesnt match
        if len(date_range) != len(prices):
            # return error response
            return get_error_message("DATA_ERROR", "price and generated date length does not match")

        try:
            # obtain each date and price in list
            for date, price in zip(date_range, prices):
                # insert into database
                p = Prices( orig_code   = origin_code,
                            dest_code   = destination_code,
                            day         = date,
                            price       = price,
                            )
                # saving assigined data
                p.save()

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


class UploadUsdPriceViewSet(GenericAPIView):
    """
    API endpoint where you can upload a price,
    Accept prices in different currencies
    and convert into USD before saving

    Parameters:
        price (list)            : The list of integer prices.
        date_from (date)        : The from date.
        date_to (date)          : The to date.
        origin_code (str)       : The origin port.
        destination_code (str)  : The destination port.
        currency_code (str)     : The currency of price.


    Returns:
        list: returns a success or failure message

    Curl:
        curl -X POST -d '''{"date_from": "2016-01-01",
                            "date_to": "2016-01-02",
                            "origin_code": "CNGGZ",
                            "destination_code": "EETLL",
                            "price": [217, 315],
                            "currency_code": "INR"}''' -H "Content-Type: application/json" http://localhost:8000/api/upload_usd_price/

    """
    queryset = ''
    serializer_class = UploadUsdPricesSerializer

    def post(self, request, *args, **kwargs):

        # obtain the data
        data = request.data
        # check data with serializer
        serializer = UploadUsdPricesSerializer(data=data)
        # if serialiser not valid
        if not serializer.is_valid():
            # return error message
            return get_error_message("DATA_ERROR", str(serializer.errors))

        # inputs from API
        prices              = data['price']
        date_to             = data['date_to']
        date_from           = data['date_from']
        origin_code         = data['origin_code']
        destination_code    = data['destination_code']
        currency_code       = data['currency_code']


        # if date length does not match
        if date_from != date_to:
            # generate a list of dates
            date_range = pd.date_range(start=date_from, end=date_to).date.tolist()

        # if generated date length and price doesnt match
        if len(date_range) != len(prices):
            # return error response
            return get_error_message("DATA_ERROR", "price and generated date length does not match")


        try:
            # obtain each date and price in list
            for date, price in zip(date_range, prices):

                # convert price into USD
                price = exchange_rates(price, currency_code)

                # insert into database
                p = Prices( orig_code   = origin_code,
                            dest_code   = destination_code,
                            day         = date,
                            price       = price,
                            )
                # saving assigined data
                p.save()

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
