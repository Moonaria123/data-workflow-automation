"""
FastAPI后端架构 - 主应用程序入口

依据文档：《开发计划与实施方案》第7-12周后端服务开发
技术架构：FastAPI + SQLAlchemy + Redis + Celery
版本：V1.0
创建日期：2025-09-20
更新日期：2025-01-12
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import uvicorn

from .core.config import get_settings
from .core.database import get_database, create_tables
from .core.auth import get_auth_manager
from .core.middleware import setup_middlewares
from .core.exceptions import APIException, ValidationException
from .routes import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动数据工作流自动化API服务...")
    
    # 初始化数据库连接
    try:
        db_manager = get_database()
        await db_manager.connect()
        logger.info("✅ 数据库连接成功")
        
        # 创建数据库表
        await create_tables()
        logger.info("✅ 数据库表创建/检查完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    
    # 初始化身份认证系统
    try:
        auth_manager = get_auth_manager()
        await auth_manager.initialize()
        logger.info("✅ 身份认证系统初始化完成")
    except Exception as e:
        logger.error(f"❌ 身份认证系统初始化失败: {e}")
        logger.info("⚠️ 继续启动但认证功能可能受限")
    
    logger.info("🎯 API服务启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🔄 正在关闭API服务...")
    
    try:
        db_manager = get_database()
        await db_manager.disconnect()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 数据库关闭失败: {e}")
    
    logger.info("👋 API服务已关闭")

def create_app() -> FastAPI:
    """创建并配置FastAPI应用实例"""
    
    app = FastAPI(
        title="数据工作流自动化API",
        description="基于FastAPI的数据处理工作流自动化平台后端服务",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 设置中间件
    setup_middlewares(app, settings)
    
    # 注册路由
    app.include_router(api_router)
    
    # 全局异常处理器
    @app.exception_handler(APIException)
    async def api_exception_handler(request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "detail": exc.detail,
                "error_code": exc.error_code,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request, exc: ValidationException):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "message": "数据验证失败",
                "detail": exc.errors,
                "error_code": "VALIDATION_ERROR",
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(HTTPException)  
    async def http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "error_code": "HTTP_ERROR",
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "服务器内部错误",
                "error_code": "INTERNAL_ERROR",
                "timestamp": time.time()
            }
        )
    
    # 健康检查端点
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "service": "数据工作流自动化API",
            "version": "1.0.0",
            "timestamp": time.time()
        }
    
    # 服务信息端点
    @app.get("/info", tags=["系统信息"])
    async def service_info():
        """服务信息端点"""
        return {
            "service": "数据工作流自动化API",
            "version": "1.0.0",
            "description": "基于FastAPI的高性能数据处理工作流自动化平台",
            "features": [
                "数据处理引擎API",
                "工作流管理服务",
                "用户认证与权限控制",
                "实时任务监控",
                "文件管理服务"
            ],
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "api": "/api/v1"
            },
            "environment": settings.environment,
            "debug": settings.debug
        }
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    # 开发环境直接运行
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else 4
    )