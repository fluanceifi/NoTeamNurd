import requests

res = requests.post('http://localhost:5000/generate-smile')
print(res.json())