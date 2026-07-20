import random

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from games.models import Game
from games.services.attack import get_opponent_choices, process_attack

SESSION_KEY = "attack_cards"


@login_required
def attack(request):
    cards = _get_attack_cards(request)
    opponents = get_opponent_choices(request.user)

    if request.method == "POST":
        defender_id = request.POST.get("defender_id")
        attacker_card = request.POST.get("attacker_card")

        try:
            game = process_attack(
                attacker=request.user,
                defender_id=defender_id,
                attacker_card=attacker_card,
                allowed_cards=cards,
            )
        except (ValueError, PermissionDenied) as exc:
            return render(
                request,
                "games/attack.html",
                {
                    "cards": cards,
                    "opponents": opponents,
                    "error": str(exc),
                },
            )

        _clear_attack_cards(request)
        return redirect("games:detail", game_id=game.id)

    return render(
        request,
        "games/attack.html",
        {
            "cards": cards,
            "opponents": opponents,
        },
    )


@login_required
def cancel_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if not game.can_cancel(request.user):
        raise PermissionDenied("취소할 수 없는 게임입니다.")

    game.status = Game.Status.CANCELLED
    game.save(update_fields=["status"])

    return redirect("games:history")


def _get_attack_cards(request):
    if SESSION_KEY not in request.session:
        request.session[SESSION_KEY] = random.sample(range(1, 11), 5)

    return request.session[SESSION_KEY]


def _clear_attack_cards(request):
    request.session.pop(SESSION_KEY, None)