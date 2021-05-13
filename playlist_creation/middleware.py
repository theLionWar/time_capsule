from social_django.middleware import SocialAuthExceptionMiddleware


class SocialAuthExceptionNotRaiseMiddleware(SocialAuthExceptionMiddleware):
    def raise_exception(self, request, exception):
        strategy = getattr(request, 'social_strategy', None)
        if strategy is not None:
            return strategy.setting('RAISE_EXCEPTIONS')
