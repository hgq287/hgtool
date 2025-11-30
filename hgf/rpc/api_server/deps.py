from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from fastapi import Depends, HTTPException

from hgf.constants import Config
from hgf.rpc.api_server.webserver import ApiServer

def get_config() -> dict[str, Any]:
  return ApiServer._config