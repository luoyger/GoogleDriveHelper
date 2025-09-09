from typing import Optional, Dict
from pydantic import BaseModel

from common.error_code import ErrorCode


class BaseResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None

    def __init__(self, code: int, message: str, data: Optional[Dict] = None):
        super().__init__(code=code, message=message, data=data)

    @classmethod
    def success(cls, data: Optional[Dict] = None):
        return cls(code=ErrorCode.SUCCESS.code, message=ErrorCode.SUCCESS.message, data=data)

    @classmethod
    def error(cls, code: int, message: str):
        return cls(code=code, message=message)

    @classmethod
    def error_code(cls, error_code: ErrorCode):
        return cls(code=error_code.code, message=error_code.message)

    @classmethod
    def from_exception(cls, exception: Exception):
        return cls(code=500, message=str(exception))
