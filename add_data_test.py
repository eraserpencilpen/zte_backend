import requests
data = {
    # location is a keyword. cannot change.
    "location": "3.0657744932941657, 101.60546813425843",
    # other data can also be input. 
    "some other data" : "some other data"
}
url = "http://127.0.0.1:5000/add_data"
cookie = ".eJwljjkOAjEMAP-SmiJxbCfZzyCvDy0FFHtUiL8TRDnSjDTvdI_djy0t5375Ld0flpYEpg4rEwblEOaQzAVJqnnQYDBoRNhFyyjs1KdA2FbXgcMCKGdvxFlIAep0lBqhlJCOPABhUKXSzGeqfZU8NLtWVWE3EIs0R67D9_9Nnfijlzx94nFu6fMF8aM03g.ZtWtgw.4NSoxJXvboZrYsoH4HIbZTqBvRw"
res = requests.post(url,json=data,cookies={"session":cookie})
print(res.text)

