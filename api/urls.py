# Django imports
from django.urls import path

# REST imports
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

# local imports
from api import views

urlpatterns = [

    # API doc
    path('', include_docs_urls(title='Rate API', public=True)),

    # scheme view
    path('schema/', get_schema_view(title="Rate API"), name="schema_view"),

    # GET average_price for each day
    path('rates/<str:date_from>/<str:date_to>/<str:origin>/<str:destination>/', views.rates, name="rates"),

    # GET average_price null for less than 3 prices
    path('rates_null/<str:date_from>/<str:date_to>/<str:origin>/<str:destination>/', views.rates_null, name="rates_null"),

    # GET average_price for each day
    path('rates_sql/<str:date_from>/<str:date_to>/<str:origin>/<str:destination>/', views.rates_sql, name="rates_sql"),

    # POST upload_price
    path('upload_price/', views.UploadPriceViewSet.as_view(), name="upload_price"),

    # POST upload_usd_price
    path('upload_usd_price/', views.UploadUsdPriceViewSet.as_view(), name="upload_usd_price"),


]
