from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied

from games.models import Game

@login_required
def history(request):
    # 내가 attacker든 defender든 관련된 매치를 모두 최신순으로 보여줌
    games = (
        Game.objects.filter(Q(attacker=request.user) | Q(defender=request.user))
        .select_related("attacker", "defender", "winner")
        .order_by("-created_at")
    )
    
    # 템플릿은 메서드에 인자를 못 넘기니, 각 game에 미리 계산해서 붙여준다
    for game in games:
        game.viewer_can_cancel = game.can_cancel(request.user)
        game.viewer_can_counter = game.can_counter(request.user)

    # 상단 통계 카드용 집계
    wins = games.filter(status=Game.Status.COMPLETED, winner=request.user).count()
    losses = (
        games.filter(status=Game.Status.COMPLETED)
        .exclude(winner=request.user).exclude(winner__isnull=True)
        .count()
    )
    draws = games.filter(status=Game.Status.COMPLETED, winner__isnull=True).count()

    return render(request, "games/history.html", {
        "games": games,
        "me": request.user,
        "total": games.count(),
        "wins": wins,
        "losses": losses,
        "draws": draws,
    })

@login_required
def detail(request, game_id):
    #게임 상세 페이지(상태+보는 사람에 따라 다른 버튼/문구 보여줌)
    #존재하지 않으면 404, PENDING 상태면 defender_card/승패/점수변화는 컨텍스트에서 제외
    game = get_object_or_404(
        Game.objects.select_related("attacker", "defender", "winner"),
        pk=game_id,
    )
    if not game.is_related_user(request.user):
        raise PermissionDenied  # 403
    
    reveal_result = game.status == Game.Status.COMPLETED
    is_draw = reveal_result and game.winner_id is None

    
    context = {
        "game": game,
        "can_cancel": game.can_cancel(request.user),
        "can_counter": game.can_counter(request.user),
        "reveal_result": reveal_result,
        "is_draw": is_draw,
        "defender_card": game.defender_card if reveal_result else None,
    }
    return render(request, "games/detail.html", context)