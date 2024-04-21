from os import environ, path, makedirs
from github import Github, PaginatedList, Repository, UnknownObjectException
import json
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

    def save_to_file(self, repos: list[Repository.Repository], file_repos:str= 'data/repos.json', file_readme:str= 'data/readme.json', file_contributors:str= 'data/contributors.json', verbose=False) -> int:
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
        with open(file_repos, 'w') as json_file:
            json.dump(data_repo, json_file)

        with open(file_readme, 'w') as json_file:
            json.dump(data_readme, json_file)

        with open(file_contributors, 'w') as json_file:
            json.dump(data_contrib, json_file)

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
        # return {repo, [name, login, url_to_img]}
        try:
            with open(file_contrib, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"File {file_contrib} not found")
            return {}

if __name__ == "__main__":
    fetch_data = FetchData(environ.get('MY_GITHUB_TOKEN'))
    # repos = fetch_data.fetch_repos()
    # fetch_data.save_to_file(repos)
    loaded_repos = fetch_data.load_repo()
    # Now loaded_repos is a list of Repository objects
    print([repo.full_name for repo in loaded_repos])
