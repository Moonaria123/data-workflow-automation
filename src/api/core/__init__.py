"""
API核心模块初始化

依据文档：《系统架构设计文档》模块组织规范
功能：核心模块导入、配置管理、依赖注入
版本：V1.0
创建日期：2025-09-20
"""

# 配置管理
from .config import (
    Settings,
    DevelopmentSettings,
    ProductionSettings,
    TestSettings,
    get_settings,
    get_database_url,
    get_redis_url,
    configure_logging,
)

# 数据库管理
from .database import (
    DatabaseManager,
    get_database,
    create_tables,
    drop_tables,
    init_database,
    cleanup_database,
)

# 认证管理
from .auth import (
    AuthManager,
    get_auth_manager,
    create_access_token,
    verify_password,
    hash_password,
)

# 异常处理
from .exceptions import (
    APIException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ResourceConflictException,
    BusinessLogicException,
    ExternalServiceException,
    RateLimitException,
    FileUploadException,
    WorkflowException,
    NodeExecutionException,
    DataProcessingException,
    ConfigurationException,
    DatabaseException,
    CacheException,
    ERROR_CODE_MAPPING,
    get_error_message,
    create_http_exception,
)

# 依赖注入
from .dependencies import (
    get_db_session,
    get_request_id,
    get_current_user,
    get_current_user_optional,
    require_permissions,
    require_roles,
    require_admin,
    require_user_management,
    require_workflow_read,
    require_workflow_write,
    require_workflow_execute,
    require_workflow_admin,
    require_data_read,
    require_data_write,
    require_data_delete,
    require_data_admin,
    require_system_read,
    require_system_admin,
    PaginationParams,
    get_pagination_params,
    SearchParams,
    get_search_params,
    check_workflow_ownership,
    get_logger,
    get_config,
    check_database_health,
    check_auth_health,
    RequestContext,
    get_request_context,
)

# 中间件
from .middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    ExceptionHandlingMiddleware,
    CORSMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestSizeMiddleware,
    ResponseCompressionMiddleware,
    setup_middlewares,
)

__all__ = [
    # 配置管理
    "Settings",
    "DevelopmentSettings",
    "ProductionSettings",
    "TestSettings",
    "get_settings",
    "get_database_url",
    "get_redis_url",
    "configure_logging",

    # 数据库管理
    "DatabaseManager",
    "get_database",
    "create_tables",
    "drop_tables",
    "init_database",
    "cleanup_database",
    
    # 认证管理
    "AuthManager",
    "get_auth_manager",
    "create_access_token",
    "verify_password",
    "hash_password",
    
    # 异常处理
    "APIException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ResourceConflictException",
    "BusinessLogicException",
    "ExternalServiceException",
    "RateLimitException",
    "FileUploadException",
    "WorkflowException",
    "NodeExecutionException",
    "DataProcessingException",
    "ConfigurationException",
    "DatabaseException",
    "CacheException",
    "ERROR_CODE_MAPPING",
    "get_error_message",
    "create_http_exception",
    
    # 依赖注入
    "get_db_session",
    "get_request_id",
    "get_current_user",
    "get_current_user_optional",
    "require_permissions",
    "require_roles",
    "require_admin",
    "require_user_management",
    "require_workflow_read",
    "require_workflow_write",
    "require_workflow_execute",
    "require_workflow_admin",
    "require_data_read",
    "require_data_write",
    "require_data_delete",
    "require_data_admin",
    "require_system_read",
    "require_system_admin",
    "PaginationParams",
    "get_pagination_params",
    "SearchParams",
    "get_search_params",
    "check_workflow_ownership",
    "get_logger",
    "get_config",
    "check_database_health",
    "check_auth_health",
    "RequestContext",
    "get_request_context",
    
    # 中间件
    "RequestIDMiddleware",
    "RequestLoggingMiddleware",
    "ExceptionHandlingMiddleware",
    "CORSMiddleware",
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware",
    "RequestSizeMiddleware",
    "ResponseCompressionMiddleware",
    "setup_middlewares",
]
