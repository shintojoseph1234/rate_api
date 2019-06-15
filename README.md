# Rates API

Rates API is an HTTP-based API capable of

## Installation

Install virtual enviroonment  [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) for Dependency Management: Prevent conflicts between dependencies of multiple projects.

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

## POST API's

## Upload Price API

```bash
curl -X POST -d '''{"date_from": "2016-01-01","date_to": "2016-01-02","origin_code": "CNGGZ","destination_code": "EETLL","price": [217, 315]}''' -H "Content-Type: application/json" http://localhost:8000/api/upload_price/
```
## Upload USD Price API

```bash
curl -X POST -d '''{"date_from": "2016-01-01","date_to": "2016-01-02","origin_code": "CNGGZ","destination_code": "EETLL","price": [217, 315],"currency_code": "INR"}''' -H "Content-Type: application/json" http://localhost:8000/api/upload_usd_price/
```

## GET API's

## Rates API

```bash
curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates/2016-01-01/2016-01-02/CNGGZ/EETLL/
```
## Rates null API

```bash
curl -X GET -H 'Content-Type: application/json'  http://localhost:8000/api/rates_null/2016-01-01/2016-01-02/CNGGZ/EETLL/
```


## Batch processing
