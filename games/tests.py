from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from games.models import Game
from games.services.result import determine_winner, process_counter
from games.views.counter import _get_counter_cards, _clear_counter_cards

from django.core.exceptions import PermissionDenied
from games.services.attack import process_attack
User = get_user_model()


class DetermineWinnerTests(TestCase):
    def test_high_rule_attacker_wins(self):
        self.assertEqual(determine_winner(7, 3, Game.WinningRule.HIGH), "attacker")

    def test_high_rule_defender_wins(self):
        self.assertEqual(determine_winner(3, 7, Game.WinningRule.HIGH), "defender")

    def test_low_rule_attacker_wins(self):
        self.assertEqual(determine_winner(2, 8, Game.WinningRule.LOW), "attacker")

    def test_draw(self):
        self.assertIsNone(determine_winner(5, 5, Game.WinningRule.HIGH))

    def test_invalid_rule_raises(self):
        with self.assertRaises(ValueError):
            determine_winner(1, 2, "INVALID")


class CounterCardSessionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request_with_session(self, path="/games/1/counter/"):
        request = self.factory.get(path)
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_cards_persist_on_refresh(self):
        request = self._build_request_with_session()
        first_cards = _get_counter_cards(request, game_id=1)
        second_cards = _get_counter_cards(request, game_id=1)
        self.assertEqual(first_cards, second_cards)

    def test_cards_are_five_unique_numbers_in_range(self):
        request = self._build_request_with_session()
        cards = _get_counter_cards(request, game_id=1)
        self.assertEqual(len(cards), 5)
        self.assertEqual(len(set(cards)), 5)
        self.assertTrue(all(1 <= card <= 10 for card in cards))

    def test_cards_are_scoped_per_game(self):
        request = self._build_request_with_session()
        _get_counter_cards(request, game_id=1)
        _get_counter_cards(request, game_id=2)
        self.assertIn("counter_cards_1", request.session)
        self.assertIn("counter_cards_2", request.session)

    def test_clear_removes_session_key(self):
        request = self._build_request_with_session()
        _get_counter_cards(request, game_id=1)
        _clear_counter_cards(request, game_id=1)
        self.assertNotIn("counter_cards_1", request.session)


class ProcessCounterTests(TestCase):
    """실제 DB(Game 모델)를 사용하는 반격 처리 테스트"""

    def setUp(self):
        self.attacker = User.objects.create_user(username="attacker", password="pw", score=0)
        self.defender = User.objects.create_user(username="defender", password="pw", score=0)
        self.game = Game.objects.create(
            attacker=self.attacker,
            defender=self.defender,
            attacker_card=7,
            winning_rule=Game.WinningRule.HIGH,
            status=Game.Status.PENDING,
        )

    def test_attacker_wins_updates_score_and_status(self):
        process_counter(game_id=self.game.id, defender_user=self.defender, defender_card=3)

        self.game.refresh_from_db()
        self.attacker.refresh_from_db()
        self.defender.refresh_from_db()

        self.assertEqual(self.game.status, Game.Status.COMPLETED)
        self.assertEqual(self.game.winner, self.attacker)
        self.assertEqual(self.attacker.score, 7)
        self.assertEqual(self.defender.score, -3)
        self.assertIsNotNone(self.game.completed_at)

    def test_defender_wins_updates_score(self):
        process_counter(game_id=self.game.id, defender_user=self.defender, defender_card=9)

        self.game.refresh_from_db()
        self.attacker.refresh_from_db()
        self.defender.refresh_from_db()

        self.assertEqual(self.game.winner, self.defender)
        self.assertEqual(self.attacker.score, -7)
        self.assertEqual(self.defender.score, 9)

    def test_draw_no_score_change(self):
        self.game.attacker_card = 5
        self.game.save()

        process_counter(game_id=self.game.id, defender_user=self.defender, defender_card=5)

        self.game.refresh_from_db()
        self.attacker.refresh_from_db()
        self.defender.refresh_from_db()

        self.assertIsNone(self.game.winner)
        self.assertEqual(self.attacker.score, 0)
        self.assertEqual(self.defender.score, 0)

    def test_wrong_user_cannot_counter(self):
        other = User.objects.create_user(username="other", password="pw")

        with self.assertRaises(PermissionError):
            process_counter(game_id=self.game.id, defender_user=other, defender_card=3)

        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.Status.PENDING)

    def test_already_completed_game_cannot_counter_again(self):
        process_counter(game_id=self.game.id, defender_user=self.defender, defender_card=3)

        with self.assertRaises(PermissionError):
            process_counter(game_id=self.game.id, defender_user=self.defender, defender_card=5)


class CounterAttackViewTests(TestCase):
    """뷰 레벨 통합 테스트 (로그인, 권한, 카드 조작 방지)"""

    def setUp(self):
        self.attacker = User.objects.create_user(username="attacker", password="pw")
        self.defender = User.objects.create_user(username="defender", password="pw")
        self.game = Game.objects.create(
            attacker=self.attacker,
            defender=self.defender,
            attacker_card=7,
            winning_rule=Game.WinningRule.HIGH,
            status=Game.Status.PENDING,
        )

    def test_login_required(self):
        response = self.client.get(f"/games/{self.game.id}/counter/")
        self.assertEqual(response.status_code, 302)

    def test_wrong_user_gets_403(self):
        other = User.objects.create_user(username="other", password="pw")
        self.client.force_login(other)

        response = self.client.get(f"/games/{self.game.id}/counter/")
        self.assertEqual(response.status_code, 403)

    def test_defender_can_view_counter_page(self):
        self.client.force_login(self.defender)

        response = self.client.get(f"/games/{self.game.id}/counter/")
        self.assertEqual(response.status_code, 200)

    def test_submitting_card_not_in_session_is_rejected(self):
        self.client.force_login(self.defender)
        self.client.get(f"/games/{self.game.id}/counter/")  # 세션에 카드 생성

        response = self.client.post(
            f"/games/{self.game.id}/counter/", {"defender_card": 999}
        )

        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.Status.PENDING)
        self.assertEqual(response.status_code, 200)  # 에러 메시지와 함께 폼 재표시

