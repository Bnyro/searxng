# SPDX-License-Identifier: AGPL-3.0-or-later
"""You (general)"""

import json
import re
import typing as t

from searx.network import raise_for_httperror
from searx.enginelib import EngineCache
from searx.exceptions import SearxEngineAPIException
from searx.result_types import EngineResults
from searx.utils import eval_xpath_list, html_to_text
from searx.network import get

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

CACHE: EngineCache
# from testing, these are 43 or 44 hex chars
_NEXT_ACTION_RE = re.compile(r"\"([a-f0-9]{40,50})\"")


def setup(engine_settings: dict[str, str]):
    global CACHE  # pylint: disable=global-statement
    CACHE = EngineCache(engine_settings["name"])


def _get_next_action() -> str:
    cached_action: str | None
    if cached_action := CACHE.get("action"):
        return cached_action

    doc = get(base_url).html()
    script_src: str
    for script_src in eval_xpath_list(doc, "//script/@src"):
        script = get(base_url + script_src)
        # there are multiple next tokens that match the regex
        # the script we are looking for also contains an example JSON search response,
        # so we look for the results key in it
        if not '"results"' in script.text:
            continue

        if match := _NEXT_ACTION_RE.search(script.text):
            CACHE.set("action", match.group(1))
            return match.group(1)

    raise SearxEngineAPIException("failed to find next action")


def request(query: str, params: "OnlineParams") -> None:
    params["url"] = base_url
    params["headers"].update(
        {
            "Content-Type": "text/plain",
            "next-action": _get_next_action(),
        }
    )

    params["method"] = "POST"
    params["json"] = [{"query": query}]  # pyright: ignore[reportGeneralTypeIssues]
    params["raise_for_httperror"] = False


def response(resp: "SXNG_Response") -> EngineResults:
    # cached next action is no longer valid
    if resp.status_code == 404:
        CACHE.set("action", None)

    raise_for_httperror(resp)

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
