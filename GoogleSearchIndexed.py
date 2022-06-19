import tldextract
from googlesearch import search

def get_googleCS(req_url):
    google_indexed = 0

    ext_search = tldextract.extract(req_url)
    for url in search(req_url, tld="com", num=5, stop=5, pause=10):
        ext_google = tldextract.extract(url)
        if str('.'.join(ext_search[:3])) == str('.'.join(ext_google[:3])):
            google_indexed = 1
    print(google_indexed)
    return google_indexed


g_index = get_googleCS("https://example.com")
