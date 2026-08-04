# SPDX-License-Identifier: AGPL-3.0-or-later
"""Goodsearch"""

from urllib.parse import urlencode
import typing as t

from lxml import html

from searx.utils import eval_xpath, eval_xpath_list, extract_text
from searx.result_types import EngineResults

if t.TYPE_CHECKING:
    from extended_types import SXNG_Response
    from search.processors import OnlineParams


# Engine metadata
about = {
    "website": "https://good-search.org/",
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "HTML",
}

# Engine configuration
categories = ["general"]
paging = True

# Search URL
base_url = "https://good-search.org"

GoodsearchCategs = t.Literal["index", "images", "news", "videos"]
goodsearch_categ: GoodsearchCategs = "index"

language = "en"
"""Supported: en, de, es, fr, it, nl"""


def init(_):
    if goodsearch_categ not in t.get_args(GoodsearchCategs):
        raise ValueError(f"invalid search category: {goodsearch_categ}")


def request(query: str, params: "OnlineParams") -> None:
    query_params: dict[str, t.Any] = {"q": query, "s": params["pageno"]}
    params["url"] = f"{base_url}/{language}/search/{goodsearch_categ}?{urlencode(query_params)}"


def response(resp: "SXNG_Response") -> EngineResults:
    results = EngineResults()
    dom = html.fromstring(resp.text)

    if goodsearch_categ == "index":
        for result in eval_xpath_list(dom, "//div[@id='hybrid']/div[contains(@class, 'box') and ./a]"):
            results.add(
                results.types.MainResult(
                    url=extract_text(eval_xpath(result, "./a/@href")),
                    title=extract_text(eval_xpath(result, "./a/h4[contains(@class, 'result')]")) or "",
                    content=extract_text(eval_xpath(result, "./div[contains(@class, 'link--search')]")) or "",
                )
            )
    elif goodsearch_categ == "images":
        for result in eval_xpath_list(dom, "//div[@id='results']/div/div"):
            results.add(
                results.types.Image(
                    url=extract_text(eval_xpath(result, "./a/@href")),
                    title=extract_text(eval_xpath(result, "./a//h3")) or "",
                    thumbnail_src=extract_text(eval_xpath(result, ".//img/@src")) or "",
                )
            )
    elif goodsearch_categ == "videos":
        for result in eval_xpath_list(dom, "//div[contains(@class, 'videos')]/a[contains(@class, 'link--video')]"):
            results.add(
                results.types.MainResult(
                    template="videos.html",
                    url=extract_text(eval_xpath(result, "./@href")),
                    title=extract_text(eval_xpath(result, ".//h4")) or "",
                    content=extract_text(eval_xpath(result, ".//p")) or "",
                    thumbnail=extract_text(eval_xpath(result, ".//img/@src")) or "",
                )
            )
    elif goodsearch_categ == "news":
        for result in eval_xpath_list(dom, "//div[contains(@class, 'news')]/a[contains(@class, 'link--video')]"):
            results.add(
                results.types.MainResult(
                    url=extract_text(eval_xpath(result, "./@href")),
                    title=extract_text(eval_xpath(result, ".//h4")) or "",
                    content=extract_text(eval_xpath(result, ".//p")) or "",
                    thumbnail=extract_text(eval_xpath(result, ".//img/@src")) or "",
                )
            )

    return results
