from os import path, makedirs

from github import Repository
from jinja2 import Environment, FileSystemLoader, select_autoescape
from shutil import copytree, copy2

class GenerateWeb:
    def __init__(
            self,
            repos: list[Repository.Repository],
            output_dir: str = 'output',
            template_dir: path = 'templates',
            static_dir: path = 'static',
            hide_private: bool = False
    ):
        self.repos = repos
        self.static_dir = static_dir
        self.output_dir = output_dir
        self.hide_private = hide_private
        if not path.exists(self.output_dir):
            makedirs(self.output_dir)

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'jinja2'])
        )

    def generate(self):
        # self.copy_static_files()
        self.generate_list_repos()
        self.generate_detail_repos()

    def copy_static_files(self):
        #TODO: not working
        copytree(self.static_dir, self.output_dir, dirs_exist_ok=True)


    def generate_list_repos(self):
        list_template = self.env.get_template('list.html')
        if self.hide_private:
            data = [repo for repo in self.repos if not repo.private]
        else:
            data = self.repos
        # data.sort(key=lambda repo: repo.name)
        with open(f'{self.output_dir}/index.html', 'w') as f:
            f.write(list_template.render(repos=data))

    def generate_detail_repos(self):
        detail_template = self.env.get_template('detail.html')
        for repo in self.repos:
            if self.hide_private and repo.private:
                continue
            if not path.exists(f'{self.output_dir}/{repo.name}'):
                makedirs(f'{self.output_dir}/{repo.name}')
            with open(f'{self.output_dir}/{repo.name}/index.html', 'w') as f:
                f.write(detail_template.render(repo=repo))