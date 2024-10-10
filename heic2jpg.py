import os
import pyheif
from PIL import Image
import typer
import concurrent.futures
import time
from loguru import logger
import piexif

app = typer.Typer(add_completion=False)

# Limit the maximum number of threads to avoid overloading the NAS
MAX_THREADS = 8

# Default sleep interval to reduce the load on the NAS during directory traversal
SLEEP_INTERVAL = 0.01

def find_heic_files(directory, sleep_interval=SLEEP_INTERVAL):
    heic_files = []
    logger.info(f"Starting to scan for HEIC files in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".heic"):
                heic_file_path = os.path.join(root, file)
                heic_files.append(heic_file_path)
                logger.debug(f"Found HEIC file: {heic_file_path}")
        time.sleep(sleep_interval)  # Adding a slight delay to reduce NAS load
    logger.info(f"Finished scanning. Total HEIC files found: {len(heic_files)}")
    return heic_files

def convert_heic_to_jpg(heic_path, jpg_path, overwrite=False, delete_original=False):
    logger.debug(f"Processing file: {heic_path}")
    if not overwrite and os.path.exists(jpg_path):
        logger.debug(f"JPEG already exists for {heic_path}, skipping conversion.")
        return
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
        exif_bytes = piexif.dump(exif_dict)

        image.save(jpg_path, "JPEG", exif=exif_bytes)
        logger.info(f"Successfully converted {heic_path} to {jpg_path}")

        if delete_original:
            os.remove(heic_path)
            logger.info(f"Deleted original HEIC file: {heic_path}")

    except pyheif.error.HeifError as e:
        logger.error(f"HEIF error for {heic_path}: {e}")
    except OSError as e:
        logger.error(f"OS error for {heic_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during conversion of {heic_path}: {e}")

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
    # Adjust logging based on verbosity
    if verbose:
        logger.remove()
        logger.add(lambda msg: typer.echo(msg, err=True), level="DEBUG")
    else:
        logger.remove()
        logger.add(lambda msg: typer.echo(msg, err=True), level="INFO")

    start_time = time.time()
    logger.info(f"Conversion process started for directory: {directory}")

    heic_files = find_heic_files(directory)

    if not heic_files:
        logger.info("No HEIC files found.")
        return

    heic_files_to_convert = []
    for heic_file in heic_files:
        if output_dir:
            relative_path = os.path.relpath(heic_file, directory)
            jpg_file = os.path.join(output_dir, os.path.splitext(relative_path)[0] + '.jpg')
            os.makedirs(os.path.dirname(jpg_file), exist_ok=True)
        else:
            jpg_file = os.path.splitext(heic_file)[0] + '.jpg'

        heic_files_to_convert.append((heic_file, jpg_file))

    if not heic_files_to_convert:
        logger.info("All HEIC files have already been converted to JPEG.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for heic_file, jpg_file in heic_files_to_convert:
            futures.append(executor.submit(
                convert_heic_to_jpg,
                heic_file,
                jpg_file,
                overwrite=overwrite,
                delete_original=delete_original
            ))

        # Wait for all futures to complete
        concurrent.futures.wait(futures)

    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Conversion process completed in {total_time:.2f} seconds.")

if __name__ == "__main__":
    app()
