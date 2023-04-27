import { Octokit } from '@octokit/core';
// @ts-ignore
import {marked} from 'marked';

import * as dotenv from 'dotenv'
dotenv.config()

// @ts-ignore
import express, { Request, Response } from 'express';

// use ENV variable
// please set GITHUB_TOKEN in your environment variables or in .env file
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_ORG = 'RoboticsBrno';

const octokit = new Octokit({ auth: GITHUB_TOKEN });
const app = express();
const port = process.env.PORT || 3000;



app.get('/', async (req: Request, res: Response) => {
    // http://localhost:3000/?topic=servo
    const topic = req.query.topic as string | undefined;
    let topics = topic ? [topic] : ["servo"];
    try {
        const searchResults = await octokit.request('GET /search/repositories', {
            q: `org:${GITHUB_ORG} topic:${topics.join(' topic:')}`,
            per_page: 100,
        });

        const repos = searchResults.data.items;

        const reposList = repos
            .map(
                (repo: any) =>
                    `<li>
                        <a href="${repo.html_url}" target="_blank">${repo.name}</a> [<a href="/readme?repo=${repo.full_name}">README</a>] [<a href="/info?repo=${repo.full_name}">Info</a>]
                        <p>${repo.description || 'No description available'}</p>
                        <p>Stars: ${repo.stargazers_count}</p>
                        <p>Language: ${repo.language}</p>
                        <p>Created: ${new Date(repo.created_at).toLocaleDateString()}</p>
                        <p>Updated: ${new Date(repo.updated_at).toLocaleDateString()}</p>
                        <p>
                    </li>`,
            )
            .join('');

        res.send(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Organization Repositories with Selected Topic</title>
          <style>
            /* ... */
          </style>
        </head>
        <body>
          <h1>Repositories with Topic: ${topics.join(', ')}</h1>
          <ul>${reposList}</ul>
        </body>
      </html>
    `);
    } catch (error: unknown) {
        console.error('Failed to fetch repositories:', error);
        res.status(500).send('Failed to fetch repositories from GitHub');
    }
});


app.get('/readme', async (req: Request, res: Response) => {
    // http://localhost:3000/readme?repo=JakubAndrysek/PySpaceMouse
    let githubRepo = req.query.repo as string
    if (!githubRepo) {
        githubRepo = "JakubAndrysek/PySpaceMouse";
    }
    try {
        const [owner, repo] = githubRepo.split('/');

        const readmeResponse = await octokit.request('GET /repos/{owner}/{repo}/readme', {
            owner,
            repo,
            headers: {
                Accept: 'application/vnd.github.VERSION.raw',
            },
        });

        const readmeMarkdown = readmeResponse.data;
        const readmeHtml = marked(readmeMarkdown.toString());
        res.send(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>GitHub README</title>
        </head>
        <body>
          <div>${readmeHtml}</div>
        </body>
      </html>
    `);
    } catch (error: any) {
        console.error('Failed to fetch README:', error.message);
        res.status(500).send('Failed to fetch README from GitHub');
    }
});

