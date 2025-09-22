"""
FastAPI应用配置模块

依据文档：《技术架构设计》配置管理规范
模块功能：统一配置管理、环境变量处理、应用设置
版本：V1.0
创建日期：2025-09-20
"""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """应用程序配置设置"""
    
    # 基础配置
    APP_NAME: str = Field(default="数据工作流自动化API", description="应用程序名称")
    VERSION: str = Field(default="1.0.0", description="版本号")
    DEBUG: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    HOST: str = Field(default="127.0.0.1", description="服务器主机地址")
    PORT: int = Field(default=8000, description="服务器端口")
    WORKERS: int = Field(default=4, description="工作进程数")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="密钥")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间(分钟)")
    ALGORITHM: str = Field(default="HS256", description="JWT算法")
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="允许的跨域源"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="允许的主机"
    )
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./workspace/database/app.db",
        description="数据库连接URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="数据库SQL日志")
    
    # Redis配置
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis密码")
    
    # Celery配置
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", description="Celery代理URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", description="Celery结果后端")
    
    # 文件配置
    UPLOAD_MAX_SIZE: int = Field(default=100 * 1024 * 1024, description="最大上传文件大小(字节)")  # 100MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".xlsx", ".xls", ".csv", ".json", ".txt", ".pdf"],
        description="允许上传的文件扩展名"
    )
    WORKSPACE_PATH: str = Field(default="./workspace", description="工作区路径")
    TEMP_PATH: str = Field(default="./workspace/temp", description="临时文件路径")
    
    # 性能配置
    MAX_CONCURRENT_TASKS: int = Field(default=10, description="最大并发任务数")
    REQUEST_TIMEOUT: int = Field(default=300, description="请求超时时间(秒)")
    MAX_MEMORY_MB: int = Field(default=2048, description="最大内存使用(MB)")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    LOG_FILE: Optional[str] = Field(default=None, description="日志文件路径")
    
    # 监控配置
    ENABLE_METRICS: bool = Field(default=True, description="启用指标收集")
    METRICS_PORT: int = Field(default=8001, description="指标服务端口")
    
    # 开发配置
    RELOAD_ON_CHANGE: bool = Field(default=False, description="文件变更时重载")
    API_DOCS_ENABLED: bool = Field(default=True, description="启用API文档")
    
    # 中间件配置
    ENABLE_REQUEST_LOGGING: bool = Field(default=True, description="启用请求日志")
    ENABLE_SECURITY_HEADERS: bool = Field(default=True, description="启用安全头部")
    ENABLE_RATE_LIMITING: bool = Field(default=False, description="启用限流")
    RATE_LIMIT_CALLS: int = Field(default=100, description="限流调用次数")
    RATE_LIMIT_PERIOD: int = Field(default=3600, description="限流时间窗口(秒)")
    MAX_REQUEST_SIZE: int = Field(default=10 * 1024 * 1024, description="最大请求大小")
    ENABLE_COMPRESSION: bool = Field(default=True, description="启用响应压缩")
    COMPRESSION_MINIMUM_SIZE: int = Field(default=1024, description="压缩最小大小")
    
    # 属性别名，用于向后兼容
    @property
    def debug(self) -> bool:
        return self.DEBUG
    
    @property
    def host(self) -> str:
        return self.HOST
    
    @property
    def port(self) -> int:
        return self.PORT
    
    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def enable_request_logging(self) -> bool:
        return self.ENABLE_REQUEST_LOGGING
    
    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL
    
    @property
    def enable_security_headers(self) -> bool:
        return self.ENABLE_SECURITY_HEADERS
    
    @property
    def enable_rate_limiting(self) -> bool:
        return self.ENABLE_RATE_LIMITING
    
    @property
    def rate_limit_calls(self) -> int:
        return self.RATE_LIMIT_CALLS
    
    @property
    def rate_limit_period(self) -> int:
        return self.RATE_LIMIT_PERIOD
    
    @property
    def max_request_size(self) -> int:
        return self.MAX_REQUEST_SIZE
    
    @property
    def enable_compression(self) -> bool:
        return self.ENABLE_COMPRESSION
    
    @property
    def compression_minimum_size(self) -> int:
        return self.COMPRESSION_MINIMUM_SIZE
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        """验证密钥强度"""
        if len(v) < 32:
            logger.warning("密钥长度少于32字符，建议使用更强的密钥")
        return v
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_origins(cls, v):
        """验证跨域源配置"""
        if "*" in v:
            logger.warning("允许所有跨域源，生产环境请配置具体域名")
        return v
    
    @field_validator("WORKSPACE_PATH", "TEMP_PATH")
    @classmethod
    def validate_paths(cls, v):
        """验证路径配置"""
        if not os.path.isabs(v):
            # 转换为绝对路径
            v = os.path.abspath(v)
        
        # 确保目录存在
        os.makedirs(v, exist_ok=True)
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是: {', '.join(valid_levels)}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DevelopmentSettings(Settings):
    """开发环境配置"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_ECHO: bool = True
    RELOAD_ON_CHANGE: bool = True
    
    class Config:
        env_prefix = "DEV_"

class ProductionSettings(Settings):
    """生产环境配置"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_ECHO: bool = False
    API_DOCS_ENABLED: bool = False
    
    class Config:
        env_prefix = "PROD_"

class TestSettings(Settings):
    """测试环境配置"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///:memory:"
    REDIS_URL: str = "redis://localhost:6379/15"  # 使用测试数据库
    LOG_LEVEL: str = "WARNING"
    
    class Config:
        env_prefix = "TEST_"

@lru_cache()
def get_settings() -> Settings:
    """获取应用配置(缓存)"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        logger.info("使用生产环境配置")
        return ProductionSettings()
    elif env == "test":
        logger.info("使用测试环境配置")
        return TestSettings()
    else:
        logger.info("使用开发环境配置")
        return DevelopmentSettings()

def get_database_url() -> str:
    """获取数据库连接URL"""
    settings = get_settings()
    return settings.DATABASE_URL

def get_redis_url() -> str:
    """获取Redis连接URL"""
    settings = get_settings()
    return settings.REDIS_URL

def configure_logging():
    """配置应用程序日志"""
    settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        filename=settings.LOG_FILE,
        filemode='a' if settings.LOG_FILE else None
    )
    
    # 配置特定模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    if settings.DEBUG:
        logging.getLogger("src").setLevel(logging.DEBUG)
    
    logger.info(f"日志配置完成，级别: {settings.LOG_LEVEL}")

# 导出配置实例
settings = get_settings()

# 应用启动时配置日志
configure_logging()
