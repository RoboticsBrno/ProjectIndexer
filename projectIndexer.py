import os
import click
from src.fetch_data import FetchData
from src.generate_web import GenerateWeb
from pprint import pprint
from time import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@click.command(help='Save repos from RoboticsBrno organization to file')
@click.option('--github-token', default=None, help='Github token (default is in .env file)')
@click.option('--output-repos', '-o', default='data/repos.json', help='build file (default is repos.json)')
@click.option('--output-readme', '-r', default='data/readme.json', help='build file (default is readme.json)')
@click.option('--output-contributors', '-c', default='data/contributors.json', help='build file (default is contributors.json)')
@click.option('--output-about', '-a', default='data/about.json', help='build file (default is about.json)')
@click.option('--output-team', '-t', default='data/team.json', help='build file (default is team.json)')
@click.option('--verbose', default=False, is_flag=True, help='Verbose build')
def fetch_github(github_token, output_repos, output_readme, output_contributors, output_about, output_team, verbose):
    fetch_data = FetchData(github_token)
    start = time()
    repos = fetch_data.fetch_repos()
    if repos is None:
        logger.error("No repos fetched")
        return
    repos_count = fetch_data.save_to_file(repos, output_repos, output_readme, output_contributors, output_about, output_team, verbose)
    logger.info(f"Fetched {repos_count} repos in {time() - start:.2f} seconds")

@click.command(help='List repos from file - for debugging')
@click.option('--github-token', default=None, help='Github token (default is in .env file)')
@click.option('--input-file', default='data/repos.json', help='Input file (default is repos.json)')
def list(github_token, input_file):
    fetch_data = FetchData(github_token, input_file)
    repos = fetch_data.load_repo()
    if not repos:
        raise Exception("No repos loaded")

    print(f"Loaded {len(repos)} repos")
    pprint(repos)

@click.command(help='Generate web from repos')
@click.option('--github-token', default=None, help='Github token (default is in .env file)')
@click.option('--fetch-directly', default=False, is_flag=True, help='Fetch repos directly from github')
@click.option('--input-repos', default='data/repos.json', help='Input file (default is repos.json)')
@click.option('--input-readme', default='data/readme.json', help='Input file (default is readme.json)')
@click.option('--input-contributors', default='data/contributors.json', help='Input file (default is contributors.json)')
@click.option('--input-about', default='data/about.json', help='Input file (default is about.json)')
@click.option('--input-team', default='data/team.json', help='Input file (default is team.json)')
@click.option('--build-dir', '-o', default='build', help='build directory (default is build)')
@click.option('--template-dir', '-t', default='templates', help="Template directory (default is 'templates')")
@click.option('--static-dir', default='static', help="Static directory (default is 'static')")
@click.option('--project-dir', default='projects', help="Project directory (default is 'projects')")
@click.option('--hide-private', default=False, is_flag=True, help="Hide private repos")
@click.option('--verbose', default=False, is_flag=True, help='Verbose build')
@click.option('--compile-tailwind', default=False, is_flag=True, help='Compile tailwind (requires npx + tailwindcss)')
def generate(github_token: str, fetch_directly: bool, input_repos: str, input_readme:str, input_contributors:str, input_about:str, input_team:str, build_dir: str, template_dir: str, static_dir: str, project_dir: str, hide_private: bool, verbose: bool, compile_tailwind: bool):
    print(f"Generating web to {build_dir} directory")
    start = time()
    fetch_data = FetchData(github_token)
    if fetch_directly:
        repos = fetch_data.fetch_repos()
        readme = {
            repo.full_name: fetch_data.fetch_readme(repo)
            for repo in repos
        }

        contributors ={
            repo.full_name:
            [[contributor.html_url, contributor.avatar_url, contributor.name, contributor.login, contributor.contributions,] for contributor in fetch_data.fetch_contributors(repo)] for repo in repos
        }

        about_info = fetch_data.fetch_about_info()
        team = fetch_data.fetch_team()

    else:
        repos = fetch_data.load_repo(input_repos)
        readme = fetch_data.load_readme(input_readme)
        contributors = fetch_data.load_contributors(input_contributors)
        about_info = fetch_data.load_about(input_about)
        team = fetch_data.load_team(input_team)

    if not repos or not readme or not contributors or not team:
        raise Exception("No repos loaded")

    # sort repos by time of last push (newest to oldest)
    repos_w_time = []
    for repo in repos:
        repos_w_time.append((repo, max(repo.pushed_at, repo.updated_at)))

    sorted_repos = sorted(repos_w_time, key=lambda x: x[1], reverse=True)
    
    repos = [repo for repo, t in sorted_repos]

    generate_web = GenerateWeb(repos, readme, contributors, about_info, team, hide_private, verbose, compile_tailwind)
    # generate_web = GenerateWeb(repos, readme, contributors, about_info, team, build_dir, template_dir, static_dir, project_dir, hide_private, verbose, compile_tailwind)

    generate_web.generate()
    print(f"Generated web to {build_dir} directory in {time() - start:.2f} seconds")


@click.command(help='Serve generated web with livereload / without livereload')
@click.option('--port', default=8000, help='Port to serve on (default is 8000)')
@click.option('--host', default='localhost', help='Host to serve on (default is localhost)')
@click.option('--build-dir', default='build', help='build directory (default is build)')
@click.option('--no-livereload', default=False, is_flag=True, help='Disable live reload and serve only once')
def serve(port: int, host: str, build_dir: str, no_livereload: bool):
    os.chdir(build_dir)
    if no_livereload:
        import http.server
        import socketserver
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer((host, port), Handler) as httpd:
            httpd.allow_reuse_address = True
            print(f"Serving at http://{host}:{port}")
            httpd.serve_forever()
    else:
        import livereload
        server = livereload.Server()
        # watch everything in the build directory
        server.watch(".")
        print(f"Serving at http://{host}:{port}")
        server.serve(port=port, host=host)


cli.add_command(fetch_github)
cli.add_command(list)
cli.add_command(generate)
cli.add_command(serve)

if __name__ == '__main__':
    cli()