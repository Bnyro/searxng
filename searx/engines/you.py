# SPDX-License-Identifier: AGPL-3.0-or-later
"""You (general)"""

import json
import typing as t

from searx.result_types import EngineResults
from searx.utils import html_to_text

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams

about = {
    "website": "https://you.com/",
    "official_api_documentation": "https://you.com/docs/welcome",
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
}
categories = ["general"]

base_url = "https://you.com"


def request(query: str, params: "OnlineParams") -> None:
    params["url"] = base_url
    params["headers"].update(
        {
            "Content-Type": "text/plain",
            "next-action": "40bb14456a4887272fa7b55413a0cb2823bc467759",
        }
    )

    params["method"] = "POST"
    params["json"] = [{"query": query}]  # pyright: ignore[reportGeneralTypeIssues]


def response(resp: "SXNG_Response") -> EngineResults:
    res = EngineResults()

    raw_json = resp.text.splitlines()[1].removeprefix("1:")
    result: dict[str, str]
    for result in json.loads(raw_json)["data"]["results"]:
        res.add(
            res.types.MainResult(
                url=result["url"],
                title=result["title"],
                content=html_to_text(result["description"]),
            )
        )

    return res
