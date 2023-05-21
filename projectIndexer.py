import os
from os import path, chdir
import click
from src.fetch_data import FetchData
from src.generate_web import GenerateWeb
from pprint import pprint
from time import time

@click.group()
def cli():
    pass

@click.command(help='Save repos from RoboticsBrno organization to file')
@click.option('--github-token', default=None, help='Github token (default is in .env file)')
@click.option('--output-file', default='data/repos.json', help='Output file (default is repos.json)')
@click.option('--verbose', default=False, help='Verbose output')
def fetch_github(github_token, output_file, verbose):
    fetch_data = FetchData(github_token, output_file)
    start = time()
    repos = fetch_data.fetch_repos()
    if repos is None:
        print("No repos fetched")
        return
    repos_count = fetch_data.save_to_file(repos, verbose=verbose)
    print(f"Fetched {repos_count} repos in {time() - start:.2f} seconds")

@click.command(help='List repos from file - for debugging')
@click.option('--github-token', default=None, help='Github token (default is in .env file)')
@click.option('--input-file', default='data/repos.json', help='Input file (default is repos.json)')
def list(github_token, input_file):
    fetch_data = FetchData(github_token, input_file)
    repos = fetch_data.load_from_file()
    print(f"Loaded {len(repos)} repos")
    pprint(repos)

@click.command(help='Generate web from repos')
@click.option('--github-token', default=None, help='Github token (default is in .env file)')
@click.option('--input-file', default='data/repos.json', help='Input file (default is repos.json)')
@click.option('--output-dir', '-o', default='output', help='Output directory (default is output)')
@click.option('--template-dir', '-t', default='templates', help="Template directory (default is 'templates')")
@click.option('--static-dir', default='static', help="Static directory (default is 'static')")
@click.option('--hide-private', default=False, is_flag=True, help="Hide private repos")
def generate(github_token: str, input_file: str, output_dir: str, template_dir: str, static_dir: str, hide_private: bool):
    fetch_data = FetchData(github_token, input_file)
    repos = fetch_data.load_from_file()

    generate_web = GenerateWeb(repos, output_dir, path.abspath(template_dir), static_dir, hide_private)

    start = time()
    generate_web.generate()
    print(f"Generated web to {output_dir} directory in {time() - start:.2f} seconds")


@click.command(help='Serve generated web with livereload / without livereload')
@click.option('--port', default=8000, help='Port to serve on (default is 8000)')
@click.option('--host', default='localhost', help='Host to serve on (default is localhost)')
@click.option('--output-dir', default='output', help='Output directory (default is output)')
@click.option('--no-livereload', default=False, help='Disable live reload and serve only once')
def serve(port: int, host: str, output_dir: str, no_livereload: bool):
    chdir(output_dir)
    if no_livereload:
        import http.server
        import socketserver
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer((host, port), Handler) as httpd:
            print(f"Serving at http://{host}:{port}")
            httpd.serve_forever()
    else:
        import livereload
        server = livereload.Server()
        # watch everything in the output directory
        server.watch(".")
        print(f"Serving at http://{host}:{port}")
        server.serve(port=port, host=host)


cli.add_command(fetch_github)
cli.add_command(list)
cli.add_command(generate)
cli.add_command(serve)

if __name__ == '__main__':
    cli()