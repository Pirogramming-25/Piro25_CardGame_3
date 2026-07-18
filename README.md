# Piro25_CardGame_3

## 팀 공통 개발 규칙

### 1. 브랜치 규칙

`develop` 브랜치에서는 직접 작업하거나 커밋하지 않습니다.

기능별로 새로운 브랜치를 생성한 뒤 작업합니다.

```bash
git checkout develop
git pull origin develop
git checkout -b 브랜치명
```

브랜치 이름은 다음 형식을 사용합니다.

```text
feat/기능명       새로운 기능 개발
fix/기능명        버그 수정
refactor/기능명   코드 구조 개선
style/기능명      CSS 및 디자인 수정
docs/기능명       문서 수정
test/기능명       테스트 코드 작성
```

예시:

```text
feat/attack
feat/game-history
fix/counter-validation
style/ranking-page
```

하나의 브랜치에서는 가능한 한 하나의 기능만 작업합니다.

---

### 2. 작업 시작 전 확인

작업을 시작하기 전에 반드시 최신 `develop` 브랜치를 받아옵니다.

```bash
git checkout develop
git pull origin develop
```

이미 생성한 작업 브랜치에 최신 변경사항을 반영하려면 다음 명령어를 사용합니다.

```bash
git checkout 작업브랜치
git merge develop
```

충돌이 발생한 경우 임의로 코드를 삭제하지 않고, 해당 파일을 작업한 팀원과 확인한 뒤 해결합니다.

---

### 3. 커밋 메시지 규칙

커밋 메시지는 다음 형식으로 작성합니다.

```text
타입: 작업 내용
```

사용 가능한 타입:

```text
feat: 새로운 기능 추가
fix: 오류 수정
refactor: 코드 구조 개선
style: UI 또는 CSS 수정
docs: README 등 문서 수정
test: 테스트 코드 추가 또는 수정
chore: 설정 및 기타 작업
```

예시:

```text
feat: 공격 카드 선택 기능 구현
fix: 동일 사용자 연속 공격 오류 수정
style: 랭킹 페이지 카드 디자인 수정
test: 반격 성공 조건 테스트 추가
```

`수정`, `작업`, `완료`처럼 작업 내용을 알 수 없는 커밋 메시지는 사용하지 않습니다.

---

### 4. Pull Request 규칙

작업이 완료되면 작업 브랜치를 원격 저장소에 올리고 Pull Request를 생성합니다.

```bash
git push origin 작업브랜치
```

PR에는 다음 내용을 작성합니다.

```markdown
## 작업 내용
- 구현한 기능
- 수정한 파일
- 주요 로직

## 테스트
- 직접 확인한 시나리오
- 실행한 테스트 명령어

## 리뷰 요청
- 중점적으로 확인할 부분
- 아직 해결하지 못한 부분
```

PR을 생성하기 전에 다음 사항을 확인합니다.

* 서버가 정상적으로 실행되는지 확인
* 기존 기능에 오류가 없는지 확인
* 불필요한 코드와 출력문 제거
* 마이그레이션 파일 누락 여부 확인
* `.env` 파일이 포함되지 않았는지 확인
* 테스트 코드가 통과하는지 확인

최소 한 명 이상의 리뷰를 받은 뒤 `develop` 브랜치에 병합합니다.

---

### 5. Django 앱 역할 구분

프로젝트 앱의 역할은 다음과 같이 구분합니다.

```text
accounts
- 로그인 및 로그아웃
- 사용자 모델
- 소셜 로그인
- 사용자 관련 signal

games
- 게임 생성 및 진행
- 공격 및 반격
- 게임 결과 처리
- 전적 조회
- 게임 관련 모델

core
- 메인 페이지
- 랭킹 페이지
- 공통 페이지
```

다른 앱의 기능이 필요한 경우 해당 앱의 코드를 직접 복사하지 않고, 모델·서비스 함수·URL을 통해 연결합니다.

---

### 6. View와 Service 역할 분리

복잡한 게임 로직은 `views.py`에 직접 작성하지 않고 `games/services/`에 작성합니다.

```text
games/services/attack.py
- 공격 처리
- 카드 사용 검증
- 공격 결과 반환

games/services/result.py
- 게임 종료 조건 확인
- 승패 처리
- 점수 및 결과 저장
```

`views.py`는 다음 역할만 담당하도록 합니다.

1. 요청 데이터 확인
2. 권한 및 로그인 여부 확인
3. Form 또는 Service 호출
4. Template 렌더링 또는 Redirect 처리

예시:

```python
def attack_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == "POST":
        result = process_attack(
            game=game,
            attacker=request.user,
            card_id=request.POST.get("card_id"),
        )

        if result.success:
            return redirect("games:detail", game_id=game.id)

    return render(request, "games/attack.html", {"game": game})
```

---

### 7. URL 작성 규칙

각 앱의 URL에는 `app_name`을 지정합니다.

```python
app_name = "games"
```

URL 이름은 기능을 명확하게 표현합니다.

```python
path("<int:game_id>/", views.game_detail, name="detail")
path("<int:game_id>/attack/", views.attack, name="attack")
path("<int:game_id>/counter/", views.counter, name="counter")
path("history/", views.history, name="history")
```

Template에서는 URL을 직접 입력하지 않고 `{% url %}` 태그를 사용합니다.

