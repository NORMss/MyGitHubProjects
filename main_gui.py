import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import re
import json
import http.server
import socketserver
import webbrowser
import os

# Constants
HEADERS = {}
RATE_LIMIT = 5000
CONFIG_FILE = "config.json"

def set_headers(token):
    global HEADERS
    HEADERS = {'Authorization': f'token {token}'}

def get_repositories(username, per_page):
    url = f'https://api.github.com/users/{username}/repos?per_page={per_page}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching repositories: {response.status_code}")

def get_issues(repo_name, username):
    url = f'https://api.github.com/repos/{username}/{repo_name}/issues?state=all'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching issues for repo {repo_name}: {response.status_code}")

def extract_markdown_links(issue_body):
    if issue_body is None:
        return []
    markdown_link_pattern = r'\[(.*?)\]\((.*?)\)'
    links = re.findall(markdown_link_pattern, issue_body)
    return [{"text": link[0], "url": link[1]} for link in links]

def parse_github_data(username, per_page, include_issues, all_repos, progress_callback):
    if all_repos:
        per_page = 100  # GitHub API max per page
    repositories = get_repositories(username, per_page)
    result = {"repository": []}
    skipped_repos = []

    for i, repo in enumerate(repositories):
        progress_callback(i + 1, len(repositories))

        if 'name' not in repo or not isinstance(repo['name'], str):
            continue

        repo_issues_with_links = []
        repo_issues_without_links = []
        if include_issues:
            issues = get_issues(repo['name'], username)
            for issue in issues:
                issue_body = issue.get('body', None)
                links = extract_markdown_links(issue_body)
                if links:
                    issue_info = {
                        "title": f"{issue.get('title', 'No title')} #{issue.get('number', 'No number')}",
                        "description": issue_body.split("\n")[0] if issue_body else "No description",
                        "links": links
                    }
                    repo_issues_with_links.append(issue_info)
                else:
                    issue_info = {
                        "title": f"{issue.get('title', 'No title')} #{issue.get('number', 'No number')}",
                        "description": issue_body.split("\n")[0] if issue_body else "No description",
                        "links": []
                    }
                    repo_issues_without_links.append(issue_info)

        repo_info = {
            "name": repo.get('name', 'No name'),
            "description": repo.get('description', 'No description'),
            "url": repo.get('html_url', '#'),
            "created_at": repo.get('created_at', ''),
            "issues_with_links": repo_issues_with_links,
            "issues_without_links": repo_issues_without_links
        }
        result["repository"].append(repo_info)

        if not repo_issues_with_links and not repo_issues_without_links and include_issues:
            skipped_repos.append(repo.get('name', 'No name'))

    return result, skipped_repos

def save_config(username, token, per_page, include_issues, include_all_repos):
    config = {
        "username": username,
        "token": token,
        "per_page": per_page,
        "include_issues": include_issues,
        "include_all_repos": include_all_repos
    }
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    return {}

def start_local_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("Serving at port 8000")
        webbrowser.open("http://localhost:8000/")
        httpd.serve_forever()

def start_server_in_thread():
    server_thread = threading.Thread(target=start_local_server, daemon=True)
    server_thread.start()

# GUI Functions
def start_parsing():
    username = username_entry.get()
    token = token_entry.get()
    per_page = int(per_page_entry.get()) if not all_repos_var.get() else 0
    include_issues = issues_var.get()
    include_all_repos = all_repos_var.get()

    if not username or not token:
        messagebox.showerror("Error", "Username and Token are required!")
        return

    set_headers(token)
    save_config(username, token, per_page, include_issues, include_all_repos)

    def run():
        try:
            progress_bar["maximum"] = 100
            progress_label.config(text="Starting...")

            def update_progress(current, total):
                progress_bar["value"] = (current / total) * 100
                progress_label.config(text=f"Processing {current}/{total}")

            data, skipped = parse_github_data(username, per_page, include_issues, include_all_repos, update_progress)

            with open('github_projects.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)

            with open('skipped_repos.json', 'w') as skipped_file:
                json.dump({"skipped_repositories": skipped}, skipped_file, indent=4)        

            messagebox.showinfo("Success", "Parsing completed successfully!")

            start_server_in_thread()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0
            progress_label.config(text="")

    threading.Thread(target=run).start()

root = tk.Tk()
root.title("GitHub Repository Parser")
root.geometry("500x500")

# Load Config
config = load_config()

# Username
username_label = tk.Label(root, text="GitHub Username:")
username_label.pack(pady=5)
username_entry = tk.Entry(root, width=40)
username_entry.pack(pady=5)
username_entry.insert(0, config.get("username", ""))

# Token
token_label = tk.Label(root, text="GitHub Token:")
token_label.pack(pady=5)
token_entry = tk.Entry(root, width=40, show="*")
token_entry.pack(pady=5)
token_entry.insert(0, config.get("token", ""))

# Per Page
per_page_label = tk.Label(root, text="Number of Repositories:")
per_page_label.pack(pady=5)
per_page_entry = tk.Entry(root, width=10)
per_page_entry.pack(pady=5)
per_page_entry.insert(0, config.get("per_page", "150"))

# Include Issues
issues_var = tk.BooleanVar(value=config.get("include_issues", False))
issues_check = tk.Checkbutton(root, text="Include Issues", variable=issues_var)
issues_check.pack(pady=5)

# Include All Repos
all_repos_var = tk.BooleanVar(value=config.get("include_all_repos", False))
all_repos_check = tk.Checkbutton(root, text="Include All Repositories", variable=all_repos_var)
all_repos_check.pack(pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)
progress_label = tk.Label(root, text="")
progress_label.pack(pady=5)

# Start Button
start_button = tk.Button(root, text="Start Parsing", command=start_parsing)
start_button.pack(pady=20)

# Open Localhost Button
def open_localhost():
    webbrowser.open("http://localhost:8000/")

localhost_button = tk.Button(root, text="Open Localhost", command=open_localhost)
localhost_button.pack(pady=10)

root.mainloop()
