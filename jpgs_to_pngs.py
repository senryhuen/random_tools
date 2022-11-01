"""Converts JPG/JPEGs to PNGs

This script will losslessly convert all JPG/JPEG images in a given folder
(including sub-folders) into PNG images, with the option to delete or keep the
original files. It can also save the EXIF metadata from the original image to
a text file. The PNG file format does not support embedding EXIF data (it
supports metadata in the form of 'text chunks', but reading of that metadata
is not well supported so storing in a text file may be more future-proof).

This script requires that `Pillow`, 'exif' and 'Send2Trash' be installed
within the Python environment you are running this script in.

Contains the following functions:

    * convert_jpgs_to_pngs - converts all JPG/JPEGs in a list of JPG filepaths
        into PNGs, and optionally saving its metadata to a text file, returns
        list of files converted and list of files that already existed
    * save_jpg_metadata_to_txt_file - saves EXIF metadata of JPG/JPEG image to
        a text file
    * main - main function with provides an interface to run the script and
        select options

"""

from PIL import Image
from exif import Image as exifImage
from send2trash import send2trash
import pathlib
import os


def convert_jpgs_to_pngs(jpg_filepaths: list, save_metadata_txtfile: bool = False) -> tuple[list, list]:
    """Losslessly converts all JPG/JPEGs in `jpg_filepaths` to PNGs

    Keeps and does not alter the original images. New images are created. The
    new files will be in the same location and have the same filenames but with
    the extension '.png' rather than '.jpg' or '.jpeg'.

    Args:
        jpg_filepaths (list of strings): List of filepaths of JPG/JPEG images
            to be converted into PNGs. Non JPG/JPEG files are ignored.
        save_metadata_txtfile (bool, optional): Whether to save EXIF metadata
            of original images or not. Defaults to False.

    Returns:
        tuple[list, list]: two lists, the first is a list of all images that were
            converted successfully, and the second is a list of all images for
            which a PNG version already existed and was skipped.

    """
    converted_jpgs = []
    existing_pngs = []

    for jpg in jpg_filepaths:
        new_name = os.path.splitext(str(jpg))[0] + ".png"

        if os.path.exists(new_name):
            existing_pngs.append(new_name)
            continue

        with Image.open(jpg) as img:
            img.save(r"{}".format(new_name), compress_level=0)

        if save_metadata_txtfile:
            new_name_txt = os.path.splitext(str(jpg))[0] + ".txt"
            save_jpg_metadata_to_txtfile(jpg, new_name_txt)

        converted_jpgs.append(jpg)
    
    return converted_jpgs, existing_pngs


def save_jpg_metadata_to_txtfile(jpg_filepath, save_path):
    """Saves EXIF metadata of JPG/JPEG image to text file

    If the image does not contain any metadata, it will be skipped.

    Args:
        jpg_filepath (string): File path of a JPG/JPEG image to save metadata
            for.
        save_path (string): File path of text file to be created, where the
            metadata will be saved to. Must not already exist.
    
    Returns:
        (int): True if metadata was saved successfully, False if image was skipped.

    Raises:
        ValueError: If `jpg_filepath` is not a .txt file.

    """
    if os.path.splitext(save_path)[1] != ".txt":
        raise ValueError(f"save_path: Must be a .txt file. '{save_path}' is not a txt file.")

    if os.path.exists(save_path):
        print(f"save_path: '{save_path}' file already exists.")
        print(f"Skipped '{jpg_filepath}'")
        return False

    with open(jpg_filepath, 'rb') as image_file:
        img_exif = exifImage(image_file)  

    if img_exif.has_exif:
        with open(save_path, "w+") as write_file:
            write_file.write(f"\"{os.path.splitext(os.path.basename(save_path))[0]}\"\n")
            for exif_tag in img_exif.list_all():
                write_file.write(f"{exif_tag} : {str(img_exif.get(exif_tag))}\n")
        return True
    else:
        print(f"jpg_filepath: Image '{jpg_filepath}' does not have EXIF metadata")
        print(f"Skipped '{jpg_filepath}'")
        return False


def main():
    search_path = input("Enter path to a directory containing jpgs/jpegs to convert to .PNG: ")
    image_paths = list(pathlib.Path(search_path).rglob("*.jpg")) + list(pathlib.Path(search_path).rglob("*.jpeg"))
    converted_jpgs, existing_pngs = convert_jpgs_to_pngs(image_paths)
    converted_jpgs_count = len(converted_jpgs)
    existing_pngs_count = len(existing_pngs)

    if converted_jpgs_count == 0 and existing_pngs_count == 0:
        print("No JPGs Found")
    else:
        print(converted_jpgs_count, "JPGs converted to PNGs")
        if existing_pngs_count != 0:
            print(existing_pngs_count, "JPG conversions already exist and were not converted")

        # Shows which JPGs were/not converted to PNGs
        ask = input("Would you like to see a list of these? (Press Space to View)")
        if ask == " ":
            if converted_jpgs_count > 0:
                print("\nJPGs Converted:")
                for i in converted_jpgs:
                    print(i)
            if existing_pngs_count > 0:
                print("\nJPGs Not Converted:")
                for o in existing_pngs:
                    print(o)

        # Option to delete original JPGs (if applicable)
        if converted_jpgs_count > 0:
            ask = input("Would you like to delete the original JPGs? (Press Space to Delete)")
            if ask == " ":
                send2trash(converted_jpgs)
                print(len(converted_jpgs), "JPGs deleted")


if __name__ == "__main__":
    main()
