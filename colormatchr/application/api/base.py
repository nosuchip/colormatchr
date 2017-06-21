# -*- coding: utf-8 -*-

import json
from application.common import json_enc


def response_json(success=True, message=None, data=None, code=200, mimetype='application/json'):
    """Make API JSON response tuple `json, code, mimetype` like: {'success': False, 'message': '', 'data': {}}
    """
    response_data = {'success': success}

    if message is not None:
        response_data['message'] = message
    if data is not None:
        response_data['data'] = data

    return (
        json.dumps(response_data, cls=json_enc.ExtendedJSONEncoder),
        code,
        mimetype
    )


def response_ok(message='', data=None):
    """API call successful, result ready and returned"""
    return response_json(success=True, message=message, data=data)


def response_fail(message='', data=None):
    """API call unsuccessful, message should be provided"""
    return response_json(success=False, message=message, data=data)


def response_error(message='', data=None):
    """API call failed and cannot be processed"""
    return response_json(success=False, message=message, data=data, code=500)


def response_not_found(message='', data=None):
    """API call failed, resource not found"""
    return response_json(success=False, message=message, data=data, code=404)


def response_forbidden(message='', data=None):
    """API call failed, access denied"""
    return response_json(success=False, message=message, data=data, code=401)
