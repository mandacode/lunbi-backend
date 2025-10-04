import requests

BASE = "https://visualization.osdr.nasa.gov/biodata/api"

def get_all_datasets():
    url = f"{BASE}/v2/datasets/"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_dataset_metadata(accession):
    url = f"{BASE}/v2/dataset/{accession}/"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_samples_of_assay(accession, assay_name):
    # zakładam, że assay_name to dokładny ciąg który pojawia się w API
    url = f"{BASE}/v2/dataset/{accession}/assay/{assay_name}/samples/"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def query_metadata(filters: dict, output_format="json"):
    """
    filters: słownik, np. {"study.characteristics.strain": "S288C", "id.accession": "OSD-48"}
    output_format: "json", "csv", itp.
    """
    url = f"{BASE}/v2/query/metadata/"
    params = filters.copy()
    params["format"] = output_format
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    # jeśli JSON:
    if output_format.lower().startswith("json"):
        return resp.json()
    else:
        return resp.text  # CSV lub TSV jako tekst

def query_data(filters: dict, output_format="json"):
    url = f"{BASE}/v2/query/data/"
    params = filters.copy()
    params["format"] = output_format
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    if output_format.lower().startswith("json"):
        return resp.json()
    else:
        return resp.content
