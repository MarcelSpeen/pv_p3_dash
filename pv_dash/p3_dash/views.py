from django.shortcuts import render

def p3_view(request):
    return render(request, 'p3_dash/dashboard.html')