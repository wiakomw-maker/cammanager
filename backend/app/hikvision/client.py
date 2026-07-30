from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree

import httpx


def _tag_name(element: ElementTree.Element) -> str:
    return element.tag.rsplit("}", maxsplit=1)[-1]


def _text(element: ElementTree.Element, name: str) -> str | None:
    for child in element.iter():
        if _tag_name(child) == name and child.text:
            return child.text.strip()
    return None


def _as_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _as_float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


@dataclass(frozen=True)
class HikvisionConnection:
    host: str
    port: int
    username: str
    password: str
    https: bool


class HikvisionClient:
    """Small ISAPI client for Hikvision recorders; no vendor abstraction is intentional."""

    def __init__(self, connection: HikvisionConnection, *, verify_tls: bool, timeout_seconds: float) -> None:
        scheme = "https" if connection.https else "http"
        self._base_url = f"{scheme}://{connection.host}:{connection.port}/ISAPI"
        self._client = httpx.AsyncClient(
            auth=httpx.DigestAuth(connection.username, connection.password),
            verify=verify_tls,
            timeout=timeout_seconds,
        )

    async def __aenter__(self) -> HikvisionClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()

    async def _get_xml(self, path: str) -> ElementTree.Element:
        response = await self._client.get(f"{self._base_url}{path}", headers={"Accept": "application/xml"})
        response.raise_for_status()
        return ElementTree.fromstring(response.content)

    async def _send_xml(self, method: str, path: str, root: ElementTree.Element) -> None:
        response = await self._client.request(
            method,
            f"{self._base_url}{path}",
            content=ElementTree.tostring(root, encoding="utf-8", xml_declaration=True),
            headers={"Content-Type": "application/xml", "Accept": "application/xml"},
        )
        response.raise_for_status()

    async def device_info(self) -> dict[str, str | None]:
        root = await self._get_xml("/System/deviceInfo")
        return {
            "model": _text(root, "model"),
            "serial": _text(root, "serialNumber") or _text(root, "serialNo"),
            "firmware": _text(root, "firmwareVersion"),
        }

    async def system_status(self) -> str:
        root = await self._get_xml("/System/status")
        value = (_text(root, "deviceStatus") or _text(root, "status") or "online").lower()
        return "online" if value in {"online", "ok", "1", "true"} else value

    async def storage_info(self) -> dict[str, int | str | None]:
        root = await self._get_xml("/ContentMgmt/Storage")
        total = _as_int(_text(root, "totalCapacity") or _text(root, "capacity"))
        free = _as_int(_text(root, "freeSpace") or _text(root, "freeCapacity"))
        return {"status": _text(root, "status") or _text(root, "hddStatus"), "total": total, "free": free}

    async def temperature(self) -> float | None:
        root = await self._get_xml("/System/status")
        for element in root.iter():
            if _tag_name(element).lower() in {"temperature", "temperaturecelsius"}:
                return _as_float(element.text.strip() if element.text else None)
        return None

    async def input_channels(self) -> list[dict[str, Any]]:
        root = await self._get_xml("/ContentMgmt/InputProxy/channels")
        channels: list[dict[str, Any]] = []
        for element in root.iter():
            if _tag_name(element) not in {"InputProxyChannel", "VideoInputChannel"}:
                continue
            channel = _as_int(_text(element, "id"))
            if channel is None:
                continue
            channels.append(
                {
                    "channel": channel,
                    "name": _text(element, "name") or f"Camera {channel}",
                    "model": _text(element, "model"),
                    "serial": _text(element, "serialNumber") or _text(element, "serialNo"),
                    "ip": _text(element, "ipAddress"),
                    "mac": _text(element, "macAddress"),
                    "firmware": _text(element, "firmwareVersion"),
                    "online": False,
                    "status": "unknown",
                }
            )
        results = await asyncio.gather(
            *(self.input_channel_status(channel["channel"]) for channel in channels),
            return_exceptions=True,
        )
        for channel, result in zip(channels, results, strict=True):
            if isinstance(result, Exception):
                continue
            channel["online"] = result
            channel["status"] = "online" if result else "offline"
        return channels

    async def input_channel_status(self, channel: int) -> bool:
        root = await self._get_xml(f"/ContentMgmt/InputProxy/channels/{channel}/status")
        online = (_text(root, "online") or "false").lower()
        return online in {"true", "online", "1"}

    async def snapshot(self, channel: int) -> tuple[bytes, str]:
        stream_channel = channel * 100 + 1
        response = await self._client.get(f"{self._base_url}/Streaming/channels/{stream_channel}/picture")
        response.raise_for_status()
        return response.content, response.headers.get("content-type", "image/jpeg")

    async def users(self) -> list[dict[str, str | None]]:
        root = await self._get_xml("/Security/users")
        users: list[dict[str, str | None]] = []
        for element in root.iter():
            if _tag_name(element) != "User":
                continue
            username = _text(element, "userName")
            if username:
                users.append({"id": _text(element, "id"), "username": username, "level": _text(element, "userLevel")})
        return users

    async def create_user(self, username: str, password: str, user_level: str) -> None:
        root = ElementTree.Element("User", xmlns="http://www.hikvision.com/ver20/XMLSchema")
        ElementTree.SubElement(root, "userName").text = username
        ElementTree.SubElement(root, "password").text = password
        ElementTree.SubElement(root, "userLevel").text = user_level
        await self._send_xml("POST", "/Security/users", root)
