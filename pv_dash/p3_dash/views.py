from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. Welkom aya.")


from django.shortcuts import render

# Create your views here.
