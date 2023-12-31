from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import json

try:
    from rest_framework.response import Response
except ImportError:
    from django.http import JsonResponse as Response


class BaseMiddleware(MiddlewareMixin):

    def get_response_data(self, response):
        if isinstance(response, JsonResponse):
            return json.loads(response.content)
        if isinstance(response, Response):
            return getattr(response, 'data', {})

    def set_data_to_response(self, response, data):
        if isinstance(response, JsonResponse):
            origin_data = json.loads(response.content)
            if isinstance(origin_data, dict):
                origin_data.update(data)
            response.content = json.dumps(origin_data)
            return

        if isinstance(response, Response):
            res_data = getattr(response, 'data', {})
            res_data.update(data)
            setattr(response, 'data', res_data)
            response._is_rendered = False
            response.render()
            return