# ─────────────────────────────────────────────
# 공격 신청/취소 테스트 — 역할3(공격) 담당
# ─────────────────────────────────────────────
class ProcessAttackServiceTests(TestCase):
    def setUp(self):
        self.attacker = User.objects.create_user(username="atk_a", password="pw")
        self.defender = User.objects.create_user(username="atk_b", password="pw")
        self.cards = [1, 3, 5, 7, 9]

    def test_valid_attack_creates_pending_game(self):
        game = process_attack(
            attacker=self.attacker, defender_id=self.defender.pk,
            attacker_card=5, allowed_cards=self.cards,
        )
        self.assertEqual(game.status, Game.Status.PENDING)
        self.assertIn(game.winning_rule, [Game.WinningRule.HIGH, Game.WinningRule.LOW])

    def test_card_not_in_allowed_cards_is_rejected(self):
        with self.assertRaises(ValueError):
            process_attack(
                attacker=self.attacker, defender_id=self.defender.pk,
                attacker_card=10, allowed_cards=self.cards,
            )

    def test_self_attack_is_rejected(self):
        with self.assertRaises(PermissionDenied):
            process_attack(
                attacker=self.attacker, defender_id=self.attacker.pk,
                attacker_card=5, allowed_cards=self.cards,
            )

    def test_nonexistent_defender_is_rejected(self):
        with self.assertRaises(ValueError):
            process_attack(
                attacker=self.attacker, defender_id=99999,
                attacker_card=5, allowed_cards=self.cards,
            )


class AttackViewTests(TestCase):
    def setUp(self):
        self.attacker = User.objects.create_user(username="view_a", password="pw")
        self.defender = User.objects.create_user(username="view_b", password="pw")

    def test_login_required(self):
        response = self.client.get(reverse("games:attack"))
        self.assertEqual(response.status_code, 302)

    def test_get_shows_five_cards_and_opponent_list(self):
        self.client.force_login(self.attacker)
        response = self.client.get(reverse("games:attack"))

        self.assertEqual(len(response.context["cards"]), 5)
        opponents = list(response.context["opponents"])
        self.assertIn(self.defender, opponents)
        self.assertNotIn(self.attacker, opponents)

    def test_cards_do_not_change_on_refresh(self):
        self.client.force_login(self.attacker)
        first = self.client.get(reverse("games:attack")).context["cards"]
        second = self.client.get(reverse("games:attack")).context["cards"]
        self.assertEqual(first, second)

    def test_successful_attack_creates_game_and_redirects(self):
        self.client.force_login(self.attacker)
        cards = self.client.get(reverse("games:attack")).context["cards"]

        response = self.client.post(
            reverse("games:attack"),
            {"attacker_card": cards[0], "defender_id": self.defender.pk},
        )

        game = Game.objects.get(attacker=self.attacker, defender=self.defender)
        self.assertRedirects(response, reverse("games:detail", args=[game.id]))

    def test_attack_without_selecting_card_shows_error(self):
        self.client.force_login(self.attacker)
        self.client.get(reverse("games:attack"))

        response = self.client.post(
            reverse("games:attack"),
            {"attacker_card": "", "defender_id": self.defender.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Game.objects.filter(attacker=self.attacker).exists())

    def test_self_attack_is_blocked(self):
        self.client.force_login(self.attacker)
        cards = self.client.get(reverse("games:attack")).context["cards"]

        response = self.client.post(
            reverse("games:attack"),
            {"attacker_card": cards[0], "defender_id": self.attacker.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Game.objects.filter(attacker=self.attacker).exists())


class CancelGameTests(TestCase):
    def setUp(self):
        self.attacker = User.objects.create_user(username="cancel_a", password="pw")
        self.defender = User.objects.create_user(username="cancel_b", password="pw")
        self.stranger = User.objects.create_user(username="cancel_c", password="pw")

        self.pending_game = Game.objects.create(
            attacker=self.attacker, defender=self.defender,
            attacker_card=4, winning_rule=Game.WinningRule.HIGH,
            status=Game.Status.PENDING,
        )

    def test_attacker_can_cancel_pending_game(self):
        self.client.force_login(self.attacker)
        response = self.client.get(reverse("games:cancel", args=[self.pending_game.id]))

        self.pending_game.refresh_from_db()
        self.assertEqual(self.pending_game.status, Game.Status.CANCELLED)
        self.assertRedirects(response, reverse("games:history"))

    def test_defender_cannot_cancel(self):
        self.client.force_login(self.defender)
        response = self.client.get(reverse("games:cancel", args=[self.pending_game.id]))
        self.assertEqual(response.status_code, 403)

    def test_cannot_cancel_after_countered(self):
        self.pending_game.status = Game.Status.COMPLETED
        self.pending_game.save()

        self.client.force_login(self.attacker)
        response = self.client.get(reverse("games:cancel", args=[self.pending_game.id]))
        self.assertEqual(response.status_code, 403)

        