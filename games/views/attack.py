from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def attack(request):
    return render(request, "games/attack.html")


@login_required
def cancel_game(request, game_id):
    return render(
        request,
        "games/detail.html",
        {"game_id": game_id},
    )