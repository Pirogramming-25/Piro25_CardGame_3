from django.urls import path

from games.views.attack import attack, cancel_game
from games.views.counter import counter_attack, result
from games.views.history import detail, history

app_name = "games"

urlpatterns = [
    path("attack/", attack, name="attack"),
    path("history/", history, name="history"),
    path("<int:game_id>/", detail, name="detail"),
    path("<int:game_id>/cancel/", cancel_game, name="cancel"),
    path("<int:game_id>/counter/", counter_attack, name="counter"),
    path("<int:game_id>/result/", result, name="result"),
]