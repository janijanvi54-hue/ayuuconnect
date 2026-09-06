"""Global error handlers.

Errors are logged server-side; clients only ever receive generic, safe
messages. Stack traces are never returned to end users.
"""

from flask import jsonify

from .response import ApiError


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify(
            {
                "success": False,
                "message": error.message,
                "error_code": error.error_code,
            }
        ), error.status

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify(
            {"success": False, "message": "Resource not found", "error_code": "NOT_FOUND"}
        ), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify(
            {
                "success": False,
                "message": "Method not allowed",
                "error_code": "METHOD_NOT_ALLOWED",
            }
        ), 405

    @app.errorhandler(413)
    def handle_payload_too_large(_error):
        return jsonify(
            {
                "success": False,
                "message": "Request payload too large",
                "error_code": "PAYLOAD_TOO_LARGE",
            }
        ), 413

    @app.errorhandler(Exception)
    def handle_unhandled(error):
        app.logger.error("Unhandled exception", exc_info=error)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error",
                "error_code": "SERVER_ERROR",
            }
        ), 500