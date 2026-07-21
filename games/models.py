from django.conf import settings
from django.db import models


class Game(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "반격 대기"
        COMPLETED = "completed", "완료"
        CANCELLED = "cancelled", "취소"

    class WinningRule(models.TextChoices):
        HIGH = "high", "높은 숫자 승리"
        LOW = "low", "낮은 숫자 승리"

    attacker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attacked_games",
    )

    defender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="defended_games",
    )

    attacker_card = models.PositiveSmallIntegerField()

    defender_card = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    winning_rule = models.CharField(
        max_length=10,
        choices=WinningRule.choices,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="won_games",
        null=True,
        blank=True,
    )

    attacker_score_change = models.IntegerField(
        default=0,
    )

    defender_score_change = models.IntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    def is_related_user(self, user):
        return (
            user.is_authenticated
            and user.pk in {
                self.attacker_id,
                self.defender_id,
            }
        )

    def can_cancel(self, user):
        return (
            user.is_authenticated
            and user.pk == self.attacker_id
            and self.status == self.Status.PENDING
        )

    def can_counter(self, user):
        return (
            user.is_authenticated
            and user.pk == self.defender_id
            and self.status == self.Status.PENDING
        )

    def __str__(self):
        return f"{self.attacker} vs {self.defender}"