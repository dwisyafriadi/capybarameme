import requests
import time
import webbrowser  # To open URLs in the default web browser

def read_bearer_token():
    try:
        with open("bearer.txt", "r") as file:
            return file.read().strip()  # Read and remove any leading/trailing whitespace
    except FileNotFoundError:
        print("Error: bearer.txt file not found.")
        return None

def check_user_info():
    url = "https://api.capybarameme.com/auth/users/info"
    bearer_token = read_bearer_token()  # Read token from file

    if bearer_token is None:
        return  # Exit if token is not available

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US, en; q=0.9",
        "Authorization": f"Bearer {bearer_token}",
        "if-not-not-matched": 'W/"2bb-9jp25TAhbnPk9q1AXpeqcv437MA"',
        "origin": "https://bot.capybarameme.com",
        "priority": "u=1, i",
        "referrer": "https://bot.capybarameme.com/",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129", "Microsoft Edge WebView2";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        user_info = response.json()

        # Process and print user info
        user = user_info.get("user", {})
        print(f"User ID: {user.get('uid')}")
        print(f"Username: {user.get('uname')}")
        print(f"Total Score: {user.get('total_score')}")
        print(f"Locked Score: {user.get('locked_score')}")
        print(f"Invite Code: {user.get('invite_code')}")
        print(f"Account Age: {user.get('age')}")
        print(f"TON Address: {user.get('ton_address')}")

        # Print scores
        for score in user_info.get("score", []):
            print(f"{score.get('label')}: {score.get('score')}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def fetch_tasks():
    url = "https://api.capybarameme.com/auth/tasks/list"
    bearer_token = read_bearer_token()  # Read token from file

    if bearer_token is None:
        return  # Exit if token is not available

    headers = {
        "accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {bearer_token}",
        "origin": "https://bot.capybarameme.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        tasks_info = response.json()

        # Process and print tasks info
        task_list = []  # List to hold task names and types
        print("Tasks List:")
        for task_category in tasks_info:
            print(f"\nCategory: {task_category.get('title')} ({task_category.get('type')})")
            for task in task_category.get("list", []):
                completion_status = "Completed" if task.get("is_completed") else "Not Completed"
                print(f" - {task.get('label')} (Score: {task.get('score')}) - {completion_status}")
                
                # Check if URL exists and print it
                if task.get("url"):
                    print(f"   Link: {task.get('url')}")
                
                # Store the task name, type, and URL in the list for clearing
                task_list.append({
                    "name": task.get("name"),
                    "type": task_category.get("type"),
                    "url": task.get("url")  # Ensure URL is captured
                })

        return task_list  # Return the list of tasks

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def clear_task(task_name, task_type, task_url):
    url = "https://api.capybarameme.com/auth/tasks/submit"
    bearer_token = read_bearer_token()  # Read token from file

    if bearer_token is None:
        return  # Exit if token is not available

    headers = {
        "accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {bearer_token}",
        "origin": "https://bot.capybarameme.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }

    payload = {
        "name": task_name,
        "type": task_type,
    }

    print(f"Payload to clear task: {payload}")  # Log the payload

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        result = response.json()

        # Print the response message
        print(result.get("msg"))

    except requests.exceptions.HTTPError as e:
        if "daily check_in already completed" in e.response.text:
            print("Daily check_in has been claimed.")
            if task_url:
                print("Opening the task link...")
                webbrowser.open(task_url)  # Open the link in a web browser
                print("Waiting for 15 seconds...")
                time.sleep(3)  # Wait for 15 seconds before continuing
            else:
                print("No URL available to open for this task.")
        else:
            # Log the full response content for debugging
            print(f"Error: {e} - Response: {e.response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_info()
    tasks = fetch_tasks()  # Get the list of tasks
    if tasks:
        for task in tasks:
            print(f"Task Name: {task['name']}, Task Type: {task['type']}, Task URL: {task.get('url')}")
            if task.get('url'):  # Ensure URL exists
                # Click "Go" by opening the URL first
                print(f"Opening task link for: {task['name']}")
                webbrowser.open(task['url'])  # Open the task link
                print("Waiting for 15 seconds...")
                time.sleep(3)  # Wait for 15 seconds after opening the link
                # Then attempt to clear the task
                clear_task(task["name"], task["type"], task.get("url"))
            else:
                print("No URL available for this task.")
