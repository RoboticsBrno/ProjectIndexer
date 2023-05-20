from django.shortcuts import render
from github import Github
from decouple import config

def list_repos(request):
    g = Github(config('GITHUB_TOKEN'))  # get the Github token from .env file
    organization = g.get_organization("RoboticsBrno")
    repos = organization.get_repos()
    return render(request, 'list.html', {'repos': repos})

def detail_repo(request, repo_name):
    g = Github(config('GITHUB_TOKEN'))  # get the Github token from .env file
    repo = g.get_repo(f"RoboticsBrno/{repo_name}")
    return render(request, 'detail.html', {'repo': repo})
