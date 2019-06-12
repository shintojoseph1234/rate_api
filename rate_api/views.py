# django imports
from django.shortcuts import render


# default index view
def index(request):
    return render(request, "index.html", {})
