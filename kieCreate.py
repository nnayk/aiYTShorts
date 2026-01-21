import requests
import pdb

url = "https://api.kie.ai/api/v1/jobs/createTask"

payload = {
    "model": "gpt-image/1.5-text-to-image",
    "input": {
        "prompt": "German Shepherd playing soccer with 2 owners. Make sure it is cartoon themed and highly realistic. Make sure minimal text is used and that it is spelled correctly!",
        "aspect_ratio": "1:1",
        "quality": "medium"
    }
}
headers = {
    "Authorization": "Bearer 7e928e5d6720899bdcc06f85de7e4815",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
pdb.set_trace()
