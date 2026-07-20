import random

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction

from games.models import Game

User = get_user_model()


def get_opponent_choices(user):
    """공격 가능한 상대 목록 (본인 제외)."""
    return User.objects.exclude(pk=user.pk).order_by("username")


def process_attack(attacker, defender_id, attacker_card, allowed_cards):
    """
    공격 신청 처리.

    attacker: request.user (공격자)
    defender_id: 상대로 선택한 유저의 pk
    attacker_card: 선택한 카드 숫자
    allowed_cards: 이번 턴에 제공된 카드 5장 (세션 값) — 조작 방지 검증용
    """
    try:
        defender_id = int(defender_id)
    except (TypeError, ValueError):
        raise ValueError("공격 상대를 선택해주세요.")

    try:
        attacker_card = int(attacker_card)
    except (TypeError, ValueError):
        raise ValueError("카드를 선택해주세요.")

    if attacker_card not in allowed_cards:
        raise ValueError("제공되지 않은 카드입니다.")

    if defender_id == attacker.pk:
        raise PermissionDenied("자기 자신은 공격할 수 없습니다.")

    defender = User.objects.filter(pk=defender_id).first()
    if defender is None:
        raise ValueError("존재하지 않는 사용자입니다.")

    with transaction.atomic():
        game = Game.objects.create(
            attacker=attacker,
            defender=defender,
            attacker_card=attacker_card,
            winning_rule=random.choice(Game.WinningRule.values),
            status=Game.Status.PENDING,
        )

    return game