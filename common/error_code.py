from enum import Enum


class ErrorCode(Enum):
    # Part 1: Common Error Code
    SUCCESS = (200, "Success")  # HTTP 200 OK

    PARAM_ERROR = (1400, "Param error")  # HTTP 400 Bad Request
    NO_AVAILABLE_APIKEY_ERROR = (1401, "No Available Apikey")  # HTTP 401 Unauthorized
    PERMISSION_DENIED = (1403, "Permission denied")  # HTTP 403 Forbidden
    OPERATION_NOT_ALLOWED = (1405, "Operation Not Allowed")  # HTTP 405 Method Not Allowed
    OPERATION_TIMED_OUT = (1408, "Operation timed out")  # HTTP 408 Request Timeout

    INTERNAL_SERVER_ERROR = (1500, "Internal Server Error")  # HTTP 500 Internal Server Error
    UNKNOWN_ERROR = (1520, "Unknown error")  # HTTP 520 Unknown Error (Commonly used in some APIs)

    # Part 2: Business Error Code
    PLATFORM_NOT_SUPPORT = (2201, "Platform not support")
    LINK_NOT_PARSED = (2202, "Link not parsed")
    RESOURCE_EXISTING = (2203, "Resource existing")
    INSERT_RESOURCE_FAILED = (2204, "Insert resource failed")

    def __init__(self, code, message):
        self.code = code
        self.message = message