```django
<a href="{% url 'games:detail' game.id %}">
    게임 상세보기
</a>
```

---

### 8. Template 작성 규칙

모든 페이지는 기본적으로 `base.html`을 상속합니다.

```django
{% extends "base.html" %}
{% load static %}

{% block title %}
게임 공격
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/attack.css' %}">
{% endblock %}

{% block content %}
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/attack.js' %}"></script>
{% endblock %}
```

공통 헤더, 네비게이션, 버튼 등은 각 페이지에서 반복 작성하지 않고 `base.html` 또는 공통 컴포넌트로 관리합니다.

Template 안에서 복잡한 계산이나 게임 판정 로직을 작성하지 않습니다.

---

### 9. CSS 작성 규칙

공통 스타일과 페이지별 스타일을 구분합니다.

```text
reset.css
- 브라우저 기본 스타일 초기화

base.css
- 전체 레이아웃
- 폰트
- 헤더 및 네비게이션

components.css
- 버튼
- 카드
- 입력창
- 모달
- 배지

페이지명.css
- 해당 페이지에서만 사용하는 스타일
```

예시:

```text
attack.html  → attack.css
counter.html → counter.css
history.html → history.css
```

페이지별 CSS에서 `body`, `button`, `input` 등 공통 태그 스타일을 무분별하게 덮어쓰지 않습니다.

클래스 이름은 기능을 알 수 있도록 작성합니다.

```css
.attack-card {}
.attack-card__image {}
.attack-card__name {}
.attack-card--selected {}
```

`box1`, `text2`, `btn3`과 같이 의미를 알 수 없는 이름은 사용하지 않습니다.

---

### 10. JavaScript 작성 규칙

JavaScript 파일은 페이지별로 분리합니다.

```text
attack.html  → attack.js
counter.html → counter.js
```

HTML 내부에 긴 JavaScript 코드를 직접 작성하지 않습니다.

DOM 요소를 가져올 때 존재 여부를 확인합니다.

```javascript
const attackForm = document.querySelector(".attack-form");

if (attackForm) {
    attackForm.addEventListener("submit", (event) => {
        // 처리 로직
    });
}
```

디버깅이 끝난 뒤 불필요한 `console.log()`와 `alert()`를 제거합니다.

---

### 11. Model 및 Migration 규칙

Model을 수정한 사람은 반드시 마이그레이션 파일을 생성합니다.

```bash
python manage.py makemigrations
python manage.py migrate
```

생성한 마이그레이션 파일도 함께 커밋합니다.

이미 팀원이 사용 중인 마이그레이션 파일을 임의로 삭제하거나 수정하지 않습니다.

Model 필드명은 영어 소문자와 `_`를 사용합니다.

```python
created_at
updated_at
attacker
defender
is_finished
```

게임 상태나 카드 종류처럼 선택지가 정해진 값은 문자열을 직접 반복하지 않고 `TextChoices`를 사용합니다.

```python
class GameStatus(models.TextChoices):
    WAITING = "WAITING", "대기"
    PLAYING = "PLAYING", "진행 중"
    FINISHED = "FINISHED", "종료"
```

---

### 12. 테스트 규칙

게임 핵심 로직은 반드시 테스트 코드를 작성합니다.

최소 테스트 대상:

* 공격 성공 및 실패
* 반격 성공 및 실패
* 잘못된 카드 사용
* 자신의 턴이 아닐 때 요청
* 이미 종료된 게임 접근
* 승패 결정
* 전적 저장
* 비로그인 사용자 접근 제한

전체 테스트 실행:

```bash
python manage.py test
```

게임 앱 테스트 실행:

```bash
python manage.py test games
```

특정 테스트 파일 실행:

```bash
python manage.py test games.tests.test_attack
```

PR을 올리기 전에 관련 테스트를 실행하고 결과를 PR에 작성합니다.

---

### 13. 환경변수 및 보안 규칙

`.env` 파일은 절대 Git에 올리지 않습니다.

```gitignore
.env
```

공유가 필요한 환경변수 이름은 `.env.example`에 작성합니다.

```env
SECRET_KEY=
DEBUG=
SOCIAL_AUTH_CLIENT_ID=
SOCIAL_AUTH_SECRET=
```

`.env.example`에는 실제 비밀번호, Secret Key, API Key를 작성하지 않습니다.

설정값은 `settings.py`에 직접 입력하지 않고 환경변수로 관리합니다.

---

### 14. 파일 수정 전 팀원 확인

다음 파일은 프로젝트 전체에 영향을 줄 수 있으므로 수정 전 팀 채널에 공유합니다.

```text
config/settings.py
config/urls.py
core/templates/base.html
static/css/base.css
static/css/components.css
accounts/models.py
games/models.py
requirements.txt
```

같은 파일을 여러 명이 동시에 수정해야 한다면 수정 범위와 담당 부분을 먼저 나눕니다.

---

### 15. 공통 완료 기준

기능은 코드를 작성한 것만으로 완료 처리하지 않습니다.

다음 조건을 모두 만족해야 완료된 것으로 판단합니다.

* 정상적인 상황에서 기능이 동작함
* 잘못된 요청을 처리함
* 비로그인 및 권한 없는 사용자를 처리함
* 화면 깨짐이 없음
* 기존 기능에 영향을 주지 않음
* 테스트를 완료함
* 불필요한 코드가 제거됨
* PR 리뷰가 완료됨
