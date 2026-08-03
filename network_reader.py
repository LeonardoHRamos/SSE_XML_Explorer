"""Read and parse XML records from a configured Windows network share."""

from __future__ import annotations

import os
from pathlib import Path, PureWindowsPath
import subprocess

from dotenv import load_dotenv

load_dotenv()

from logger import logger
from utils.errors import CaminhoNaoEncontradoError, KNRNaoEncontradoError
from xml_parser import parse_sse_xml

AUTH_TIMEOUT_SECONDS = 15


class AuthenticationError(ConnectionError):
    """Raised when Windows cannot authenticate the configured network share."""


def _setting(name: str) -> str:
    return os.getenv(name, "").strip()


def _base_paths() -> list[str]:
    return [item.strip(" \\/") for item in _setting("XML_BASE_PATHS").split(";") if item.strip(" \\/")]


def authenticate_share(host: str, share: str, username: str, password: str) -> None:
    if not share:
        raise AuthenticationError("NETWORK_SHARE não foi configurado.")

    target = rf"\\{host}\{share}"
    command = ["net", "use", target, "/persistent:no"]
    input_text = None
    if username:
        command = ["net", "use", target, "*", f"/user:{username}", "/persistent:no"]
        input_text = f"{password}\n"

    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=AUTH_TIMEOUT_SECONDS,
            check=False,
            startupinfo=startupinfo,
        )
    except subprocess.TimeoutExpired as exc:
        raise AuthenticationError("A autenticação de rede excedeu o tempo limite.") from exc
    except OSError as exc:
        raise AuthenticationError("Não foi possível executar a autenticação de rede.") from exc

    if result.returncode != 0:
        logger.warning("Network authentication failed with exit code %s", result.returncode)
        raise AuthenticationError("Falha ao autenticar no compartilhamento de rede.")


def list_base_paths(host: str, share: str, base_paths: list[str]) -> list[Path]:
    accessible: list[Path] = []
    for base in base_paths:
        candidate = Path(str(PureWindowsPath(rf"\\{host}\{share}") / PureWindowsPath(base)))
        try:
            if candidate.is_dir():
                accessible.append(candidate)
        except OSError:
            continue
    if not accessible:
        raise CaminhoNaoEncontradoError("Nenhum caminho XML configurado está acessível.")
    return accessible


def find_xml_by_knr(base_paths: list[Path], knr: str) -> Path:
    for base_path in base_paths:
        try:
            for candidate in base_path.rglob("*.xml"):
                if knr in candidate.name:
                    return candidate
        except OSError:
            continue
    raise KNRNaoEncontradoError(f"KNR {knr} não encontrado.")


def consultar_knr(ip: str, knr: str) -> dict[str, str]:
    username = _setting("NETWORK_USERNAME")
    password = _setting("NETWORK_PASSWORD")
    share = _setting("NETWORK_SHARE")
    base_paths = _base_paths()
    if not base_paths:
        raise CaminhoNaoEncontradoError("XML_BASE_PATHS não foi configurado.")

    authenticate_share(ip, share, username, password)
    xml_path = find_xml_by_knr(list_base_paths(ip, share, base_paths), knr)
    data = parse_sse_xml(xml_path)
    data["xml_path"] = str(xml_path)
    logger.info("XML query completed successfully")
    return data
