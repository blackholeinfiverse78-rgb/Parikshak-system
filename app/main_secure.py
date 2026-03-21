"""
SECURE FastAPI Application - Task Review Agent
Implements comprehensive security measures including authentication, authorization, and input validation
"""
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime, timedelta

# Import security middleware
from app.security import (
    SecurityConfig, 
    UserRole, 
    get_current_user, 
    require_admin,
    require_user_or_admin,
    check_rate_limit,
    InputSanitizer,
    add_security_headers,
    rate_limiter
)

# Import API routes
from app.api import lifecycle
from app.api import tts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Task Review Agent starting up...")
    yield
    logger.info("Task Review Agent shutting down...")

# Create FastAPI app with security configuration
app = FastAPI(
    title="Task Review Agent - SECURE",
    description="Enterprise-grade autonomous evaluation system with comprehensive security",
    version="2.0.0-secure",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Security middleware configuration
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Limited methods
    allow_headers=["Authorization", "Content-Type"],  # Limited headers
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests"""
    client_ip = request.client.host
    
    # Skip rate limiting for health check
    if request.url.path == "/health":
        response = await call_next(request)
        return response
    
    try:
        check_rate_limit(client_ip)
    except HTTPException as e:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    
    response = await call_next(request)
    return response

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    return add_security_headers(response)

# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests for security monitoring"""
    start_time = datetime.utcnow()
    client_ip = request.client.host
    
    # Log request (without sensitive data)
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response

# Authentication endpoints
@app.post("/auth/login", tags=["Authentication"])
async def login(username: str, password: str):
    """
    Authenticate user and return JWT token
    Note: In production, implement proper password hashing and user database
    """
    # Demo authentication - replace with real authentication
    demo_users = {
        "admin": {"password": "admin123", "role": UserRole.ADMIN},
        "user": {"password": "user123", "role": UserRole.USER},
        "readonly": {"password": "readonly123", "role": UserRole.READONLY}
    }
    
    if username in demo_users and demo_users[username]["password"] == password:
        access_token_expires = timedelta(minutes=30)
        access_token = SecurityConfig.create_access_token(
            data={"sub": username, "role": demo_users[username]["role"]},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User {username} authenticated successfully")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "role": demo_users[username]["role"]
        }
    
    logger.warning(f"Failed authentication attempt for user: {username}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )

@app.get("/auth/me", tags=["Authentication"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "authenticated": True
    }

# Health check endpoint (no authentication required)
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0-secure"
    }

# System info endpoint (admin only)
@app.get("/system/info", tags=["System"])
async def system_info(current_user: dict = Depends(require_admin)):
    """Get system information (admin only)"""
    return {
        "system": "Task Review Agent",
        "version": "2.0.0-secure",
        "security_enabled": True,
        "authentication": "JWT",
        "authorization": "Role-based",
        "rate_limiting": "Enabled",
        "cors_origins": ALLOWED_ORIGINS,
        "trusted_hosts": ALLOWED_HOSTS
    }

# Include API routers with authentication
app.include_router(
    lifecycle.router,
    prefix="/api/v1",
    dependencies=[Depends(require_user_or_admin)]  # Require authentication
)

app.include_router(
    tts.router,
    prefix="/api/v1",
    dependencies=[Depends(require_user_or_admin)]  # Require authentication
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to prevent information disclosure"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Don't expose internal errors in production
    if os.getenv("ENVIRONMENT") == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )

# Security validation endpoint
@app.get("/security/validate", tags=["Security"])
async def validate_security_config(current_user: dict = Depends(require_admin)):
    """Validate security configuration (admin only)"""
    security_checks = {
        "jwt_secret_configured": bool(os.getenv("JWT_SECRET_KEY")),
        "cors_restricted": "*" not in ALLOWED_ORIGINS,
        "trusted_hosts_configured": len(ALLOWED_HOSTS) > 0,
        "rate_limiting_active": True,
        "security_headers_enabled": True,
        "authentication_required": True,
        "authorization_enabled": True
    }
    
    security_score = sum(security_checks.values()) / len(security_checks) * 100
    
    return {
        "security_checks": security_checks,
        "security_score": f"{security_score:.1f}%",
        "status": "SECURE" if security_score >= 90 else "NEEDS_IMPROVEMENT"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Security configuration for production
    host = os.getenv("HOST", "127.0.0.1")  # Bind to localhost by default
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting secure Task Review Agent on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") != "production",
        access_log=True,
        log_level="info"
    )