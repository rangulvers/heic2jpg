import os
import sys
import concurrent.futures
from PIL import Image
import typer
from loguru import logger
from tqdm import tqdm
import pyheif
import piexif

app = typer.Typer(add_completion=False)

MAX_THREADS = 4

def find_heic_files(directory):
    heic_files = []
    logger.info(f"Starting to scan for HEIC files in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".heic", ".heif")):
                heic_file_path = os.path.join(root, file)
                heic_files.append(heic_file_path)
    logger.info(f"Finished scanning. Total HEIC files found: {len(heic_files)}")
    return heic_files

def convert_heic_to_jpg(heic_path, jpg_path, overwrite=False, delete_original=False):
    if not overwrite and os.path.exists(jpg_path):
        logger.debug(f"JPEG already exists for {heic_path}, skipping conversion.")
        return True  # Indicate that the file was "processed"
    try:
        heif_file = pyheif.read(heic_path)
        image = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data,
            "raw", heif_file.mode, heif_file.stride,
        )
        # Preserve EXIF metadata
        exif_dict = {}
        for metadata in heif_file.metadata or []:
            if metadata['type'] == 'Exif':
                exif_dict = piexif.load(metadata['data'])
                break
        exif_bytes = piexif.dump(exif_dict) if exif_dict else None

        image.save(jpg_path, "JPEG", exif=exif_bytes)
        logger.debug(f"Successfully converted {heic_path} to {jpg_path}")

        if delete_original:
            os.remove(heic_path)
            logger.debug(f"Deleted original HEIC file: {heic_path}")

        return True  # Indicate success

    except Exception as e:
        logger.error(f"Error converting {heic_path}: {e}", exc_info=True)
        return False  # Indicate failure

def setup_logging(verbose: bool):
    logger.remove()
    level = "DEBUG" if verbose else "ERROR"
    logger.add(sys.stderr, level=level, enqueue=True)

    # Configure logger to work with tqdm
    class TqdmLoggingHandler:
        def __init__(self, level=level):
            self.level = level

        def write(self, message):
            tqdm.write(message.rstrip())

        def flush(self):
            pass

    logger.add(TqdmLoggingHandler(), level=level)

@app.command()
def main(
    directory: str = typer.Argument(..., help="Directory to scan for HEIC files"),
    output_dir: str = typer.Option(None, "--output-dir", "-o", help="Directory to save converted JPEG files"),
    overwrite: bool = typer.Option(False, "--overwrite", "-w", help="Overwrite existing JPEG files"),
    delete_original: bool = typer.Option(False, "--delete-original", "-d", help="Delete original HEIC files after conversion"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Converts all HEIC files in a directory (recursively) to JPEG format.
    """
    setup_logging(verbose)

    start_time = time.time()
    logger.info(f"Conversion process started for directory: {directory}")

    heic_files = find_heic_files(directory)

    if not heic_files:
        print("No HEIC files found.")
        return

    heic_files_to_convert = []
    for heic_file in heic_files:
        if output_dir:
            relative_path = os.path.relpath(heic_file, directory)
            jpg_file = os.path.join(output_dir, os.path.splitext(relative_path)[0] + '.jpg')
            os.makedirs(os.path.dirname(jpg_file), exist_ok=True)
        else:
            jpg_file = os.path.splitext(heic_file)[0] + '.jpg'

        if not overwrite and os.path.exists(jpg_file):
            continue  # Skip files that don't need conversion

        heic_files_to_convert.append((heic_file, jpg_file))

    total_files = len(heic_files_to_convert)
    if total_files == 0:
        print("All HEIC files have already been converted to JPEG.")
        return

    print(f"Total HEIC files to convert: {total_files}\nStarting conversion...")

    # Use a thread-safe counter
    success_counter = 0
    failure_counter = 0

    progress_bar = tqdm(total=total_files, unit="file", ncols=80)

    def task_wrapper(args):
        heic_file, jpg_file = args
        result = convert_heic_to_jpg(heic_file, jpg_file, overwrite, delete_original)
        progress_bar.update(1)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = list(executor.map(task_wrapper, heic_files_to_convert))

    progress_bar.close()

    # Count successes and failures
    success_counter = sum(results)
    failure_counter = total_files - success_counter

    print(f"\nConversion completed. Total files converted: {success_counter}/{total_files}")
    if failure_counter > 0:
        print(f"Failed conversions: {failure_counter}")

    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Conversion process completed in {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()
