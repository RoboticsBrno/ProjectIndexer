from os import environ, path, makedirs
from github import Github, PaginatedList, Repository, UnknownObjectException
import requests
import json, yaml
import urllib.parse
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FetchData:
    def __init__(self, github_token:str=None):
        load_dotenv()
        if github_token is None:
            github_token = environ.get('MY_GITHUB_TOKEN')
        if github_token is not None:
            self.g = Github(github_token)
            self.organization = self.g.get_organization("RoboticsBrno")
            return
        raise Exception('MY_GITHUB_TOKEN not found in .env file or system path')

    def fetch_repos(self):
        return self.organization.get_repos()

    def fetch_readme(self, repo: Repository.Repository) -> str:
        try:
            return repo.get_readme().decoded_content.decode("utf-8")
        except UnknownObjectException:
            return ""
    
    def fetch_contributors(self, repo: Repository.Repository, contributors_limit:int = 15) -> PaginatedList:
        try:
            return sorted(repo.get_contributors(), key=lambda x: x.contributions, reverse=True)[:contributors_limit]
        except UnknownObjectException:
            return []
        
    def fetch_about_info(self) -> dict:
        r = requests.get("https://raw.githubusercontent.com/RoboticsBrno/.github/main/profile/README.md")
        if int(r.status_code) == 200:
            readme = {p[0]: [v for v in p[1:]] for p in [s.split("\n") for s in r.content.decode().strip().replace(" --->", "").split("<!--- ")][1:]}
        
        cs_r = requests.get("https://raw.githubusercontent.com/RoboticsBrno/.github/main/profile/README.cs.md")
        if int(cs_r.status_code) == 200:
            cs_readme = {p[0]: [v for v in p[1:]] for p in [s.split("\n") for s in cs_r.content.decode().strip().replace(" --->", "").split("<!--- ")][1:]}
        
        
        info = {}

        titles = ["Website","RoboCamp","Instagram","Facebook","YouTube","Twitter"]
        links = [s[s.find('href="')+6:s.find('"', s.find('href="')+6)] for s in readme["contacts"][1:-1] if 'href="' in s]

        contacts = {}
        for t, l in zip(titles, links):
            contacts[t] = [l, l.split("/")[-1]]

        info.update({"contacts":contacts})
        
        info.update({"readme_1":readme["readme_1"],
                     "readme_2":readme["readme_2"],
                     "readme_1_cs":cs_readme["readme_1"],
                     "readme_2_cs":cs_readme["readme_2"]})
        
        info.update({"images":[s[s.find('src="')+5:s.find('"', s.find('src="')+5)] for s in readme["images"] if 'src="' in s]})

        return info
    
    def fetch_team(self) -> list[dict]:
        team = []
        r = requests.get("https://raw.githubusercontent.com/RoboticsBrno/Our-team/main/team.yaml")
        if int(r.status_code) == 200:
            _team:dict = yaml.safe_load(r.content)
            team = [{key: urllib.parse.unquote(value) if isinstance(value, str) else value for key, value in dictionary.items()} for dictionary in _team]
        return team

    def save_to_file(self, repos: list[Repository.Repository], file_repos:str= 'data/repos.json', file_readme:str= 'data/readme.json', file_contributors:str= 'data/contributors.json', file_about:str= 'data/about.json', file_team:str= 'data/team.json', verbose=False) -> int:
        """
        Save repos to file
        :param file_repos:
        :param repos: List of repos to save
        :param verbose: Print verbose build
        :return: Count of saved repos
        """
        directory = path.dirname(file_repos)
        if not path.exists(directory):
            makedirs(directory)

        data_repo = []
        data_readme = {}
        data_contrib = {}
        index = 0
        for repo in repos:
            if verbose:
                logger.info(f"Saving {repo.full_name} to {file_repos}")
            data_repo.append(repo.raw_data)
        
            data_readme[repo.full_name] = self.fetch_readme(repo)
        
            contributors = self.fetch_contributors(repo)
            data_contrib[repo.full_name] = [[contributor.html_url, contributor.avatar_url, contributor.name, contributor.login, contributor.contributions,] for contributor in contributors]
            index += 1

        data_about = self.fetch_about_info()
        data_team = self.fetch_team()

        with open(file_repos, 'w') as json_file:
            json.dump(data_repo, json_file)

        with open(file_readme, 'w') as json_file:
            json.dump(data_readme, json_file)

        with open(file_contributors, 'w') as json_file:
            json.dump(data_contrib, json_file)

        with open(file_about, 'w') as json_file:
            json.dump(data_about, json_file)

        with open(file_team, 'w') as json_file:
            json.dump(data_team, json_file)

        if verbose:
            logger.info(f"Saved {index} repos to {file_repos}")

        return index

    def load_repo(self, io_file:str= 'data/repos.json') -> list[Repository.Repository]:
        try:
            with open(io_file, 'r') as json_file:
                raw_data_list = json.load(json_file)
            return [
                self.g.create_from_raw_data(Repository.Repository, raw_data)
                for raw_data in raw_data_list
            ]
        except FileNotFoundError:
            logger.error(f"File {io_file} not found")
            return []

    def load_readme(self, file_readme: str="data/readme.json") ->  dict[str, str]:
        try:
            with open(file_readme, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"File {file_readme} not found")
            return {}
    
    def load_contributors(self, file_contrib: str="data/contributors.json") -> dict[str, list[str]]:
        try:
            with open(file_contrib, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"File {file_contrib} not found")
            return {}

    def load_about(self, file_about:str = "data/about.json") -> dict[str, str]:
        try:
            with open(file_about, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"File {file_about} not found")
            return {}
        
    def load_team(self, file_team:str = "data/team.json") -> dict[str, str]:
        try:
            with open(file_team, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"File {file_team} not found")
            return {}

if __name__ == "__main__":
    fetch_data = FetchData(environ.get('MY_GITHUB_TOKEN'))
    # repos = fetch_data.fetch_repos()
    # fetch_data.save_to_file(repos)
    loaded_repos = fetch_data.load_repo()
    # Now loaded_repos is a list of Repository objects
    print([repo.full_name for repo in loaded_repos])
