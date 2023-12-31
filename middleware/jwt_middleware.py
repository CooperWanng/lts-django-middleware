# coding=utf-8
from .base import BaseMiddleware
from django.http import JsonResponse
from django.conf import settings
from .util import jwt_token_validate, LtsUser
import re
import time

"""
中间件功能：
获取jwt，
优先解析jwt，jwt解析成功，请求放行，并且对当前request设置用户属性,可在wsgi_request中获取lts_user属性获取用户信息
jwt解析失败，看url是否被设置无需登录态即可访问，如果未设置，请求驳回，如果设置，进一步校验LTS鉴权
LTS鉴权成功，请求放行，鉴权失败，请求驳回

LTS鉴权解释:
请求头中添加{LTS_VERIFY_KEY}，并且值以{LTS_VERIFY_VALUE_PREFIX}为开头，即认为通过了LTS鉴权

settings配置参数:
LOGIN_REQUIRED_URLS_EXCEPTIONS  type tuple 应用内无需认证的url正则匹配表达式，默认tuple()
LTS_VERIFY                      type bool  是否开启lts鉴权,若为False,LTS相关配置可不添加
LTS_VERIFY_KEY                  type str   lts鉴权请求头 默认为LUEPVERIFY
LTS_VERIFY_VALUE_PREFIX         type str   lts鉴权请求头值的开头 默认为internal_call
LTS_VERIFY_EXCEPTIONS           type tuple 无需进行LTS鉴权的url正则匹配表达式，默认tuple()
"""

__TOKEN_ERROR__ = "__TOKEN_ERROR__"


class LtsJwtVerifyMiddleware(BaseMiddleware):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expired_response = JsonResponse(data={'message': 'token expired'}, status=302)
        self.lts_check_response = JsonResponse(
            data={'code': 401, 'message': 'lts verify check failed', 'data': []}, status=401
        )

        self.app_exceptions = [re.compile(url) for url in self.get_config("LOGIN_REQUIRED_URLS_EXCEPTIONS", [])]
        self.lts_exceptions = [re.compile(url) for url in self.get_config("LTS_VERIFY_EXCEPTIONS", [])]

        self.lts_verify_key = self.get_config("LTS_VERIFY_KEY", "LUEPVERIFY")
        self.lts_verify_value_prefix = self.get_config("LTS_VERIFY_VALUE_PREFIX", "internal_call")

    def get_config(self, config_key, default):
        return getattr(settings, config_key, default)

    def is_exception(self, request, exception_list):
        try:
            for url in exception_list:
                if url.match(request.path):
                    return True
            return False
        except:
            return False

    def lts_check(self, request):
        lts_verify = self.get_config("LTS_VERIFY", False)
        if not lts_verify:
            return True

        if self.is_exception(request, self.lts_exceptions):
            return True

        if request.META.get("HTTP_" + self.lts_verify_key, '').lower().startswith(self.lts_verify_value_prefix):
            return True

        return False

    def get_jwt_token(self, request):
        req_auth = request.META.get('HTTP_AUTHORIZATION')
        req_cookie_jwt = request.COOKIES.get('jwt')
        req_url_jwt = request.GET.get('jwt')
        jwt_token = req_auth or req_url_jwt or req_cookie_jwt  # 有顺序的

        return jwt_token

    def parse_jwt_token(self, request, jwt_token):
        if jwt_token:
            try:
                payload, header = jwt_token_validate(jwt_token)
                if payload.get('exp') < int(time.time()):
                    return __TOKEN_ERROR__

                user = LtsUser(payload.get('username'), payload.get('uid'))
                setattr(request, "lts_user", user)
                return True
            except:
                return __TOKEN_ERROR__
        return False

    def process_request(self, request):

        jwt_token = self.get_jwt_token(request)
        token_check = self.parse_jwt_token(request, jwt_token)

        if token_check == __TOKEN_ERROR__:
            return self.expired_response

        if not token_check:
            is_exception = self.is_exception(request, self.app_exceptions)
            if not is_exception:
                return self.expired_response
            lts_check = self.lts_check(request)
            if not lts_check:
                return self.lts_check_response
