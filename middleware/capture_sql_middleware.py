# coding=utf-8
from .base import BaseMiddleware
from django.db import connections
from django.conf import settings

"""
获取本次请求所执行的数据库dml语句及其消耗
仅在 DEBUG = True 时生效
中间件会在相应中添加一个同类名的key,值为一个字典
字典中每个key为数据链接别名，值包含所有sql明细以及总消耗
"""


class CaptureSQLMiddleware(BaseMiddleware):
    dml_prefix = ['select', 'insert', 'update', 'delete']

    def get_connection_dml_sql(self, connection):
        all_sql = connection.queries
        total_cost = 0
        result = []
        exec_num = 1
        for sql_info in all_sql:
            if sql_info['sql'].split(' ')[0].lower() in self.dml_prefix:
                sql_info['exec_num'] = exec_num
                sql_info['time'] = float(sql_info['time'])
                result.append(sql_info)
                exec_num += 1
                total_cost += float(sql_info['time'])
        for item in result:
            item['rate'] = str(round(item['time'] / total_cost, 4) * 100) + '%' if total_cost else '0%'
        return result, total_cost

    def get_all_dml_sql(self):
        result = {}
        for conn in connections:
            queries, total_cost = self.get_connection_dml_sql(connections[conn])
            result[conn] = {
                "queries": queries,
                "total_cost": total_cost
            }
        return result

    def process_response(self, request, response):
        if settings.DEBUG is False:
            return response

        result = self.get_all_dml_sql()
        self.set_data_to_response(response, {self.__class__.__name__: result})

        return response
