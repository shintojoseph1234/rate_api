from django.urls import reverse
from django.test import TestCase, Client

# REST imports
from rest_framework import status
from rest_framework.test import APITestCase

# other imports
import datetime

# local imports
from api.models import Prices

# initialize client
client = Client()

# Test Prices Model
class PricesTest(TestCase):
    '''
    Test module for Prices model
    '''

    def setUp(self):

        Prices.objects.create(
            orig_code='CNGGZ',
            dest_code='EETLL',
            day=datetime.datetime.strptime('2016-01-02', '%Y-%m-%d'),
            price=1244
            )

        Prices.objects.create(
            orig_code='CNGGZ',
            dest_code='SEGOT',
            day=datetime.datetime.strptime('2016-01-01', '%Y-%m-%d'),
            price=1647
            )

    def test_price(self):

        EETLL_price = Prices.objects.get(
            orig_code='CNGGZ',
            dest_code='EETLL',
            day=datetime.datetime.strptime('2016-01-02', '%Y-%m-%d'),
            )

        SEGOT_price = Prices.objects.get(
            orig_code='CNGGZ',
            dest_code='SEGOT',
            day=datetime.datetime.strptime('2016-01-01', '%Y-%m-%d'),
            )

        self.assertEqual(EETLL_price.get_price(), 1244)
        self.assertEqual(SEGOT_price.get_price(), 1647)

# POST API upload_price Test
class Test_A_UploadPriceAPI(APITestCase):

    # initialize inputs
    def setUp(self):

        self.valid_input = {"date_from": "2016-01-01",
                            "date_to": "2016-01-02",
                        	"origin_code": "CNGGZ",
                        	"destination_code": "EETLL",
                        	"price": [217, 315]
                            }

        self.invalid_input_1 = {"date_from": "2016-01-01",
                                "date_to": "2016-01-03",
                            	"origin_code": "CNGGZ",
                            	"destination_code": "EETLL",
                            	"price": [217]
                                }

        self.invalid_input_2 = {"date_from": "2016-01-01",
                                "date_to": "2014-01-03",
                            	"origin_code": "CNGGZ",
                            	"destination_code": "EETLL",
                            	"price": [217, 315]
                                }

    def test_valid_upload(self):

        # structure of the output data
        output_data = [{
                    	"status": True,
                    	"data": {
                    		"message": "Data successfully ingested"
                    	}
                    }]

        # url to be tested
        url = reverse('upload_price')

        # Obtaining the POST response for the input data
        response = self.client.post(url, self.valid_input, format='json')

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_upload_1(self):

        # structure of the output data
        output_data = [{
                    	"status": "error",
                    	"data": {
                    		"http_code": "400 BAD REQUEST",
                    		"errors": [{
                    			"error_code": 2000,
                    			"error_message": "price and generated date length does not match"
                    		}]
                    	}
                    }]

        # url to be tested
        url = reverse('upload_price')

        # Obtaining the POST response for the input data
        response = self.client.post(url, self.invalid_input_1, format='json')

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_upload_2(self):

        # structure of the output data
        output_data = [{
                    	"status": "error",
                    	"data": {
                    		"http_code": "400 BAD REQUEST",
                    		"errors": [{
                    			"error_code": 2000,
                    			"error_message": "{'non_field_errors': [ErrorDetail(string='date_from must be less than or equal to date_to', code='invalid')]}"
                    		}]
                    	}
                    }]

        # url to be tested
        url = reverse('upload_price')

        # Obtaining the POST response for the input data
        response = self.client.post(url, self.invalid_input_2, format='json')

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# POST API upload_usd_price Test
class Test_B_UploadUSDPriceAPI(APITestCase):

    # initialize inputs
    def setUp(self):

        self.valid_input = {"date_from": "2016-01-01",
                        	"date_to": "2016-01-02",
                        	"origin_code": "CNGGZ",
                        	"destination_code": "EETLL",
                        	"price": [217, 315],
                        	"currency_code": "INR"
                        }
        self.invalid_input = {  "date_from": "2016-01-01",
                            	"date_to": "2016-01-02",
                            	"origin_code": "CNGGZ",
                            	"destination_code": "EETLL",
                            	"price": [217, 315],
                            	"currency_code": "invalidcode"
                            }



    def test_valid_upload(self):

        # structure of the output data
        output_data = [{
                    	"status": True,
                    	"data": {
                    		"message": "Data successfully ingested"
                    	}
                    }]

        # url to be tested
        url = reverse('upload_usd_price')

        # Obtaining the POST response for the input data
        response = self.client.post(url, self.valid_input, format='json')

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_upload(self):

        # structure of the output data
        output_data = [{
                    	"status": True,
                    	"data": {
                    		"message": "Failed to ingest data"
                    	}
                    }]

        # url to be tested
        url = reverse('upload_usd_price')

        # Obtaining the POST response for the input data
        response = self.client.post(url, self.invalid_input, format='json')

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

