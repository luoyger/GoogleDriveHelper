# -*- coding: utf-8 -*-
import uuid
from contextlib import asynccontextmanager
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from common.config_loader import GLOBAL_CONFIG
from common.consul_client import init_service_register_and_discovery, service_register_and_discovery_enabled, \
    deregister_service
from common.logger import UVICORN_LOGGING_CONFIG, logger, request_id_context
from common.pymysql_pool import init_pymysql_pool
from common.utils import generate_request_id
from router.router import router

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info("Application startup")


    if service_register_and_discovery_enabled():
        init_service_register_and_discovery()

    yield

    # 关闭事件
    logger.info("Application shutdown")
    if service_register_and_discovery_enabled():
        deregister_service()



class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 从到请求头获取request_id
        upstream_request_id = request.headers.get('X-Request-ID')
        if upstream_request_id is not None and upstream_request_id != '':
            request_id = upstream_request_id
        else:
            request_id = generate_request_id()
        request.state.request_id = request_id
        # 设置 contextvar
        request_id_context.set(request_id)
        response = await call_next(request)
        # 将 request_id 添加到响应头中，以便客户端跟踪
        response.headers['X-Request-ID'] = request_id
        return response


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(router)
app.include_router(api_router)
app.add_middleware(RequestIDMiddleware)


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)


if __name__ == "__main__":
    # 初始化数据库连接
    init_pymysql_pool()

    uvicorn.run(app, host="0.0.0.0", port=GLOBAL_CONFIG['port'], log_config=UVICORN_LOGGING_CONFIG)
