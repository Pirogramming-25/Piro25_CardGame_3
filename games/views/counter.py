import random

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from games.models import Game
from games.services.result import process_counter


@login_required
def counter_attack(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if not game.can_counter(request.user):
        raise PermissionDenied("반격할 수 없는 게임입니다.")

    cards = _get_counter_cards(request, game_id)

    if request.method == "POST":
        defender_card = request.POST.get("defender_card")

        try:
            defender_card = int(defender_card)
            if defender_card not in cards:
                raise ValueError("제공되지 않은 카드입니다.")

            process_counter(
                game_id=game.id,
                defender_user=request.user,
                defender_card=defender_card,
            )
        except (TypeError, ValueError, PermissionError):
            return render(
                request,
                "games/counter.html",
                {
                    "game_id": game_id,
                    "attacker": game.attacker,
                    "cards": cards,
                    "error": "카드를 다시 선택해주세요.",
                },
            )

        _clear_counter_cards(request, game_id)
        return redirect("games:detail", game_id=game.id)

    return render(
        request,
        "games/counter.html",
        {
            "game_id": game_id,
            "attacker": game.attacker,
            "cards": cards,
        },
    )


def _get_counter_cards(request, game_id):
    session_key = f"counter_cards_{game_id}"

    if session_key not in request.session:
        request.session[session_key] = random.sample(range(1, 11), 5)

    return request.session[session_key]


def _clear_counter_cards(request, game_id):
    session_key = f"counter_cards_{game_id}"
    request.session.pop(session_key, None)