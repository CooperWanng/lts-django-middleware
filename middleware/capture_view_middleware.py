# coding=utf-8
from .base import BaseMiddleware
from django.conf import settings
import time

"""
获取视图函数执行时间
"""


class CaptureViewExecTimeMiddleware(BaseMiddleware):
    init_view_timestamp = "_init_view_timestamp"

    def set_elapsed_field(self, request):
        setattr(request, self.init_view_timestamp, time.time())

    def get_elapsed_field(self, request):
        if hasattr(request, self.init_view_timestamp):
            return getattr(request, self.init_view_timestamp)
        if hasattr(request._request, self.init_view_timestamp):
            return getattr(request._request, self.init_view_timestamp)
        return

    def process_request(self, request):
        if settings.DEBUG is True:
            self.set_elapsed_field(request)

    def process_response(self, request, response):
        if settings.DEBUG is True:
            init_time = self.get_elapsed_field(request)
            if init_time:
                total_cost = time.time() - init_time
                self.set_data_to_response(response, {self.__class__.__name__: total_cost})

        return response
