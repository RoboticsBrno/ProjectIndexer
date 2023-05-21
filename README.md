# ProjectIndexer
This is a RoboticsBrno indexer generator for out GitHub projects.
ProjectIndexer is a static web generator written in Python.
It generates a static web page with a list of all our projects based on the GitHub API.

## How to use it
1. Clone this repository
2. Install dependencies
3. create file `.env` with content `MY_GITHUB_TOKEN=your_github_token`
    - you can generate your token [here](https://github.com/settings/tokens?type=beta)
4. run `python3 project_indexer.py`

## ProjectIndexer options
- `fetch-github` - fetches data from GitHub API and saves it to `data/repos.json`
- `generate` - generates static web page from `data/repos.json` and saves it to `output` folder
- `serve` - serves the static web page from `output` folder