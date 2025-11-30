import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.http import HTTPBasic, HTTPBasicCredentials

from hgf.constants import Config
from hgf.rpc.api_server.deps import get_config

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

router_login = APIRouter()

def verify_auth(api_config, username: str, password: str):
    """Verify username/password"""
    return secrets.compare_digest(username, api_config.get("username")) and secrets.compare_digest(
        password, api_config.get("password")
    )