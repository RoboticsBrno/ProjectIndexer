import os
import random
import re
from datetime import datetime
from os import path, makedirs
from pprint import pprint
from typing import Union

from github import Repository
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from shutil import copytree
import subprocess
import logging

from markdown import markdown

from src.jinja_extensions.color_extension import ColorExtension
from src.web_helpers import load_projects, fix_readme_relative_images

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerateWeb:
    def __init__(
            self,
            repos: list[Repository.Repository],
            readme: dict[str, str],
            build_dir: str = 'build',
            template_dir: path = 'templates',
            static_dir: path = 'static',
            project_dir: path = 'projects',
            hide_private: bool = False,
            verbose: bool = False,
            compile_tailwind: bool = False,
    ):
        if hide_private:
            self.repos = [repo for repo in repos if not repo.private]
        else:
            self.repos = repos

        self.readme = readme
        self.static_dir = static_dir
        self.template_dir = template_dir
        self.project_dir = project_dir
        self.build_dir = build_dir
        self.hide_private = hide_private
        self.verbose = verbose
        self.compile_tailwind = compile_tailwind
        if not path.exists(self.build_dir):
            makedirs(self.build_dir)

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'jinja2']),
            extensions=[ColorExtension]
        )

        self.paths = {
            "/": {"path": "index.html", "showHeader": False, "external": False},
            "Repos": {"path": "repos/index.html", "showHeader": True, "external": False},
            "Repo": {"path": "repos/{}/index.html", "showHeader": False, "external": False},
            "Projects": {"path": "projects/index.html", "showHeader": True, "external": False},
            "Project": {"path": "projects/{}/index.html", "showHeader": False, "external": False},
            "Demo": {"path": "demo/index.html", "showHeader": True, "external": False},
            "About": {"path": "about/index.html", "showHeader": True, "external": False},
            "Our team": {"path": "https://team.robotikabrno.cz/", "showHeader": True, "external": True},
        }

        self.env.globals['paths'] = self.paths

    def generate(self):
        self.copy_static_files()
        self.generate_repos_list()
        self.generate_repos_detail()
        self.generate_demo()
        self.generate_about()

        projects = load_projects(self.project_dir)
        self.generate_project_list(projects)
        self.generate_projects(projects)
        if self.compile_tailwind:
            self.compile_tailwind_css()

    def copy_static_files(self):
        #TODO: not working
        if self.verbose:
            logger.info(f"Copying static files from {self.static_dir} to {self.build_dir}")

        if not path.exists(self.static_dir):
            logger.warning(f"Static directory {self.static_dir} does not exist")
            return

        copytree(self.static_dir, self.build_dir, dirs_exist_ok=True)

    def compile_tailwind_css(self):
        if self.verbose:
            logger.info('Compiling tailwindcss')

        try:
            # Assuming that your Tailwind CSS file is `./src/tailwind.css`
            # and you want to output to `./build/tailwind.css`.
            command = "npx tailwindcss -i css/style.css -o build/style.css"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()
            print("Command executed successfully. Exit code:", process.returncode)

        except subprocess.CalledProcessError as e:
            print("An error occurred while executing the command. Error: ", e)



    def generate_repos_list(self):
        self.render_page('repos.html', self.paths.get("/").get("path"), repos=self.repos)
        self.render_page('repos.html', self.paths.get("Repos").get("path"), repos=self.repos)

    def generate_repos_detail(self):
        for repo in self.repos:
            readme_md = self.readme.get(repo.full_name, "No readme found")
            readme_fixed_images = fix_readme_relative_images(readme_md, repo.full_name, repo.default_branch)
            readme_html = markdown(readme_fixed_images, extensions=['fenced_code'])
            path_repo = self.paths.get("Repo").get("path").format(repo.name)
            self.render_page('repoDetail.html', path_repo, repo=repo, readme=readme_html)

    def generate_demo(self):
        self.render_page('demo.html', self.paths.get("Demo").get("path"))


    def generate_project_list(self, projects: list):
        self.render_page('projectList.html', self.paths.get("Projects").get("path"), projects=projects)

    def generate_projects(self, projects: list):
        pprint(projects)

        for project in projects:
            path_project = self.paths.get("Project").get("path").format(project["url"])
            self.render_page('projectDetail.html', path_project, project=project)



    def generate_about(self,):
        self.render_page('about.html', self.paths.get("About").get("path"))


    def render_page(self, template_name: Union[str, "Template"], path_render: str, **kwargs):
        template = self.env.get_template(template_name)
        full_path = os.path.join(self.build_dir, path_render)
        if not path.exists(path.dirname(full_path)):
            makedirs(path.dirname(full_path))
        try:
            with open(full_path, 'w') as f:
                if self.verbose:
                    logger.info(f"Generating {path}")
                f.write(template.render(**kwargs))
        except Exception as e:
            logger.error(f"Error while generating {path_render}")
            logger.error(e)
            raise e