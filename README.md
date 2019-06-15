# Rates API

Rates API is an HTTP-based API capable of returning average prices for each day on a route between Port Codes origin and destination

## Installation

Install virtual enviroonment  [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) for Dependency Management

```bash
pip install virtualenv
```
Create and Activate a virtual environment

```bash
virtualenv rates_API_env
source rates_API_env/bin/activate
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt.

```bash
pip install --upgrade -r requirements.txt
```
Execute Dockerfile and start the container
```bash
docker build -t ratestask .
docker run -p 0.0.0.0:5432:5432 --name ratestask ratestask
```

Migrate the database
```bash
python manage.py makemigrations
python manage.py migrate
```
Run the unittests if required
```bash
python manage.py test
```
Run the server
```bash
python manage.py runserver 8000
```
Open  [localhost:8000](http://localhost:8000/)  in a browser to see the UI

Open  [localhost:8000/api](http://localhost:8000/api/)  in a browser to see the available API

Open  [localhost:8000/api/schema](http://localhost:8000/api/schema/)  in a browser to see the schema of all API

## Packaging

Alternatively you can also make the entire app into a package
```bash
python setup.py sdist
```
This creates a directory called dist and builds your new package, rate_API-0.1.tar.gz inside it.

You can then install it by  
```bash
pip install rate_API-0.1.tar.gz
```
## POST API's

## Upload Price API
API endpoint where you can upload a price, including the following parameters: date_from, date_to, origin_code, destination_code, price

```bash
curl -X POST -d '''{"date_from": "2016-01-01","date_to": "2016-01-02","origin_code": "CNGGZ","destination_code": "EETLL","price": [217, 315]}''' -H "Content-Type: application/json" http://localhost:8000/api/upload_price/
```
## Upload USD Price API
API endpoint where you can upload prices in different currencies, including the following parameters: date_from, date_to, origin_code, destination_code, price, currency_code

```bash
curl -X POST -d '''{"date_from": "2016-01-01","date_to": "2016-01-02","origin_code": "CNGGZ","destination_code": "EETLL","price": [217, 315],"currency_code": "INR"}''' -H "Content-Type: application/json" http://localhost:8000/api/upload_usd_price/
```

## GET API's

## Rates API
API endpoint that takes the following parameters: date_from, date_to, origin, destination and returns a list with the average prices for each day on a route between Port Codes origin and destination

```bash
curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates/2016-01-01/2016-01-02/CNGGZ/EETLL/
```
## Rates null API
API endpoint that takes the following parameters: date_from, date_to, origin, destination and returns a list with the average prices for each day on a route between Port Codes origin and destination except null values for days on which there are less than 3 prices in total.

```bash
curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates_null/2016-01-01/2016-01-02/CNGGZ/EETLL/
```


## Batch processing
When receiving and updating big batches of new prices

-  Noticed that data is in the format of timeseries. So change the database to a NoSQL database (MongoDB),
   so that inserting and updating large amount of data to the database can be done fastly.
-  Optimise the function with big calculations using [numba](https://numba.pydata.org/) or [cython](https://cython.readthedocs.io/en/latest/src/tutorial/cython_tutorial.html)  
