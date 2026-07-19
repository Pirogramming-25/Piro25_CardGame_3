from django.shortcuts import render
from django.contrib.auth import get_user_model


def main(request):
    context = {}
    if request.user.is_authenticated:
        # Role 2가 Game 모델 만들면 아래 주석 해제
        # from games.models import Game
        # context["pending_attacks"] = Game.objects.filter(
        #     defender=request.user,
        #     status=Game.Status.PENDING,
        # ).count()
        context["pending_attacks"] = 0
    return render(request, "core/main.html", context)

User = get_user_model()

def ranking(request):
    # Role 2의 Game 모델 완성되면 아래 방식으로 승리수 정렬 추가
    # from django.db.models import Count
    # users = User.objects.annotate(wins=Count("won_games")).order_by(
    #     "-score", "-wins", "date_joined"
    # )
    users = User.objects.order_by("-score", "date_joined")

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