import os
import zipfile
import nbformat
import chardet
import shutil

from nbconvert import PythonExporter

# ANSI color codes for terminal output
COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[94m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_MAGENTA = "\033[95m"


def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, "rb") as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result["encoding"]


def convert_to_utf8(file_path, source_encoding):
    """Convert a non-UTF-8 file to UTF-8."""
    with open(file_path, "r", encoding=source_encoding, errors="replace") as f:
        content = f.read()
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# Step 1: Extract submissions.zip to submissions directory
zip_file = "./Assignment5/submissions.zip"  # Replace with your zip file path
root_dir = "./Assignment5/submissions/"  # Replace with your folder path

if not os.path.exists(root_dir):
    os.makedirs(root_dir)

if os.path.exists(zip_file):
    print(f"{COLOR_CYAN}Extracting {zip_file} to {root_dir}{COLOR_RESET}")
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(root_dir)

# Step 2: Delete all .pdf files and macOS metadata files from the submissions directory
for dirpath, _, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith(".pdf") or file.startswith("._"):
            file_path = os.path.join(dirpath, file)
            print(f"{COLOR_RED}Deleting file: {file_path}{COLOR_RESET}")
            os.remove(file_path)

# Step 3: Extract each student's zip archive into a separate directory
for dirpath, _, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith(".zip") and not file.startswith("._"):
            zip_path = os.path.join(dirpath, file)
            extract_dir = os.path.join(dirpath, file.replace(".zip", ""))
            print(f"{COLOR_CYAN}Extracting {zip_path} to {extract_dir}{COLOR_RESET}")
            os.makedirs(extract_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            except zipfile.BadZipFile:
                print(f"Skipping invalid zip file: {zip_path}")
                continue

# Step 3.5: Fix directories with .ipynb extension (students who zipped notebooks directly)
for dirpath, dirnames, _ in os.walk(root_dir, topdown=False):
    for dirname in dirnames:
        if dirname.endswith(".ipynb"):
            old_path = os.path.join(dirpath, dirname)
            new_dirname = dirname.replace(".ipynb", "")
            new_path = os.path.join(dirpath, new_dirname)
            
            # If the new path already exists, merge contents
            if os.path.exists(new_path):
                print(f"{COLOR_MAGENTA}Merging {old_path} into existing {new_path}{COLOR_RESET}")
                for item in os.listdir(old_path):
                    src = os.path.join(old_path, item)
                    dst = os.path.join(new_path, item)
                    if os.path.isfile(src):
                        shutil.move(src, dst)
                    elif os.path.isdir(src):
                        shutil.move(src, dst)
                shutil.rmtree(old_path)
            else:
                print(f"{COLOR_MAGENTA}Renaming directory: {old_path} -> {new_path}{COLOR_RESET}")
                os.rename(old_path, new_path)

# Step 4: Remove all .ipynb_checkpoints and virtual environment directories
for dirpath, dirnames, _ in os.walk(root_dir):
    for dirname in list(dirnames):  # Create a copy to safely modify during iteration
        if dirname in (".ipynb_checkpoints", "__MACOSX", ".venv", ".env", "venv", "env", "virtualenv"):
            checkpoints_path = os.path.join(dirpath, dirname)
            print(f"{COLOR_RED}Deleting directory: {checkpoints_path}{COLOR_RESET}")
            shutil.rmtree(checkpoints_path)
            dirnames.remove(dirname)  # Prevent walking into deleted directories

# Step 5: Recursively walk through the directory and process the notebooks
for dirpath, _, filenames in os.walk(root_dir):
    print(f"{COLOR_BLUE}Currently in directory: {dirpath}{COLOR_RESET}")  # Check each directory
    for file in filenames:
        if file.endswith(".ipynb"):
            full_path = os.path.join(dirpath, file)
            print(f"{COLOR_GREEN}Found notebook: {full_path}{COLOR_RESET}")

            # Detect encoding of the file
            encoding = detect_encoding(full_path)
            print(f"{COLOR_YELLOW}Encoding detected: {encoding}{COLOR_RESET}")

            if encoding != "utf-8":
                print(f"{COLOR_YELLOW}Converting {full_path} from {encoding} to UTF-8{COLOR_RESET}")
                convert_to_utf8(full_path, encoding)

            # Check if file is empty or too small to be a valid notebook
            file_size = os.path.getsize(full_path)
            if file_size == 0:
                print(f"Skipping empty file: {full_path}")
                continue
            elif file_size < 10:  # Very small files are likely invalid
                print(
                    f"Skipping very small file (likely invalid): {full_path}"
                )
                continue

            print(f"{COLOR_CYAN}Converting: {full_path}{COLOR_RESET}")

            try:
                # Read the notebook using utf-8 encoding
                with open(full_path, "r", encoding="utf-8") as f:
                    notebook_content = nbformat.read(f, as_version=4)

                # Convert notebook to python script
                exporter = PythonExporter()
                script, _ = exporter.from_notebook_node(notebook_content)

                # Write the Python script
                py_file = full_path.replace(".ipynb", ".py")
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(script)
                print(f"{COLOR_GREEN}Saved as: {py_file}{COLOR_RESET}")

            except (
                UnicodeDecodeError,
                nbformat.reader.NotJSONError,
                ValueError,
            ) as e:
                print(f"Error processing notebook: {full_path} (Error: {e})")
                print("Skipping corrupted or invalid notebook file.")
                continue
