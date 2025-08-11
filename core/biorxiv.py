import requests

def search_crossref_preprints_by_prefix(query: str, rows: int = 20, cursor: str | None = None):
    params = {
        "query.bibliographic": query,
        "filter": "type:posted-content,prefix:10.1101",
        "select": "DOI,title,author,issued,URL,container-title,type",
        "rows": rows,
    }
    if cursor:
        params["cursor"] = cursor
    r = requests.get("https://api.crossref.org/works", params=params)
    r.raise_for_status()
    return r.json()

def search_openalex_preprints(query: str, page: int = 1, per_page: int = 25, servers=("bioRxiv","medRxiv")):
    params = {
        "search": query,  # searches titles, abstracts, and some fulltext
        "page": page,
        "per-page": per_page,
        "select": "id,doi,display_name,primary_location"
    }
    response = requests.get("https://api.openalex.org/works", params=params)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    filtered = [
        work for work in results
        if (work.get("primary_location") or {}).get("source", {}).get("display_name") in servers
    ]
    return {"results": filtered, "raw": data}

if __name__ == "__main__":
    print(search_crossref_preprints_by_prefix(query="covid-19"))