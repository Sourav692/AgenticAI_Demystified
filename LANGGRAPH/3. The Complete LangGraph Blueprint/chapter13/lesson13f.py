import os
import time
import logging
import pandas as pd
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_openai import OpenAIEmbeddings
import psycopg2
from table_config import TABLE_CONFIG
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="audit_data_monitor.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Validate environment variables
def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        logging.error(f"Environment variable '{var_name}' is not set.")
        raise EnvironmentError(f"Environment variable '{var_name}' is required.")
    return value

# Database connection configuration
DB_CONFIG = {
    "dbname": get_env_var("DB_NAME"),
    "user": get_env_var("DB_USER"),
    "password": get_env_var("DB_PASSWORD"),
    "host": get_env_var("DB_HOST"),
    "port": get_env_var("DB_PORT"),
}

# Persistent file tracking setup
LOADED_FILES_PATH = ".loaded_files"
loaded_files = set()

def load_previous_files():
    """Load previously tracked files to avoid re-processing."""
    if os.path.exists(LOADED_FILES_PATH):
        with open(LOADED_FILES_PATH, "r") as f:
            loaded_files.update(line.strip() for line in f)
    logging.info(f"Loaded files from previous session: {loaded_files}")

def save_loaded_files():
    """Save the list of loaded files for persistence across sessions."""
    with open(LOADED_FILES_PATH, "w") as f:
        for file_name in loaded_files:
            f.write(file_name + "\n")

# Function to handle data loading and embedding
def load_and_embed_data(file_path: str, table_name: str, text_fields: list):
    try:
        df = pd.read_csv(file_path)
        with psycopg2.connect(**DB_CONFIG) as conn:
            for index, row in df.iterrows():
                text_for_embedding = " ".join([str(row[field]) for field in text_fields])
                embedding = OpenAIEmbeddings().embed_query(text_for_embedding)

                # Prepare SQL insertion with embedding
                insert_query = f"""
                INSERT INTO {table_name} (
                    {', '.join(df.columns)}, embedding
                ) VALUES (
                    {', '.join(['%s' for _ in range(len(df.columns))])}, %s
                ) ON CONFLICT (recordid) DO UPDATE SET
                    {', '.join([f"{col} = EXCLUDED.{col}" for col in df.columns])},
                    embedding = EXCLUDED.embedding
                """
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(insert_query, [*row, embedding])
                    conn.commit()
                except Exception as e:
                    logging.error(f"Error inserting row {index} from {file_path}: {e}")

        logging.info(f"Successfully loaded and embedded data from {file_path} into {table_name}.")
    except Exception as e:
        logging.error(f"Failed to load and embed data from {file_path}: {e}")

# Handler for new file events
class AuditDataHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_name = os.path.basename(event.src_path)
        if file_name in TABLE_CONFIG and file_name not in loaded_files:
            config = TABLE_CONFIG[file_name]
            load_and_embed_data(
                file_path=event.src_path,
                table_name=config["table"],
                text_fields=config["text_fields"]
            )
            loaded_files.add(file_name)
            save_loaded_files()

# Load and process existing files in the directory
def process_existing_files(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name in TABLE_CONFIG and file_name not in loaded_files:
            config = TABLE_CONFIG[file_name]
            load_and_embed_data(
                file_path=file_path,
                table_name=config["table"],
                text_fields=config["text_fields"]
            )
            loaded_files.add(file_name)
    save_loaded_files()

# Folder monitoring setup
def monitor_audit_data_folder():
    folder_name = get_env_var("AUDIT_FOLDER")
    folder_path = os.path.join(os.getcwd(), folder_name)

    try:
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Error: Folder '{folder_path}' not found in the current working directory.")
        
        load_previous_files()
        process_existing_files(folder_path)

        # Set up observer for new files
        event_handler = AuditDataHandler()
        observer = Observer()
        observer.schedule(event_handler, folder_path, recursive=False)
        observer.start()
        logging.info(f"Monitoring folder: {folder_path}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Shutting down folder monitor.")
            observer.stop()
        observer.join()

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Run the monitor
if __name__ == "__main__":
    monitor_audit_data_folder()
