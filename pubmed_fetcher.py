import requests
import csv
import re
from typing import List, Dict, Any

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def fetch_pubmed_ids(query: str) -> List[str]:
    """Fetch paper IDs from PubMed based on query."""
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": 10}
    response = requests.get(PUBMED_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_paper_details(paper_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch details of papers using PubMed IDs."""
    if not paper_ids:
        return []
    
    params = {"db": "pubmed", "id": ",".join(paper_ids), "retmode": "json"}
    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    papers = []
    for paper_id in paper_ids:
        summary = data["result"].get(paper_id, {})
        title = summary.get("title", "Unknown Title")
        pub_date = summary.get("pubdate", "Unknown Date")
        authors = summary.get("authors", [])
        
        non_academic_authors = [a for a in authors if not re.search(r"university|lab|institute", a.get("name", "").lower())]
        company_affiliations = [a.get("name") for a in non_academic_authors if "pharma" in a.get("name", "").lower() or "biotech" in a.get("name", "").lower()]
        corresponding_email = summary.get("source", "Unknown Email")

        papers.append({
            "PubmedID": paper_id,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Author(s)": ", ".join([a.get("name", "") for a in non_academic_authors]),
            "Company Affiliation(s)": ", ".join(company_affiliations),
            "Corresponding Author Email": corresponding_email
        })
    return papers

def save_to_csv(papers: List[Dict[str, Any]], filename: str):
    """Save paper details to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"])
        writer.writeheader()
        writer.writerows(papers)