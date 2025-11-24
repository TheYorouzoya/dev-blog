from django.shortcuts import HttpResponse


def index(request):
    return HttpResponse("Hello, World! This is the start of my blog app.")
