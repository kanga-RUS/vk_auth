from django.shortcuts import redirect, render


def handler404(request, exception, template_name="404.html"):
    response = render(request, template_name="errors/404.html", status=404)
    return response


def handler500(request, template_name="500.html"):
    response = render(request, template_name="errors/500.html", status=500)
    return response


def home_redirect(request):
    return redirect('/')
