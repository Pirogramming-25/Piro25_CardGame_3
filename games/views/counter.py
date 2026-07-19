from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def counter_attack(request, game_id):
    return render(
        request,
        "games/counter.html",
        {"game_id": game_id},
    )


@login_required
def result(request, game_id):
    return render(
        request,
        "games/result.html",
        {"game_id": game_id},
    )