import argparse
import os

from PIL import Image
from tqdm import tqdm

from helpers.files import IsImageFile


def resize_image(image_path: str, max_size: int):
    """Przeskalowuje obraz, jeśli jest większy niż podany rozmiar."""
    try:
        with Image.open(image_path) as img:
            # Check : Is image is not bigger than max_size
            if (img.width <= max_size) and (img.height <= max_size):
                return

            # Aspect ratio, new width and height
            if img.width > img.height:
                new_width = max_size
                new_height = int(max_size * img.height / img.width)
            else:
                new_height = max_size
                new_width = int(max_size * img.width / img.height)

            # Resize image and save
            img.thumbnail((new_width, new_height))
            img.save(image_path)

    except Exception as e:
        print(f"Image opening problem with {image_path}, Error: {e}")


def main(input_path: str, max_size: int):
    """Main function"""
    # Check : Is input path is a directory
    if not os.path.isdir(input_path):
        print("Invalid path!")
        return

    # Filter only images :
    images = [filename for filename in os.listdir(input_path) if IsImageFile(filename)]

    for filename in tqdm(images, desc="Images processing"):

        # Resize image
        file_path = os.path.join(input_path, filename)
        resize_image(file_path, max_size)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Images rescaler.")
    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Directory path with images."
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        required=True,
        help="Max size(width or height).",
    )

    args = parser.parse_args()

    main(args.input, args.size)
