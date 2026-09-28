import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Server

import settings

from src.shared.logger import logger
from .endpoints import main_router
from .utils import (
    validation_exception_handler,
    LoggingMiddleware,
    WebhookBypassMiddleware,
    http_exception_wrapper,
)

from src.shared.exceptions import (
    NotFoundException,
    MappingException,
    UniqueViolationException,
    ProductInUseException,
    CategoryNotEmptyException,
    InvalidCategoryParentException,
    InvalidProductPriceException,
    InvalidCartQuantityException,
    EmptyCartException,
    InsufficientStockException,
    ProductUnavailableException,
    InvalidOrderTransitionException,
    InvalidInitDataException,
    InitDataExpiredException,
    TokenException,
    NotAuthenticatedException,
    PermissionDeniedException,
)


class ServerFactory:
    def __init__(self, settings: settings.ServerSettings):
        self.settings = settings
        self.app = None
        self.server = None

    def create_server(self) -> Server:
        self.app = self._configure_app()
        self.server = self._configure_server()
        return self.server

    def _configure_app(self) -> FastAPI:
        app = FastAPI(
            title="Catalogue backend",
            version="1.0.0",
            exception_handlers={
                RequestValidationError: validation_exception_handler,
                NotFoundException: http_exception_wrapper(404),
                MappingException: http_exception_wrapper(400),
                UniqueViolationException: http_exception_wrapper(409),
                ProductInUseException: http_exception_wrapper(409),
                CategoryNotEmptyException: http_exception_wrapper(409),
                InvalidCategoryParentException: http_exception_wrapper(422),
                InvalidProductPriceException: http_exception_wrapper(422),
                InvalidCartQuantityException: http_exception_wrapper(422),
                EmptyCartException: http_exception_wrapper(409),
                InsufficientStockException: http_exception_wrapper(409),
                ProductUnavailableException: http_exception_wrapper(409),
                InvalidOrderTransitionException: http_exception_wrapper(409),
                InvalidInitDataException: http_exception_wrapper(401),
                InitDataExpiredException: http_exception_wrapper(401),
                TokenException: http_exception_wrapper(401),
                NotAuthenticatedException: http_exception_wrapper(401),
                PermissionDeniedException: http_exception_wrapper(403),
            },
            root_path="/api",
            docs_url="/docs" if self.settings.docs_enabled else None,
            redoc_url=None,
            openapi_url="/openapi.json" if self.settings.docs_enabled else None,
        )

        app.include_router(main_router)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.allowed_origins,
            allow_credentials=False,  # токен идёт в Authorization, cookie нет
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
        )
        app.add_middleware(
            LoggingMiddleware,
            logger=logger,
            log_request=True,
            log_response=True,
            max_body_length=4096,
        )
        app.add_middleware(WebhookBypassMiddleware)

        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

        return app

    def _configure_server(self) -> Server:
        uvicorn_config = uvicorn.Config(
            self.app,
            host=self.settings.host,
            port=self.settings.port,
            loop="asyncio",
            lifespan="auto",
            log_level="info",
            proxy_headers=True,
            forwarded_allow_ips=self.settings.forwarded_allow_ips,
        )
        return uvicorn.Server(uvicorn_config)
