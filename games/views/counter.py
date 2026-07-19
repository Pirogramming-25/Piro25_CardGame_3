from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from games.services.result import process_counter


@login_required
def counter_attack(request, game_id):
    from games.models import Game  # 순환 참조 방지

    game = get_object_or_404(Game, pk=game_id)
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
                    "attacker_card": game.attacker_card,
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
            "attacker_card": game.attacker_card,
            "cards": cards,
        },
    )


def _get_counter_cards(request, game_id):
    """
    반격 카드 5장을 세션에 저장해서 새로고침해도 유지되게 함.
    게임마다 별도 키로 저장 (game_id로 구분).
    """
    import random

    session_key = f"counter_cards_{game_id}"

    if session_key not in request.session:
        request.session[session_key] = random.sample(range(1, 11), 5)

    return request.session[session_key]


def _clear_counter_cards(request, game_id):
    """반격 완료 후 세션에서 카드 목록 제거 (다음 게임에 영향 없도록)"""
    session_key = f"counter_cards_{game_id}"
    request.session.pop(session_key, None)