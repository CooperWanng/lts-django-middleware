# coding=utf-8
from .base import BaseMiddleware
from django.conf import settings
from django.http import JsonResponse
import traceback
import uuid
import logging
import json

"""
捕获视图函数异常并且同一处理的的中间件

settings配置参数:
VIEW_EXCEPTION_LOGGER    type logger object     日志handle对象
VIEW_EXCEPTION_RESPONSE  type response object   捕获异常后所返回给用户的response
"""


class ViewExceptionMiddleware(BaseMiddleware):

    def get_default_logger(self):
        return logging.getLogger()

    def catch_request_log(self, logger, request):
        logger.error("URL:{}".format(request.path))
        logger.error("METHOD:{}".format(request.method))
        logger.error("PARAMS:{}".format(json.dumps(dict(request.GET))))
        logger.error("FORM_DATA:{}".format(json.dumps(dict(request.POST))))
        logger.error("BODY:{}".format(str(request.body.decode())))
        logger.error("HEADERS:{}".format(json.dumps(dict(request.headers))))


    def process_exception(self, request, exception):
        logger = getattr(settings, "VIEW_EXCEPTION_LOGGER", self.get_default_logger())
        response = getattr(settings, "VIEW_EXCEPTION_RESPONSE", JsonResponse({"code": 400, "message": "服务异常"}))

        exception_code = str(uuid.uuid4())
        logger.error("ViewExceptionMiddleware code:{}".format(exception_code))
        logger.error(traceback.format_exc())

        try:
            self.catch_request_log(logger, request)
        except:
            logger.error(traceback.format_exc())

        self.set_data_to_response(response, {self.__class__.__name__: exception_code})

        return response