# GET API rates Test
class Test_C_RatesAPI(APITestCase):

    # initialize inputs
    def setUp(self):

        Prices.objects.create(
            orig_code='CNGGZ',
            dest_code='EETLL',
            day=datetime.datetime.strptime('2016-01-01', '%Y-%m-%d'),
            price=10
            )

        Prices.objects.create(
            orig_code='CNGGZ',
            dest_code='EETLL',
            day=datetime.datetime.strptime('2016-01-02', '%Y-%m-%d'),
            price=20
            )

    def test_valid_rates(self):

        # input data to be given as request
        date_from = "2016-01-01"
        date_to = "2016-01-02"
        origin  = "CNGGZ"
        destination = "EETLL"

        # structure of the output data
        output_data = [{
                    	"status": "success",
                    	"data": [{
                    		"day": "2016-01-01",
                    		"average_price": 10
                    	}, {
                    		"day": "2016-01-02",
                    		"average_price": 20
                    	}]
                    }]

        # url to be tested
        url = reverse('rates', args=(date_from, date_to, origin, destination))

        # Obtaining the GET response
        response = self.client.get(url)

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_rates(self):

        # input data to be given as request
        date_from = "2016-01-01"
        date_to = "2014-01-02"
        origin  = "CNGGZ"
        destination = "EETLL"

        # structure of the output data
        output_data = [{
                    	'status': 'error',
                    	'data': {
                    		'http_code': '400 BAD REQUEST',
                    		'errors': [{
                    			'error_code': 2000,
                    			'error_message': "{'non_field_errors': [ErrorDetail(string='date_from must be less than or equal to date_to', code='invalid')]}"
                    		}]
                    	}
                    }]

        # url to be tested
        url = reverse('rates', args=(date_from, date_to, origin, destination))

        # Obtaining the GET response
        response = self.client.get(url)

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# GET API rates Test
class Test_D_RatesNullAPI(APITestCase):

    # initialize inputs
    def setUp(self):

        Prices.objects.create(
            orig_code='CNGGZ',
            dest_code='EETLL',
            day=datetime.datetime.strptime('2016-01-01', '%Y-%m-%d'),
            price=10
            )

        Prices.objects.create(
            orig_code='CNGGZ',
            dest_code='EETLL',
            day=datetime.datetime.strptime('2016-01-02', '%Y-%m-%d'),
            price=20
            )


    def test_valid_rates_null(self):

        # input data to be given as request
        date_from = "2016-01-01"
        date_to = "2016-01-02"
        origin  = "CNGGZ"
        destination = "EETLL"

        # structure of the output data
        output_data = [{
                    	"status": "success",
                    	"data": [{
                    		"day": "2016-01-01",
                    		"average_price": "null"
                    	}, {
                    		"day": "2016-01-02",
                    		"average_price": "null"
                    	}]
                    }]

        # url to be tested
        url = reverse('rates_null', args=(date_from, date_to, origin, destination))

        # Obtaining the GET response
        response = self.client.get(url)

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_rates_null(self):

        # input data to be given as request
        date_from = "2016-01-01"
        date_to = "2014-01-02"
        origin  = "CNGGZ"
        destination = "EETLL"

        # structure of the output data
        output_data = [{
                    	'status': 'error',
                    	'data': {
                    		'http_code': '400 BAD REQUEST',
                    		'errors': [{
                    			'error_code': 2000,
                    			'error_message': "{'non_field_errors': [ErrorDetail(string='date_from must be less than or equal to date_to', code='invalid')]}"
                    		}]
                    	}
                    }]

        # url to be tested
        url = reverse('rates', args=(date_from, date_to, origin, destination))

        # Obtaining the GET response
        response = self.client.get(url)

        # checking weather the outputa data is as per the requirement
        self.assertEqual(response.data, output_data)

        # checking wether the response is success
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
