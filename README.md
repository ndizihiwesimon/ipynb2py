# ipynb2py

A Python script for batch converting Jupyter notebook files (`.ipynb`) to Python scripts (`.py`), with built-in support for processing student assignment submissions.

## Features

- **Batch Conversion**: Recursively converts all `.ipynb` files in a directory to `.py` files
- **Encoding Detection**: Automatically detects file encoding using `chardet` and converts to UTF-8
- **Archive Extraction**: Extracts nested zip files (useful for student submissions)
- **Smart Directory Handling**: Fixes incorrectly named directories (e.g., when students zip notebooks directly)
- **Cleanup**: Removes unnecessary files (PDFs, macOS metadata, checkpoint directories, virtual environments)
- **Colored Output**: Progress tracking with color-coded terminal messages for easy monitoring
- **Error Handling**: Gracefully handles corrupted or invalid notebook files

## Requirements

- **Anaconda** (base environment preferred)

## Installation

Ensure you're using the Anaconda base environment and install the required packages:

```bash
# Activate Anaconda base environment
conda activate base

# Install required packages
pip install nbformat nbconvert chardet
```

## Usage

1. Edit the script to set your input path:
   ```python
   zip_file = "./Assignment5/submissions.zip"  # Your zip file
   root_dir = "./Assignment5/submissions/"     # Output directory
   ```

2. Run the script:
   ```bash
   python miso-converter.py
   ```

## What It Does

1. **Extracts** the main submissions zip file
2. **Deletes** PDF files and macOS metadata files (`._*`)
3. **Extracts** individual student zip archives
4. **Fixes** directories with `.ipynb` extensions (from incorrectly zipped submissions)
5. **Removes** unnecessary directories (`.ipynb_checkpoints`, `__MACOSX`, `venv`, `env`, `virtualenv`, etc.)
6. **Converts** all `.ipynb` files to `.py` files with proper encoding
7. **Reports** progress with color-coded messages:
   - 🔵 Blue: Directory navigation
   - 🟢 Green: Notebook found/saved
   - 🟡 Yellow: Encoding operations
   - 🔵 Cyan: Conversion/extraction progress
   - 🔴 Red: File/directory deletions
   - 🟣 Magenta: Directory fixes (merge/rename)

## Output

For each notebook file, the script creates a corresponding Python file in the same directory. For example:
- `student_assignment.ipynb` → `student_assignment.py`

## Error Handling

The script will skip:
- Empty files
- Very small files (< 10 bytes)
- Corrupted or invalid notebooks
- Invalid zip files

Errors are logged to the console for review.
