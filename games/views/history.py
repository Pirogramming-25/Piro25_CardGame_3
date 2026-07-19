from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def history(request):
    return render(request, "games/history.html")


@login_required
def detail(request, game_id):
    return render(
        request,
        "games/detail.html",
        {"game_id": game_id},
    )