# SPDX-License-Identifier: AGPL-3.0-or-later
"""MetaSearch engine from Switzerland."""

import typing as t
from urllib.parse import urlencode

from searx.exceptions import SearxEngineAPIException
from searx.enginelib import EngineCache
from searx.network import get
from searx.result_types import EngineResults
from searx.utils import eval_xpath, eval_xpath_list, extract_text

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams


about = {
    "website": "https://www.etools.ch",
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "HTML",
}

categories = ["general"]
paging = True
safesearch = True

base_url = "https://www.etools.ch"

CACHE: EngineCache
"""Cache for storing the JSESSIONID cookie and the csrf token."""

_CACHE_KEY = "sessionid_and_token"


def setup(engine_settings: dict[str, str]):
    global CACHE  # pylint: disable=global-statement
    CACHE = EngineCache(engine_settings["name"])


def _get_cookie_and_csrf_token() -> tuple[str, str]:
    cached: str
    if cached := CACHE.get(_CACHE_KEY):
        session_id, _, token = cached.partition("|")
        return session_id, token

    token_resp = get(base_url)

    token = eval_xpath(token_resp.html(), "//input[@name='token']/@value")
    token = extract_text(token)
    if not token:
        raise SearxEngineAPIException("failed to extract csrf token")

    session_id = token_resp.cookies.get("JSESSIONID")
    if not session_id:
        raise SearxEngineAPIException("failed to extract session id cookie")

    CACHE.set(_CACHE_KEY, f"{session_id}|{token}")
    return session_id, token


def request(query: str, params: "OnlineParams"):
    cookie, token = _get_cookie_and_csrf_token()
    params["cookies"]["JSESSIONID"] = cookie

    if params["pageno"] == 1:
        params["url"] = f"{base_url}/searchAdvancedSubmit.do"
        params["method"] = "POST"

        params["data"] = {
            "query": query,
            "country": "web",
            "language": "all",
            # safesearch doesn't seem to work
            "safeSearch": params["safesearch"] != 0,
            "token": token,
        }
    else:
        # re-uses previous query done by the session id, which is a bit awkward
        args = {"page": params["pageno"]}
        params["url"] = f"{base_url}/searchAdvanced.do?{urlencode(args)}"


def response(resp: "SXNG_Response") -> EngineResults:
    res = EngineResults()

    doc = resp.html()
    for result in eval_xpath_list(doc, "//table[contains(@class, 'result')]//td[contains(@class, 'record')]"):
        url = extract_text(eval_xpath(result, "./a/@href"))
        # ads have the same result layout as normal results, but no URL
        if not url:
            continue

        res.add(
            res.types.MainResult(
                url=url,
                title=extract_text(eval_xpath(result, "./a")) or "",
                content=extract_text(eval_xpath(result, "./div[contains(@class, 'text')]")) or "",
            )
        )

    return res
