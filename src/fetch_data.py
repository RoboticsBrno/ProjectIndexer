from os import environ
from github import Github, PaginatedList, Repository
import json
from dotenv import load_dotenv

class FetchData:
    def __init__(self, github_token:str=None, io_file:str='data/repos.json'):
        load_dotenv()
        if github_token is None:
            github_token = environ.get('MY_GITHUB_TOKEN')
        if github_token is not None:
            self.g = Github(github_token)
            self.io_file = io_file
            self.organization = self.g.get_organization("RoboticsBrno")
            return
        raise Exception('MY_GITHUB_TOKEN not found in .env file or system path')

    def fetch_repos(self):
        return self.organization.get_repos()


    def save_to_file(self, repos: list[Repository.Repository], verbose=False) -> int:
        """
        Save repos to file
        :param repos: List of repos to save
        :param verbose: Print verbose output
        :return: Count of saved repos
        """
        data_to_write = []
        index = 0
        for repo in repos:
            if verbose:
                print(f"Saving repo {index} - {repo.full_name}")
            data_to_write.append(repo.raw_data)
            index += 1
        with open(self.io_file, 'w') as json_file:
            json.dump(data_to_write, json_file)

        if verbose:
            print(f"Saved {len(data_to_write)} repos to {self.io_file}")

        return index

    def load_from_file(self) -> list[Repository.Repository]:
        try:
            with open(self.io_file, 'r') as json_file:
                raw_data_list = json.load(json_file)
            repos = []
            for raw_data in raw_data_list:
                repos.append(self.g.create_from_raw_data(Repository.Repository, raw_data))
            return repos
        except FileNotFoundError:
            print(f"File {self.io_file} not found")
            return []

if __name__ == "__main__":
    fetch_data = FetchData(config('GITHUB_TOKEN'))
    # repos = fetch_data.fetch_repos()
    # fetch_data.save_to_file(repos)
    loaded_repos = fetch_data.load_from_file()
    # Now loaded_repos is a list of Repository objects
    print([repo.full_name for repo in loaded_repos])