app.get('/info', async (req: Request, res: Response) => {
    // http://localhost:3000/info?repo=RoboticsBrno/RB3206-ELKS
    let githubRepo = req.query.repo as string
    if (!githubRepo) {
        githubRepo = "JakubAndrysek/PySpaceMouse";
    }
    try {
        const [owner, repo] = githubRepo.split('/');

        const repoInfo = await octokit.request('GET /repos/{owner}/{repo}', {
            owner,
            repo,
        });

        res.send(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>GitHub Repository Information</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              line-height: 1.6;
            }
            table {
              width: 100%;
              border-collapse: collapse;
            }
            th, td {
              padding: 12px;
              border: 1px solid #ccc;
            }
            th {
              background-color: #f4f4f4;
            }
          </style>
        </head>
        <body>
          <h1>Repository Information</h1>
          <table>
            <tr>
              <th>Name</th>
              <td>${repoInfo.data.name}</td>
            </tr>
            <tr>
              <th>Full Name</th>
              <td>${repoInfo.data.full_name}</td>
            </tr>
            <tr>
              <th>Description</th>
              <td>${repoInfo.data.description}</td>
            </tr>
            <tr>
              <th>URL</th>
              <td><a href="${repoInfo.data.html_url}" target="_blank">${repoInfo.data.html_url}</a></td>
            </tr>
            <tr>
              <th>Clone URL</th>
              <td>${repoInfo.data.clone_url}</td>
            </tr>
            <tr>
              <th>Created At</th>
              <td>${repoInfo.data.created_at}</td>
            </tr>
            <tr>
              <th>Updated At</th>
              <td>${repoInfo.data.updated_at}</td>
            </tr>
            <tr>
              <th>Stars</th>
              <td>${repoInfo.data.stargazers_count}</td>
            </tr>
            <tr>
              <th>Forks</th>
              <td>${repoInfo.data.forks_count}</td>
            </tr>
            <tr>
              <th>Watchers</th>
              <td>${repoInfo.data.watchers_count}</td>
            </tr>
            <tr>
              <th>Language</th>
              <td>${repoInfo.data.language}</td>
            </tr>
            <tr>
                <th>Homepage</th>
                <td>${repoInfo.data.homepage}</td>
            </tr>
          </table>
          <h2>Tags</h2>
            <ul>
                ${repoInfo?.data?.topics?.map((topic: string) => `<li>${topic}</li>`).join('')}
            </ul>
        </body>
      </html>
    `);
    } catch (error: any) {
        console.error('Failed to fetch repository information:', error.message);
        res.status(500).send('Failed to fetch repository information from GitHub');
    }
});



app.get('/org-repos-old', async (req: Request, res: Response) => {
    // http://localhost:3000/org-repos-old?topic=servo
    const topic = req.query.topic as string | undefined;
    let topics = topic ? [topic] : ["servo"];
    try {
        const repoResponse = await octokit.request('GET /orgs/{org}/repos', { org: GITHUB_ORG, per_page: 100 });
        const repos = repoResponse.data;

        const reposWithSelectedTopics = (await Promise.all(
            repos.map(async (repo: any) => {
                const topicsResponse = await octokit.request('GET /repos/{owner}/{repo}/topics', {
                    owner: repo.owner.login,
                    repo: repo.name,
                    mediaType: {
                        previews: ['mercy'],
                    },
                });

                const hasSelectedTopics = topics.every((topic) => topicsResponse.data.names.includes(topic));

                return hasSelectedTopics ? repo : null;
            }),
        )).filter((repo: any) => repo !== null);

        const reposList = reposWithSelectedTopics
            .map((repo: any) => `<li><a href="${repo.html_url}" target="_blank">${repo.name}</a></li>`)
            .join('');

        res.send(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Organization Repositories with Selected Topics</title>
          <style>
            /* ... */
          </style>
        </head>
        <body>
          <h1>Repositories with Topics: ${topics.join(', ')}</h1>
          <ul>${reposList}</ul>
        </body>
      </html>
    `);
    } catch (error: unknown) {
        // ...
    }
});

app.get('/org-tag-slow', async (req: Request, res: Response) => {
    // http://localhost:3000/org-tag-slow?orgName=RoboticsBrno&tag=alks
    const orgName = req.query.orgName as string | undefined;
    const selectedTag = req.query.tag as string | undefined;

    if (!orgName || !selectedTag) {
        res.status(400).send('orgName and tag query parameters are required');
        return;
    }

    try {
        // Fetch all repositories from the organization
        const repos = await fetchOrgRepositories(orgName);

        // Filter repositories that have the selected tag
        const filteredRepos = await filterReposByTag(repos, selectedTag);

        // Render the filtered repositories
        res.send(renderRepos(filteredRepos));
    } catch (error: unknown) {
        if (error instanceof Error) {
            console.error('Failed to fetch organization repositories:', error.message);
        } else {
            console.error('Failed to fetch organization repositories:', error);
        }
        res.status(500).send('Failed to fetch organization repositories');
    }
});


async function fetchOrgRepositories(orgName: string): Promise<any[]> {
    const allRepos: any[] = [];
    let page = 1;

    while (true) {
        const { data: repos } = await octokit.request('GET /orgs/{org}/repos', {
            org: orgName,
            per_page: 100,
            page,
        });

        if (repos.length === 0) {
            break;
        }

        allRepos.push(...repos);
        page++;
    }

    return allRepos;
}

async function filterReposByTag(repos: any[], selectedTag: string): Promise<any[]> {
    const filteredRepos = [];

    for (const repo of repos) {
        const topics = await octokit.request('GET /repos/{owner}/{repo}/topics', {
            owner: repo.owner.login,
            repo: repo.name,
        });

        if (topics.data.names.includes(selectedTag)) {
            filteredRepos.push(repo);
        }
    }

    return filteredRepos;
}

function renderRepos(repos: any[]): string {
    const repoList = repos
        .map(
            (repo) => `
        <li>
          <a href="${repo.html_url}" target="_blank">${repo.full_name}</a>
        </li>`
        )
        .join('');

    return `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Repositories with Selected Tag</title>
      </head>
      <body>
        <h1>Repositories with Selected Tag</h1>
        <ul>${repoList}</ul>
      </body>
    </html>`;
}

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
