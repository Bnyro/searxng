# SPDX-License-Identifier: AGPL-3.0-or-later
"""OceanHero: Search the web and save the oceans."""

import random
import string
import typing as t
from datetime import datetime
from urllib.parse import urlencode

from searx.utils import format_duration, html_to_text
from searx.result_types import EngineResults

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams

about = {
    "website": "https://oceanhero.today",
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
}

paging = True
safesearch = True

categories = ["general"]
oceanhero_categ = "search"
"""Category to search in. Can be either "search", "images", "videos" or "news"."""

page_size = 10

base_url = "https://oceanhero.today"
safe_search_map = {0: "Off", 1: "Moderate", 2: "Strict"}

_ALPHABET = string.ascii_letters + string.digits


def init(_):
    if oceanhero_categ not in ("search", "images", "videos", "news"):
        raise ValueError("invalid search type: %s" % oceanhero_categ)


def request(query: str, params: "OnlineParams") -> None:
    args = {
        "q": query,
        "safeSearch": safe_search_map[params["safesearch"]],
        "count": page_size,
        "offset": (params["pageno"] - 1) * page_size,
    }
    if params["searxng_locale"] != "all":
        args["mkt"] = params["searxng_locale"].lower()

    params["url"] = f"{base_url}/api/{oceanhero_categ}?{urlencode(args)}"
    params["headers"].update({"Referer": f"{base_url}/"})
    params["cookies"] = {"OH_USER_ID": "".join(random.choices(_ALPHABET, k=20))}


def _parse_length_to_seconds(length: str) -> int:
    """Parses strings of format PT1H4M18S to seconds."""
    length = length.removeprefix("PT")
    duration = 0
    for delim, mul in [("H", 3600), ("M", 60), ("S", 1)]:
        parts = length.split(delim, 1)
        if len(parts) == 2:
            value, length = parts
            duration += int(value) * mul

    return duration


def response(resp: "SXNG_Response"):
    res = EngineResults()

    json_resp = resp.json()

    if oceanhero_categ == "search":
        for result in json_resp["webPages"]["value"]:
            res.add(
                res.types.MainResult(
                    url=result["url"],
                    title=html_to_text(result["name"]),
                    content=html_to_text(result["snippet"]),
                )
            )
    elif oceanhero_categ == "news":
        for result in json_resp["value"]:
            res.add(
                res.types.MainResult(
                    url=result["url"],
                    title=html_to_text(result["name"]),
                    content=html_to_text(result["description"]),
                    thumbnail=result.get("image", {}).get("thumbnail", {}).get("contentUrl"),
                    publishedDate=datetime.fromisoformat(result["datePublished"]),
                )
            )
    elif oceanhero_categ == "videos":
        for result in json_resp["value"]:
            res.add(
                res.types.LegacyResult(
                    template="videos.html",
                    url=result["contentUrl"],
                    title=html_to_text(result["name"]),
                    content=html_to_text(result["description"]),
                    thumbnail=result.get("thumbnailUrl"),
                    publishedDate=datetime.fromisoformat(result["datePublished"]),
                    length=format_duration(_parse_length_to_seconds(result["duration"])),
                )
            )
    elif oceanhero_categ == "images":
        for result in json_resp["value"]:
            res.add(
                res.types.Image(
                    url=result["hostPageUrl"],
                    title=html_to_text(result["name"]),
                    img_src=result["contentUrl"],
                    thumbnail_src=result["thumbnailUrl"],
                    resolution=f"{result['width']}x{result['height']}",
                    img_format=result.get("encodingFormat"),
                    filesize=result.get("contentSize"),
                )
            )

    return res
