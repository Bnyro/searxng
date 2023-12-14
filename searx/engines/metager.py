# SPDX-License-Identifier: AGPL-3.0-or-later
# lint: pylint
"""metaGer (general, images, news, science)
"""

from searx.network import get
from searx.utils import extract_text, eval_xpath, gen_useragent
from urllib.parse import quote_plus
from lxml import html

about = {
    "website": 'https://metager.org',
    'wikidata_id': 'Q1924645',
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}
paging = True

base_url = "https://metager.org"


def request(query, params):
    headers = {'User-Agent': gen_useragent()}
    url_response = get(f"{base_url}/meta/meta.ger3?eingabe={quote_plus(query)}", headers=headers)

    dom = html.fromstring(url_response.text)
    
    params['url'] = extract_text(eval_xpath(dom, "//meta[@name='url']/@content"))
    params['headers'] = headers

    print(get(params['url']).headers)
    
    return params

def response(resp):
    # print(resp.text)
    
    results = []
    
    return results
