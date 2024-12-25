import argparse

# Create parser
parser = argparse.ArgumentParser(description='CAT server URL')

# Create mutually exclusive group for server configurations
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--local', action='store_true', help='Use local server (http://localhost:8000)')
group.add_argument('--remote', nargs=2, metavar=('SERVER_URL', 'API_KEY'),
                  help='Remote server URL and API key')

args = parser.parse_args()

if args.local:
    SERVER_URL = 'http://localhost:8000'
    API_KEY = None
else:
    SERVER_URL, API_KEY = args.remote

# Rest of your code
print(f"Connected to server: {SERVER_URL}")
if API_KEY:
    print(f"Using API key: {API_KEY}")




from TaskExecutor.TaskExecutor import TaskExecutor


taskExecutor = TaskExecutor(SERVER_URL, API_KEY)
task = taskExecutor.create_task()
taskExecutor.open_webpage()

idx = 0
while True:
    screenshot_path = taskExecutor.take_screenshot(idx)
    response = taskExecutor.request(screenshot_path, task)
    result = taskExecutor.save_result_files(response,idx)
    taskExecutor.perform_action(result)
    idx+=1

    