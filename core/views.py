from django.shortcuts import render


def main(request):
    return render(request, "core/main.html")


def ranking(request):
    return render(request, "core/ranking.html")