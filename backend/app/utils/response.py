"""Consistent API response helpers."""

from flask import jsonify


class ApiError(Exception):
    """A business-logic error mapped to an HTTP response."""

    def __init__(self, message, error_code="ERROR", status=400, data=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status = status
        self.data = data


def api_success(message="Success", data=None, status=200, meta=None):
    """Standard success envelope."""
    payload = {"success": True, "message": message, "data": data if data is not None else {}}
    if meta:
        payload["meta"] = meta
    return jsonify(payload), status


def api_error(message, error_code="ERROR", status=400, data=None):
    """Standard error envelope."""
    payload = {"success": False, "message": message, "error_code": error_code}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status