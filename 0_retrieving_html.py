import requests
def fetchAndSaveToFile (url,path):
    response = requests.get(url)
    with open(path, mode='w', encoding='utf-8') as f:
        f.write(response.text)
url="https://en.wikipedia.org/wiki/Main_Page"
fetchAndSaveToFile(url,"File.html")
