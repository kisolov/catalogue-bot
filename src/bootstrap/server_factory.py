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

from src.shared.exceptions import NotFoundException, MappingException


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
            title="freedomvpn backend",
            version="1.0.0",
            exception_handlers={
                RequestValidationError: validation_exception_handler,
                NotFoundException: http_exception_wrapper(404),
                MappingException: http_exception_wrapper(400),
            },
            root_path="/api",
        )

        app.include_router(main_router)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
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
            forwarded_allow_ips="172.18.0.2,127.0.0.1,::1",
        )
        return uvicorn.Server(uvicorn_config)
