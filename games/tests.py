from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from games.services.result import determine_winner
from games.views.counter import _get_counter_cards, _clear_counter_cards

User = get_user_model()


class DetermineWinnerTests(TestCase):
    """모델 없이 지금 바로 돌릴 수 있는 테스트"""

    def test_high_rule_attacker_wins(self):
        self.assertEqual(determine_winner(7, 3, "HIGH"), "attacker")

    def test_high_rule_defender_wins(self):
        self.assertEqual(determine_winner(3, 7, "HIGH"), "defender")

    def test_low_rule_attacker_wins(self):
        self.assertEqual(determine_winner(2, 8, "LOW"), "attacker")

    def test_draw(self):
        self.assertIsNone(determine_winner(5, 5, "HIGH"))

    def test_invalid_rule_raises(self):
        with self.assertRaises(ValueError):
            determine_winner(1, 2, "INVALID")


# 아래는 games/models.py 머지된 뒤에 활성화
# class CounterAttackViewTests(TestCase):
#     def setUp(self):
#         self.attacker = User.objects.create_user(username="attacker", password="pw")
#         self.defender = User.objects.create_user(username="defender", password="pw")
#         self.game = Game.objects.create(
#             attacker=self.attacker, defender=self.defender,
#             attacker_card=7, winning_rule="HIGH", status=Game.GameStatus.PENDING,
#         )
#
#     def test_login_required(self):
#         response = self.client.get(reverse("games:counter", args=[self.game.id]))
#         self.assertEqual(response.status_code, 302)
#
#     def test_wrong_user_blocked(self):
#         other = User.objects.create_user(username="other", password="pw")
#         self.client.force_login(other)
#         response = self.client.post(
#             reverse("games:counter", args=[self.game.id]), {"defender_card": 5}
#         )
#         self.assertEqual(self.game.status, Game.GameStatus.PENDING)


class CounterCardSessionTests(TestCase):
    """반격 카드가 새로고침해도 유지되는지 테스트 (모델 없이 지금 바로 실행 가능)"""

    def setUp(self):
        self.factory = RequestFactory()

    def _build_request_with_session(self, path="/games/1/counter/"):
        request = self.factory.get(path)
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_cards_persist_on_refresh(self):
        """같은 요청 흐름에서 두 번 호출해도 카드가 동일해야 함 (=새로고침 시 안 바뀜)"""
        request = self._build_request_with_session()

        first_cards = _get_counter_cards(request, game_id=1)
        second_cards = _get_counter_cards(request, game_id=1)

        self.assertEqual(first_cards, second_cards)

    def test_cards_are_five_unique_numbers_in_range(self):
        """1~10 범위, 중복 없는 5장인지 검증"""
        request = self._build_request_with_session()
        cards = _get_counter_cards(request, game_id=1)

        self.assertEqual(len(cards), 5)
        self.assertEqual(len(set(cards)), 5)
        self.assertTrue(all(1 <= card <= 10 for card in cards))

    def test_cards_are_scoped_per_game(self):
        """게임마다 카드가 별도 세션 키로 저장되는지 (게임 A/B 카드 섞임 방지)"""
        request = self._build_request_with_session()

        _get_counter_cards(request, game_id=1)
        _get_counter_cards(request, game_id=2)

        self.assertIn("counter_cards_1", request.session)
        self.assertIn("counter_cards_2", request.session)

    def test_clear_removes_session_key(self):
        """반격 완료 후 세션에서 카드가 제거되는지"""
        request = self._build_request_with_session()

        _get_counter_cards(request, game_id=1)
        self.assertIn("counter_cards_1", request.session)

        _clear_counter_cards(request, game_id=1)
        self.assertNotIn("counter_cards_1", request.session)