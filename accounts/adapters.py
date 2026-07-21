from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class KakaoSocialAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        # 카카오 응답에서 nickname 꺼내기
        extra = sociallogin.account.extra_data or {}
        kakao_account = extra.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        nickname = profile.get("nickname") or f"kakao_{sociallogin.account.uid}"

        user.nickname = nickname

        # username은 유니크해야 하는데 카카오는 username을 안 줘서 uid로 만듦
        if not user.username:
            user.username = f"kakao_{sociallogin.account.uid}"

        return user