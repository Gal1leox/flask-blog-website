def convert_image_to_binary(image_path):
    """Converts an image file to binary data."""

    with open(image_path, "rb") as file:
        return file.read()
