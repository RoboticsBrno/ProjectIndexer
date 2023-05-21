from os import environ, path, makedirs
from github import Github, PaginatedList, Repository
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


    def save_to_file(self, repos: list[Repository.Repository], io_file:str='data/repos.json', verbose=False) -> int:
        """
        Save repos to file
        :param io_file:
        :param repos: List of repos to save
        :param verbose: Print verbose output
        :return: Count of saved repos
        """
        directory = path.dirname(io_file)
        if not path.exists(directory):
            makedirs(directory)

        data_to_write = []
        index = 0
        for repo in repos:
            if verbose:
                logger.info(f"Saving {repo.full_name} to {io_file}")
            data_to_write.append(repo.raw_data)
            index += 1
        with open(io_file, 'w') as json_file:
            json.dump(data_to_write, json_file)

        if verbose:
            logger.info(f"Saved {index} repos to {io_file}")

        return index

    def load_from_file(self, io_file:str='data/repos.json') -> list[Repository.Repository]:
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

if __name__ == "__main__":
    fetch_data = FetchData(environ.get('MY_GITHUB_TOKEN'))
    # repos = fetch_data.fetch_repos()
    # fetch_data.save_to_file(repos)
    loaded_repos = fetch_data.load_from_file()
    # Now loaded_repos is a list of Repository objects
    print([repo.full_name for repo in loaded_repos])
