import os
import requests
from datetime import datetime
from os import path, makedirs
from typing import Union

from github import Repository
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from shutil import copytree
import subprocess
import logging

from src.jinja_extensions.color_extension import ColorExtension
from src.web_helpers import load_projects, fix_readme_relative_images, conv_markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerateWeb:
    def __init__(
            self,
            repos: list[Repository.Repository],
            readme: dict[str, str],
            contributors: dict[str, list],
            about_info: dict,
            team: dict,
            # build_dir: str = 'build',
            # template_dir: path = 'templates',
            # static_dir: path = 'static',
            # project_dir: path = 'projects',
            hide_private: bool = False,
            verbose: bool = False,
            compile_tailwind: bool = False,
    ):
        if hide_private:
            self.repos = [repo for repo in repos if not repo.private]
        else:
            self.repos = repos

        self.readme = readme
        self.contributors = contributors
        self.about_info = about_info
        self.team = team
        self.static_dir = "static"
        self.template_dir = "templates"
        self.project_dir = "projects"
        self.build_dir = "build"
        self.hide_private = hide_private
        self.verbose = verbose
        self.compile_tailwind = compile_tailwind
        if not path.exists(self.build_dir):
            makedirs(self.build_dir)

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'jinja2']),
            extensions=[ColorExtension]
        )

        self.paths: dict[str, dict[str, str | bool]] = {
            "/":            {"path": "index.html",                  "lang":"en", "showHeader": False,    "external": False},
            "Repos":        {"path": "repos/index.html",            "lang":"en", "showHeader": True,     "external": False},
            "Repo":         {"path": "repo/{}/index.html",          "lang":"en", "showHeader": False,    "external": False},
            "Projects":     {"path": "projects/index.html",         "lang":"en", "showHeader": True,     "external": False},
            "Project":      {"path": "project/{}/index.html",       "lang":"en", "showHeader": False,    "external": False},
            "Our team":     {"path": "team/index.html",             "lang":"en", "showHeader": True,     "external": False},
            
            "/cs":          {"path": "cs/index.html",               "lang":"cs", "showHeader": False,    "external": False},
            "Repozitáře":   {"path": "cs/repozitare/index.html",    "lang":"cs", "showHeader": True,     "external": False},
            "Repo_cs":      {"path": "cs/repo/{}/index.html",       "lang":"cs", "showHeader": False,    "external": False},
            "Projekty":     {"path": "cs/projekty/index.html",      "lang":"cs", "showHeader": True,     "external": False},
            "Projekt":      {"path": "cs/projekt/{}/index.html",    "lang":"cs", "showHeader": False,    "external": False},
            "Náš tým":      {"path": "cs/nas-tym/index.html",       "lang":"cs", "showHeader": True,     "external": False},
            
            # "Our team":   {"path": "https://team.robotikabrno.cz/", "showHeader": True,     "external": True},
            # "About":        {"path": "about/index.html",            "showHeader": True,     "external": False},
        }

        self.env.globals['paths'] = self.paths

    def generate(self):
        self.copy_static_files()
        
        self.generate_about()
        self.generate_repos_list()
        self.generate_repos_detail()
        self.generate_team()
        projects = load_projects(self.project_dir)
        self.generate_project_list(projects)
        self.generate_projects(projects)
        if self.compile_tailwind:
            self.compile_tailwind_css()

    def copy_static_files(self):
        # TODO: not working
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
        self.render_page('repos.html', self.paths.get("Repos").get("path"), repos=self.repos, lang="en")
        
        self.render_page('repos_cs.html', self.paths.get("Repozitáře").get("path"), repos=self.repos, lang="cs")

    def generate_repos_detail(self):
        repo_count = len(self.repos)
        for i, repo in enumerate(self.repos):
            print(f"Generating {repo.name} {i}/{repo_count}")
            readme_md = self.readme.get(repo.full_name, "No readme found")
            readme_fixed_images = fix_readme_relative_images(
                readme_md, repo.full_name, repo.default_branch)

            list_conv = {}
            for i in range(0, 5):
                list_conv[f"\n{' ' * i}- "] = f"\n{' ' *
                                                   (3 if i > 1 else 0)} @@"
                list_conv[f"\n{' ' * i}* "] = f"\n{' ' *
                                                   (3 if i > 1 else 0)} @@"

            readme_fixed_lists = readme_fixed_images
            for o in list_conv:
                readme_fixed_lists = readme_fixed_lists.replace(
                    o, list_conv[o])

            # add the dot before each element of the list
            readme_fixed_lists = readme_fixed_lists.replace("@@", "- ● ")

            readme_html = conv_markdown(readme_fixed_lists)
            

            repo_contrib = [[sublist[i+1] if sublist[i] is None and i+1 < len(
                sublist) else sublist[i] for i in range(len(sublist))] for sublist in self.contributors[repo.full_name]]
            
            self.render_page('repoDetail.html', self.paths.get("Repo").get("path").format(repo.name), repo=repo, readme=readme_html, repo_contrib=repo_contrib, lang="en")
            self.render_page('repoDetail_cs.html', self.paths.get("Repo_cs").get("path").format(repo.name), repo=repo, readme=readme_html, repo_contrib=repo_contrib, lang="cs")

    def generate_project_list(self, projects: list):
        # Helper: order projects (both -> frequently_used -> recent -> others)
        def order_projects(items):
            both, freq, recent, other = [], [], [], []
            for it in items:
                if it.get("recent") and it.get("frequently_used"):
                    both.append(it)
                elif it.get("frequently_used"):
                    freq.append(it)
                elif it.get("recent"):
                    recent.append(it)
                else:
                    other.append(it)
            return both + freq + recent + other

        def get_localized(it, key, lang):
            if lang == "cs":
                v_cs = it.get(f"{key}-cs")
                if v_cs:
                    return v_cs
            return it.get(key)

        # Build a flat list for the given language
        def build_flat(lang):
            flat = []
            seen = set()
            for it in order_projects(projects):
                url = it.get("url")
                if not url or url in seen:
                    continue
                seen.add(url)
                flat.append({
                    "name": get_localized(it, "name", lang) or url,
                    "description": get_localized(it, "description", lang),
                    "image": get_localized(it, "image", lang),
                    "url": url,  # keep slugs shared between locales unless you also support url-cs
                })
            return flat

        projects_en = build_flat("en")
        projects_cs = build_flat("cs")

        # Render pages with a single flat 'projects' list (no categories)
        self.render_page(
            'projectList.html',
            str(self.paths["Projects"]["path"]),
            projects=projects_en,
            lang="en"
        )
        self.render_page(
            'projectList_cs.html',
            str(self.paths["Projekty"]["path"]),
            projects=projects_cs,
            lang="cs"
        )

    def generate_projects(self, projects: list):
        # pprint(projects)

        for project in projects:
            for i, repo in enumerate(project["related_repos"]):
                project["related_repos"][i]["name"] = repo["url"].split(
                    "/")[-1]  # add "name" key to related_projects
            
            readme_url = str(project["readme"]).replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")
            readme_md = "No readme found"

            r = requests.get(readme_url)
            if int(r.status_code) == 200:
                readme_md = r.content.decode().strip()

            full_name = "/".join(str(project["readme"]).split("/")[-5:-3])
            branch = str(project["readme"]).split("/")[-2]

            readme_fixed_images = fix_readme_relative_images(
                readme_md, full_name, branch)
            readme_fixed_lists = readme_fixed_images.replace('\n- ', '\n@@ ').replace('\n* ', '\n@@ ').replace(
                # add the dot before each element of the list
                '\n    - ', '\n    @@ ').replace('\n    * ', '\n    @@ ').replace("@@", "- ●")

            readme_html = conv_markdown(readme_fixed_lists)

            path_project = self.paths.get("Project").get("path").format(project["url"])
            self.render_page('projectDetail.html', path_project, project=project, readme=readme_html, lang="en")
            path_project = self.paths.get("Projekt").get("path").format(project["url"])
            self.render_page('projectDetail_cs.html', path_project, project=project, readme=readme_html, lang="cs")

    def generate_about(self):
        info = self.about_info

        # Existing readme conversions
        info["readme_1"] = conv_markdown("\n".join(info["readme_1"]))
        info["readme_2"] = conv_markdown("\n".join(info["readme_2"]))
        info["readme_1_cs"] = conv_markdown("\n".join(info["readme_1_cs"]))
        info["readme_2_cs"] = conv_markdown("\n".join(info["readme_2_cs"]))

        # Latest repos (for "Latest commits" section)
        repos = [i[0] for i in sorted([[r, r.pushed_at] for r in self.repos],
                                      key=lambda x: x[1],
                                      reverse=True)[:6]]

        # Load projects
        try:
            projects = load_projects(self.project_dir)
        except Exception:
            projects = []

        # Helper: sort by both -> frequently_used -> recent -> others
        def order_projects(items):
            both, freq, recent, other = [], [], [], []
            for it in items:
                if it.get("recent") and it.get("frequently_used"):
                    both.append(it)
                elif it.get("frequently_used"):
                    freq.append(it)
                elif it.get("recent"):
                    recent.append(it)
                else:
                    other.append(it)
            return both + freq + recent + other

        # Helper: localized getter for fields; prefers "-cs" when lang == "cs"
        def get_localized(it, key, lang):
            if lang == "cs":
                v_cs = it.get(f"{key}-cs")
                if v_cs:
                    return v_cs
            return it.get(key)

        # Build card lists for EN and CS
        def build_cards(lang):
            seen = set()
            cards = []
            for it in order_projects(projects):
                url = it.get("url")
                if not url or url in seen:
                    continue
                seen.add(url)
                cards.append({
                    # Display fields localized for CS
                    "name": get_localized(it, "name", lang) or url,
                    "description": get_localized(it, "description", lang),
                    "image": get_localized(it, "image", lang),
                    # Keep URL unlocalized unless your routing supports localized slugs
                    "url": url,
                })
                if len(cards) >= 9:
                    break
            return cards

        projects_cards_en = build_cards("en")
        projects_cards_cs = build_cards("cs")

        # Render both locales
        self.render_page(
            'about.html',
            self.paths.get("/").get("path"),
            info=info,
            repos=repos,
            projects_cards=projects_cards_en,
            lang="en",
        )
        self.render_page(
            'about_cs.html',
            self.paths.get("/cs").get("path"),
            info=info,
            repos=repos,
            projects_cards=projects_cards_cs,
            lang="cs",
        )

    def generate_team(self):
        team = self.team

        self.render_page('team.html', self.paths.get("Our team").get("path"), team=team, lang="en")
        
        self.render_page('team_cs.html', self.paths.get("Náš tým").get("path"), team=team, lang="cs")

    def render_page(self, template_name: Union[str, "Template"], path_render: str, **kwargs):
        template = self.env.get_template(template_name)
        full_path = os.path.join(self.build_dir, path_render)
        
        if not path.exists(path.dirname(full_path)):
            makedirs(path.dirname(full_path))
        try:
            with open(full_path, 'w') as f:
                if self.verbose:
                    logger.info(f"Generating {path}")
                f.write(template.render(**kwargs, now=datetime.now().year))
        except Exception as e:
            logger.error(f"Error while generating {path_render}")
            logger.error(e)
            raise e
