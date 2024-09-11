import requests
res = requests.post("http://localhost:5000/post_location",data="latitude=2%2E984787&longitude=101%2E537529&date=08+%2F+09+%2F+2024&time=23+%3A+57+%3A+44")
print(res.status_code)
print(res.text)