from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import render

from games.models import Game

User = get_user_model()


def main(request):
    context = {}
    if request.user.is_authenticated:
        context["pending_attacks"] = Game.objects.filter(
            defender=request.user,
            status=Game.Status.PENDING,
        ).count()
    return render(request, "core/main.html", context)


def ranking(request):
    users = User.objects.annotate(
        wins=Count("won_games")
    ).order_by("-score", "-wins", "date_joined")

    ranked = []
    for idx, u in enumerate(users, start=1):
        ranked.append({
            "rank": idx,
            "user": u,
            "is_me": request.user.is_authenticated and u.id == request.user.id,
        })

    top3 = ranked[:3]
    rest = ranked[3:]
    return render(request, "core/ranking.html", {"top3": top3, "rest": rest})
