import os
from typing import IO

import yaml

def load_projects(project_dir: os.path) -> list:
    def project_loader(project):
        with open(f'{project_dir}/{project}') as f:
            return yaml.safe_load(f)

    projects_dir = [f for f in os.listdir(project_dir) if f.endswith('.yaml') and not f == "template.yaml"]

    projects = [project_loader(project) for project in projects_dir]
    return projects


import re

def fix_readme_relative_images(readme_md: str, full_name: str, default_branch: str) -> str:
    # Base URL for raw content
    base_url = f"https://raw.githubusercontent.com/{full_name}/{default_branch}"

    # Regular expression to find all markdown image syntax
    md_pattern = r"\!\[([^\]]*)\]\(([^\)]*)\)"

    # Regular expression to find HTML image syntax
    html_pattern = r'<img\s+[^>]*src="([^"]*)"[^>]*>'



    # Replace relative image paths with absolute paths
    def md_replacer(match):
        alt_text = match.group(1)
        img_url = match.group(2)
        return replace_url(img_url, alt_text)

    def html_replacer(match):
        img_url = match.group(1)
        return f'<img src="{replace_url(img_url)}">'

    # def link_replacer_html(match):
    #     link_url = match.group(1)
    #     return f'<a href="{replace_url(link_url)}">'
    #
    # def link_replacer_md(match):
    #     link_url = match.group(1)
    #     return f'[{replace_url(link_url)}]'

    def replace_url(img_url, alt_text=""):
        # Handle different types of relative paths
        if img_url.startswith("/"):
            new_url = base_url + img_url
        elif img_url.startswith("./"):
            new_url = f"{base_url}/{img_url[2:]}"
        elif img_url.startswith("https://github.com"):
            new_url = base_url + img_url.split("/blob/master")[-1]
        elif img_url.startswith("http"):
            # The URL is already absolute, or it's a type of relative URL
            new_url = img_url
        else:
            new_url = base_url + "/"+ img_url

        return f"![{alt_text}]({new_url})" if alt_text else new_url

    # Replace Markdown image URLs
    readme_md = re.sub(md_pattern, md_replacer, readme_md)

    # Replace HTML image URLs
    readme_md = re.sub(html_pattern, html_replacer, readme_md)

    # # Replace HTML link URLs
    # readme_md = re.sub(r'<a href="([^"]*)">', link_replacer_html, readme_md)
    #
    # # Replace Markdown link URLs
    # readme_md = re.sub(r'\[([^]]*)\]\(([^)]*)\)', link_replacer_md, readme_md)

    return readme_md
