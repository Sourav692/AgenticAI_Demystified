import os
import logging
from mcp.server.fastmcp import FastMCP
from typing import List

# Define the file where tasks will be stored
TASKS_FILE = "tasks.txt"

# Initialize the FastMCP server with a descriptive name
mcp = FastMCP("TaskManagementAssistant")

@mcp.tool()
def add_task(task_description: str) -> str:
    """
    Adds a new task to the persistent task list file.

    This tool will create the task file if it doesn't exist. It appends
    the new task to the end of the file, ensuring each task is on a new line.

    Args:
        task_description: A string describing the task to be added.
                          For example: "Buy groceries" or "Finish the report".

    Returns:
        A string confirming that the task was successfully added.
    """
    try:
        # 'a' mode will append to the file, and create it if it doesn't exist
        with open(TASKS_FILE, "a") as f:
            f.write(f"{task_description}\n")
        return f"Task '{task_description}' was added successfully."
    except Exception as e:
        return f"An error occurred while adding the task: {e}"

@mcp.tool()
def list_tasks() -> List[str]:
    """
    Lists all the tasks from the persistent task list file.

    This tool reads all tasks from the file. If the file does not exist or
    is empty, it returns an empty list.

    Returns:
        A list of strings, where each string is a task. Returns an empty
        list if no tasks are found.
    """
    if not os.path.exists(TASKS_FILE):
        # Return an empty list if the file doesn't exist, as there are no tasks
        # The LLM can interpret this as "no tasks to show"
        return []

    try:
        with open(TASKS_FILE, "r") as f:
            # Read all lines, and strip leading/trailing whitespace (like newlines)
            tasks = [line.strip() for line in f.readlines()]
            # Filter out any empty lines that might have been created
            return [task for task in tasks if task]
    except Exception as e:
        # In case of an error, we can return a list with an error message,
        # but for simplicity and better type consistency, we'll return an empty list.
        # The LLM can be prompted to handle this gracefully
        print(f"Error reading tasks file: {e}")
        return []

if __name__ == "__main__":
    logging.getLogger("mcp").setLevel(logging.WARNING)
    # The server will run and listen for requests from the client over stdio
    mcp.run(transport="stdio")