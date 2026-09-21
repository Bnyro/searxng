# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pristine, human-scale web index, curated for clarity, free from AI noise, ads, and tracking."""

import typing as t
from urllib.parse import urlencode

from searx.result_types import EngineResults
from searx.network import get
from searx.utils import eval_xpath, eval_xpath_list, extract_text

if t.TYPE_CHECKING:
    from searx.search.processors import OnlineParams
    from searx.extended_types import SXNG_Response

about = {
    "website": "https://greppr.org",
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "HTML",
}

paging = True
categories = ['general']

# can't be changed
page_size = 30

base_url = "https://greppr.org"


def _obtain_form_params(query: str) -> tuple[dict[str, str], dict[str, str]]:
    resp = get(base_url)
    doc = resp.html()

    params = {"query": query}

    inputs = eval_xpath_list(doc, "//form[@id='queryForm']/input[@type='hidden']")

    for input in inputs:
        name = extract_text(eval_xpath(input, "./@name")) or ""
        value = extract_text(eval_xpath(input, "./@value")) or ""
        if not value:
            value = query
        params[name] = value

    header_name = extract_text(eval_xpath(doc, "//form[@id='queryForm']/@data-header-name")) or ""
    header_value = extract_text(eval_xpath(doc, "//form[@id='queryForm']/@data-nonce")) or ""

    return params, {header_name: header_value}


def request(query: str, params: "OnlineParams"):
    form_params, headers = _obtain_form_params(query)
    form_params["l"] = str(page_size)
    form_params["s"] = str((params["pageno"] - 1) * page_size)

    params["url"] = f"{base_url}/search?{urlencode(form_params)}"
    params["headers"].update(headers)


def response(resp: "SXNG_Response"):
    res = EngineResults()

    # no results found
    if not resp.text:
        return res

    doc = resp.html()
    for result in eval_xpath_list(doc, "//main/div[contains(@class, 'result-item')]"):
        res.append(
            res.types.MainResult(
                url=extract_text(eval_xpath(result, "./h4/a/@href")),
                title=extract_text(eval_xpath(result, "./h4/a")) or "",
                content=extract_text(eval_xpath(result, "./p[contains(@class, 'result-snippet')]")) or "",
            )
        )

    return res
