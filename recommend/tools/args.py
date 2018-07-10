# -*- coding=utf8 -*-
"""解析flask参数"""
import functools
import collections
from webargs.flaskparser import FlaskParser
from webargs.core import argmap2schema
from flask import jsonify


class ParamException(Exception):
    pass


class MessageParser(FlaskParser):
    """解决参数解析出错的时候直接返回PARAM_ERROR"""
    def use_args(self, argmap, req=None, locations=None, as_kwargs=False, validate=None):
        locations = locations or self.locations
        request_obj = req

        if isinstance(argmap, collections.Mapping):
            argmap = argmap2schema(argmap)()

        def decorator(func):
            req_ = request_obj

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                req_obj = req_

                # if as_kwargs is passed, must include all args
                force_all = as_kwargs

                if not req_obj:
                    req_obj = self.get_request_from_view_args(func, args, kwargs)
                # NOTE: At this point, argmap may be a Schema, or a callable
                try:
                    parsed_args = self.parse(
                        argmap, req=req_obj, locations=locations,
                        validate=validate, force_all=force_all)
                except ParamException:
                    return jsonify({'ret': -1, 'msg': 'params error'}), 400
                else:
                    if as_kwargs:
                        kwargs.update(parsed_args)
                        return func(*args, **kwargs)
                    else:
                        # Add parsed_args after other positional arguments
                        new_args = args + (parsed_args, )
                        return func(*new_args, **kwargs)
            wrapper.__wrapped__ = func
            return wrapper
        return decorator

parser = MessageParser()


@parser.error_handler
def handle_error(error):
    raise ParamException(error.messages)
