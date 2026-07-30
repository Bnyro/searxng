# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ecosia"""

import typing as t
from urllib.parse import urlencode

from searx.result_types import EngineResults

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams

about = {
    "website": "https://www.ecosia.org",
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
}

paging = True
safesearch = True
enable_http2 = False

categories = ["general"]
ecosia_categ = "search"
"""Category to search in. Can be either "search" or "images"."""


base_url = "https://www.ecosia.org"
safe_search_map = {0: "n", 1: "i", 2: "y"}

page_size = 24


def init(_):
    if ecosia_categ not in ("search", "images"):
        raise ValueError("invalid search type: %s" % ecosia_categ)


def request(query: str, params: "OnlineParams") -> None:
    args = {
        "q": query,
        "p": params["pageno"] - 1,
        "offset": (params["pageno"] - 1) * page_size,
    }
    if params["time_range"]:
        args["freshness"] = params["time_range"]

    ecfg = {"f": safe_search_map[params["safesearch"]]}

    params["cookies"]["ECFG"] = ":".join(f"{key}={value}" for (key, value) in ecfg.items())

    params["url"] = f"{base_url}/{ecosia_categ}?{urlencode(args)}"

    # "Content-Type": "application/json" forces a JSON response, only works for general and image results
    params["headers"].update({"Referer": f"{base_url}/", "Content-Type": "application/json", "Sec-GPC": "1"})


def response(resp: "SXNG_Response"):
    res = EngineResults()

    json_resp = resp.json()
    if ecosia_categ == "search":
        for result in json_resp["mainline"]:
            if not result.get("url"):  # advertisement
                continue
            res.add(res.types.MainResult(url=result["url"], title=result["title"], content=result["description"]))

        for suggestion in json_resp["relatedQueries"]:
            res.add(res.types.LegacyResult(suggestion=suggestion))
    elif ecosia_categ == "images":
        for result in json_resp["mainline"]:
            res.add(
                res.types.Image(
                    url=result["sourceUrl"],
                    title=result["title"],
                    img_src=result["imageUrl"],
                    thumbnail_src=result["thumbnailUrl"],
                    resolution=f"{result['width']}x{result['height']}",
                    img_format=result["format"],
                )
            )

    return res
