from django.db import transaction
from django.utils import timezone

from games.models import Game


def determine_winner(attacker_card: int, defender_card: int, winning_rule: str):
    """
    attacker_card, defender_card: 제출된 카드 숫자
    winning_rule: Game.WinningRule.HIGH("high") 또는 Game.WinningRule.LOW("low")
    반환: "attacker" / "defender" / None(무승부)
    """
    if attacker_card == defender_card:
        return None

    if winning_rule == Game.WinningRule.HIGH:
        return "attacker" if attacker_card > defender_card else "defender"
    elif winning_rule == Game.WinningRule.LOW:
        return "attacker" if attacker_card < defender_card else "defender"

    raise ValueError(f"알 수 없는 winning_rule 값: {winning_rule}")


def process_counter(game_id: int, defender_user, defender_card: int):
    """
    반격 처리 전체 흐름.
    game_id: 반격 대상 게임 PK
    defender_user: request.user (반격 시도자)
    defender_card: 선택한 반격 카드 숫자
    """
    with transaction.atomic():
        game = Game.objects.select_for_update().get(pk=game_id)

        if not game.can_counter(defender_user):
            raise PermissionError("반격할 수 없는 게임입니다.")

        if defender_card not in range(1, 11):
            raise ValueError("잘못된 카드 값입니다.")

        game.defender_card = defender_card

        winner_side = determine_winner(
            game.attacker_card, defender_card, game.winning_rule
        )

        if winner_side == "attacker":
            game.winner = game.attacker
            game.attacker_score_change = game.attacker_card
            game.defender_score_change = -game.defender_card
        elif winner_side == "defender":
            game.winner = game.defender
            game.attacker_score_change = -game.attacker_card
            game.defender_score_change = game.defender_card
        else:
            game.winner = None
            game.attacker_score_change = 0
            game.defender_score_change = 0

        game.attacker.score += game.attacker_score_change
        game.defender.score += game.defender_score_change
        game.attacker.save(update_fields=["score"])
        game.defender.save(update_fields=["score"])

        game.status = Game.Status.COMPLETED
        game.completed_at = timezone.now()
        game.save()

    return game