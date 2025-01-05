import requests

url = "https://www.javbus.com/search/ipx660"
req = requests.get(url)
print(req.text)