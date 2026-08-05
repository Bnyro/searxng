# SPDX-License-Identifier: AGPL-3.0-or-later
"""Talordata"""

import typing as t
from searx.result_types import EngineResults

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams

about = {
    "website": "https://www.talordata.com",
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
}

paging = True
safesearch = True

categories = ["general"]


base_url = "https://api.talordata.com"
safe_search_map = {0: "off", 1: "active", 2: "active"}

talordata_engine = "google"
page_size = 10


def request(query: str, params: "OnlineParams"):
    params["url"] = f"{base_url}/accounts/v1/serp/get_serp_data"
    params["method"] = "POST"
    params["data"] = {
        "engine": talordata_engine,
        "json": 2,
        "q": query,
        "device": "desktop",
        "safe": safe_search_map[params["safesearch"]],
        "num": page_size,
        "start": (params["pageno"] - 1) * page_size,
        "ai_overview": False,
        "no_cache": False,
    }


def response(resp: "SXNG_Response"):
    res = EngineResults()

    json_resp = resp.json()

    for result in json_resp["data"]["json"]["organic"]:
        res.add(
            res.types.MainResult(
                url=result["link"],
                title=result["title"],
                content=result["description"],
            )
        )

    return res
