import requests
import re
import json
import time

# Токен для аутентификации (если требуется)
GITHUB_TOKEN = 'https://github.com/settings/tokens'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Пользователь, для которого будем получать репозитории
USERNAME = 'github_username'

#Количество репозиториев
PER_PAGE = 150

# Лимит запросов GitHub API
RATE_LIMIT = 5000  # Проверяй свой лимит запросов

def get_repositories(username):
    url = f'https://api.github.com/users/{username}/repos?per_page={PER_PAGE}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении репозиториев: {response.status_code}")
        return []

def get_issues(repo_name):
    url = f'https://api.github.com/repos/{USERNAME}/{repo_name}/issues?state=all'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении issues для репозитория {repo_name}: {response.status_code}")
        return []

def extract_markdown_links(issue_body):
    if issue_body is None:
        return []
    
    markdown_link_pattern = r'\[(.*?)\]\((.*?)\)'
    links = re.findall(markdown_link_pattern, issue_body)
    return [{"text": link[0], "url": link[1]} for link in links]

def create_json_structure():
    repositories = get_repositories(USERNAME)
    result = {"repository": []}
    skipped_repos = []

    for repo in repositories:
        if 'name' not in repo or not isinstance(repo['name'], str):
            continue  # Пропускаем репозиторий, если нет корректного имени

        issues = get_issues(repo['name'])
        repo_issues_with_links = []
        
        for issue in issues:
            issue_body = issue.get('body', None)
            links = extract_markdown_links(issue_body)
            if links:  # Если есть ссылки, то парсим issue
                issue_info = {
                    "title": f"{issue.get('title', 'No title')} #{issue.get('number', 'No number')}",
                    "description": issue_body.split("\n")[0] if issue_body else "No description",  # Описание или заглушка
                    "links": links
                }
                repo_issues_with_links.append(issue_info)

        if repo_issues_with_links:
            repo_info = {
                "name": repo.get('name', 'No name'),
                "description": repo.get('description', 'No description'),
                "url": repo.get('html_url', '#'),
                "created_at": repo.get('created_at', ''),  # Добавляем дату создания
                "issues": repo_issues_with_links
            }
            result["repository"].append(repo_info)
        else:
            skipped_repos.append(repo.get('name', 'No name'))

        if len(result["repository"]) % 50 == 0:
            time.sleep(1)

    return result, skipped_repos

# Создаем JSON-документ
json_data, skipped_repos = create_json_structure()

# Сохраняем в файл JSON
with open('github_projects.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# Сохраняем список репозиториев, которые были пропущены
with open('skipped_repos.json', 'w') as skipped_file:
    json.dump({"skipped_repositories": skipped_repos}, skipped_file, indent=4)

print("JSON файл успешно создан!")
print("Пропущенные репозитории сохранены в 'skipped_repos.json'.")