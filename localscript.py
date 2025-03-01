# pylint: disable=missing-module-docstring,missing-function-docstring
import os
import datetime
import requests
from dotenv import load_dotenv
from win10toast import ToastNotifier

# Load environment variables
load_dotenv()
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")
APP = os.getenv("APP_TITLE")

def get_repos():
    """Fetch all repositories for the user."""
    print("Fetching all github repositories")
    url = f"https://api.github.com/users/{USERNAME}/repos"
    headers = {"Authorization": f"token {TOKEN}"}
    response = requests.get(url, headers=headers, timeout=10)
    return (
        [repo["name"] for repo in response.json()]
        if response.status_code == 200
        else []
    )


def check_last_commit(repo):
    """Check the latest commit date for a given repository."""
    print(f"Checking when was the last time a commit occurred for {repo}")
    url = f"https://api.github.com/repos/{USERNAME}/{repo}/commits"
    headers = {"Authorization": f"token {TOKEN}"}
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200 and response.json():
        last_commit_date = response.json()[0]["commit"]["committer"]["date"]
        last_commit_date = datetime.datetime.strptime(
            last_commit_date, "%Y-%m-%dT%H:%M:%SZ"
        ).date()
        return last_commit_date
    return None

def push_toast(title, body):
    toast = ToastNotifier()
    toast.show_toast(title, body, duration=20, threaded=True)

def check_global_commits():
    repos = get_repos()
    today = datetime.datetime.now(datetime.timezone.utc)

    pushed_today = any(check_last_commit(repo) == today for repo in repos)

    if pushed_today:
        msg =  "✅ Already pushed today across at least one repo!"
    else:
        msg = "❌ No GitHub push today! Commit something now."

    push_toast(APP, msg)
    print(msg)


if __name__ == "__main__":
    try:
        check_global_commits()
    except Exception: # pylint: disable=broad-exception-caught
        push_toast(APP, "Uh oh! App crashed")
    # push_toast(APP, "Hello, World!")
