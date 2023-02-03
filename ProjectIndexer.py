import requests, json, os

source_path = os.path.dirname(__file__)
data_path = "/repos.json"

if os.path.exists(source_path + data_path):
    f = open(source_path + data_path)
    repos = json.load(f)
    f.close()
else:
    content = requests.get("https://api.github.com/orgs/RoboticsBrno/repos")    # Loads only 1st 100 repositories
    repos = json.loads(content.content)

    with open(source_path + data_path, 'w') as f:
        json.dump(repos, f)