import logging
from typing import Any

import orjson
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import JSONResponse 

from hgf.constants import Config

logger = logging.getLogger(__name__)

class FTJSONResponse(JSONResponse):
  media_type = "application/json"

  def render(self, content: Any) -> bytes:
    """
    Render the content to JSON format using orjson.

    :param content: The content to be rendered.
    :return: The rendered JSON bytes.
    """
    return orjson.dumps(content, option=orjson.OPT_SERIALIZE_NUMPY)

class ApiServer:
  """
  A class to represent an API web server.
  """

  __instance = None
  __initialized = False
  _config: Config = {}

  def __init__(self, config: Config, standalone: bool = False) -> None:
    """
    Initialize the ApiServer instance.

    :param host: The host of the web server.
    :param port: The port of the web server.
    """
    ApiServer._config = config
    if self.__initialized and (standalone or self._standalone):
      return
    self._standalone: bool = standalone
    self._server = None

    ApiServer.__initialized = True

    self.app = FastAPI(
      title="Hgf API",
      description="API for hgf",
      version="0.1.0",
      default_response_class=FTJSONResponse,
    )

    self.configure_app(self.app, self._config)

    self.start_api()

  def start_api(self):
    """
    Start the API server.
    """
    rest_ip = self._config["api_server"]["listen_ip_address"]
    rest_port = self._config["api_server"]["listen_port"]
    
    uvconfig = uvicorn.Config(
      self.app,
      port=rest_port,
      host=rest_ip,
      use_colors=False,
      log_config=None,
    )
    
    try:
      server = uvicorn.Server(uvconfig)
      server.run()
    except Exception as e:
      logging.error(f"Error starting server: {e}")
      raise
    finally:
      logging.info("Server stopped")

  def configure_app(self, app: FastAPI, config):
    """
    Configure the FastAPI application with the given configuration.

    :param app: The FastAPI application instance.
    :param config: The configuration to apply.
    """
    from hgf.rpc.api_server.api_v1 import router_public as api_v1_public

    app.include_router(api_v1_public, prefix="/api/v1")

    app.add_middleware(
      CORSMiddleware,
      allow_origins=config["api_server"].get("CORS_origins", []),
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )