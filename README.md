# HEIC to JPEG Converter

A Python script to convert all HEIC files in a directory (and its subdirectories) to JPEG format, with options to preserve metadata, overwrite existing files, delete original files after conversion, and specify an output directory.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Conversion](#basic-conversion)
  - [Options](#options)
  - [Examples](#examples)
- [Notes](#notes)
- [License](#license)

---

## Features

- **Batch Conversion**: Converts all HEIC files in a directory and its subdirectories to JPEG.
- **Metadata Preservation**: Preserves EXIF metadata from the original HEIC files.
- **Overwrite Control**: Option to overwrite existing JPEG files.
- **Original File Deletion**: Option to delete original HEIC files after successful conversion.
- **Custom Output Directory**: Specify an output directory for the converted JPEG files.
- **Verbose Logging**: Provides detailed logging output for monitoring and debugging.

---

## Prerequisites

- **Python 3.6 or higher**

- **Required Python Libraries**:
  - `pyheif`
  - `Pillow` (PIL)
  - `typer`
  - `loguru`
  - `piexif`

---

## Installation

1. **Clone the Repository or Download the Script**

   Download the `heic2jpg.py` script to your local machine.

2. **Set Up a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use "venv\Scripts\activate"
   ```

3. **Install Required Libraries**

   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, install the libraries individually:

   ```bash
   pip install pyheif Pillow typer loguru piexif
   ```

---

## Usage

### Basic Conversion

To convert all HEIC files in a directory to JPEG format:

```bash
python3 heic2jpg.py [OPTIONS] DIRECTORY
```

- `DIRECTORY`: The path to the directory containing HEIC files to convert.

### Options

- `--output-dir`, `-o`:

  Specify an output directory to save the converted JPEG files. If not provided, JPEG files will be saved alongside the original HEIC files, maintaining the directory structure.

  ```bash
  --output-dir /path/to/output/directory
  ```

- `--overwrite`, `-w`:

  Overwrite existing JPEG files if they already exist.

  ```bash
  --overwrite
  ```

- `--delete-original`, `-d`:

  Delete the original HEIC files after successful conversion to JPEG.

  ```bash
  --delete-original
  ```

- `--verbose`, `-v`:

  Enable verbose output for detailed logging. Useful for debugging or monitoring the conversion process.

  ```bash
  --verbose
  ```

- `--help`, `-h`:

  Show help message and exit.

  ```bash
  --help
  ```

### Examples

#### Example 1: Basic Conversion

Convert all HEIC files in `./photos` to JPEG format, saving them alongside the original files.

```bash
python3 heic2jpg.py ./photos
```

#### Example 2: Specify Output Directory

Convert HEIC files in `./photos` and save the JPEG files in `./JPEGs`, preserving the directory structure.

```bash
python3 heic2jpg.py --output-dir ./JPEGs ./photos
```

#### Example 3: Overwrite Existing JPEGs

Convert HEIC files and overwrite any existing JPEG files with the same name.

```bash
python3 heic2jpg.py --overwrite ./photos
```

#### Example 4: Delete Original HEIC Files After Conversion

Convert HEIC files and delete the original HEIC files after successful conversion.

```bash
python3 heic2jpg.py --delete-original ./photos
```

#### Example 5: Combine Options

Convert HEIC files, overwrite existing JPEGs, delete original HEIC files, and save JPEGs to a specified output directory with verbose logging.

```bash
python3 heic2jpg.py --overwrite --delete-original --output-dir ./JPEGs --verbose ./photos
```

#### Example 6: Handling Paths with Spaces

If your directory path contains spaces, enclose it in double quotes:

```bash
python3 heic2jpg.py "/path/to/your directory with spaces"
```

---

## Notes

- **Performance Considerations**:

  - The script uses multithreading to speed up the conversion process.
  - The default maximum number of threads is set to 4 to avoid overloading the system or network storage devices (NAS).
  - You can adjust the `MAX_THREADS` variable in the script if needed.

- **Preserving Metadata**:

  - EXIF metadata from the original HEIC files is preserved in the converted JPEG files, including camera settings, GPS location, and timestamps.

- **Logging**:

  - The script uses `loguru` for logging.
  - Logs are printed to the console. Adjust the logging configuration in the script if you want to log to a file.
  - Use the `--verbose` flag to see detailed logs for each file processed.

- **Error Handling**:

  - The script handles common errors gracefully, logging any issues encountered during conversion without stopping the entire process.
  - Errors are logged with descriptive messages to help identify problematic files.

- **Dependencies**:

  - Ensure all the required libraries are installed and up to date to prevent compatibility issues.
  - If you encounter installation issues with `pyheif` or `Pillow`, make sure you have the necessary system libraries for image processing.

- **Permissions**:

  - Ensure you have read and write permissions for the directories you're accessing and writing to.
  - Be cautious when using the `--delete-original` option to avoid unintended data loss.

---


**Disclaimer**: Use this script at your own risk. Always back up your files before performing batch operations that modify or delete files.

---
