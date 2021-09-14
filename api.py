import requests
import json
import time
import sys

ddc_base_api_url = "https://datadesacenter.dpmd.jatimprov.go.id/api/"
path_list = [
    # "v1/bumdes",
    # "v1/karang-taruna",
    # "v1/kpm",
    # "v1/lembaga-adat",
    # "v1/perangkat-desa",
    # "v1/lpmd",
    # "v1/pasar-desa",
    # "v1/pkk",
    # "v1/potensi-desa-tanaman",
    "v1/potensi-desa-ternak",
    "v1/posyandu",
]

def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def ddc_api_url(path=""):
    return f"{ddc_base_api_url}{path}"

def get_data(path, **kwargs):
    sort = kwargs.get("sort", "")
    per_page = kwargs.get("per_page", 50)
    page = kwargs.get("page", 1)
    url = ddc_api_url(path)
    url = f"{url}?_format=json"
    url += f"&sort={sort}"
    url += f"&per-page={per_page}"
    url += f"&page={page}"
    result = requests.get(url)
    if result.status_code == 200:
        return True, result.json()
    return False, dict()

def scrap_data(path):
    search_keyword = {"key": "kd_kabupaten", "value": "3502"}
    all_items = []
    pages = 0
    print(f"on {path}", end=" ", flush=True)
    def _get_data(page):
        ok, data = get_data(path, sort="kd_kabupaten", per_page=50, page=page)
        if ok:
            items = data.get("items", [])
            total_items = data.get("_meta", {}).get("totalCount", None)
            total_pages = data.get("_meta", {}).get("pageCount", None)
            current_page = data.get("_meta", {}).get("currentPage", None)
            next_page_link = data.get("_links", {}).get("next", {}).get("href", None)
            last_page_link = data.get("_links", {}).get("last", {}).get("href", None)

            for item in items:
                if item.get(search_keyword["key"]) == search_keyword["value"]:
                    all_items.append(item)
                    # print(".")

            return total_pages
        
        return 0
    pages = _get_data(1)
    print(f"{pages} total", end=". ", flush=True)
    # for i in progressBar(range(2, pages), prefix = 'Progress:', suffix = 'Complete', length = 50):
    for i in range(2, pages):
        _get_data(i)
        sys.stdout.write("\r%d%%" % i)
        sys.stdout.flush()
        time.sleep(0.2)
    
    filename = path.replace("/", "_")
    print("save file...")
    with open(f"data/{filename}.json", "w+") as save_file:
        save_file.write(json.dumps(all_items))
        print("done")

for path in path_list:
    scrap_data(path)