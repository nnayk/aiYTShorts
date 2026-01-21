import requests
import pdb

url = "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=b681912871e8e440aa4acf6c0aafcd6f"

headers = {"Authorization": "Bearer 7e928e5d6720899bdcc06f85de7e4815"}

response = requests.get(url, headers=headers)

print(response.text)

pdb.set_trace()
