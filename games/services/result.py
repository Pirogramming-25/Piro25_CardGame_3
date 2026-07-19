from django.db import transaction


def determine_winner(attacker_card: int, defender_card: int, winning_rule: str):
    """
    attacker_card, defender_card: 제출된 카드 숫자
    winning_rule: Game.winning_rule 값 ("HIGH" 또는 "LOW" — 승현 확정 필요)
    반환: "attacker" / "defender" / None(무승부)
    """
    if attacker_card == defender_card:
        return None

    if winning_rule == "HIGH":
        return "attacker" if attacker_card > defender_card else "defender"
    elif winning_rule == "LOW":
        return "attacker" if attacker_card < defender_card else "defender"

    raise ValueError(f"알 수 없는 winning_rule 값: {winning_rule}")


def process_counter(game_id: int, defender_user, defender_card: int):
    """
    반격 처리 전체 흐름.
    game_id: 반격 대상 게임 PK
    defender_user: request.user (반격 시도자)
    defender_card: 선택한 반격 카드 숫자
    """
    from games.models import Game  # 순환 참조 방지를 위해 함수 내부 import

    with transaction.atomic():
        game = Game.objects.select_for_update().get(pk=game_id)

        if game.status != Game.GameStatus.PENDING:
            raise PermissionError("이미 처리된 게임입니다.")

        if game.defender_id != defender_user.id:
            raise PermissionError("본인에게 요청된 게임이 아닙니다.")

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

        game.status = Game.GameStatus.COMPLETED
        game.save()

    return game