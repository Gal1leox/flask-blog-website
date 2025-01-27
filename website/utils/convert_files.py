import base64


def convert_image_to_binary(image_path):
    """Converts an image file to binary data."""

    with open(image_path, "rb") as file:
        return file.read()


def convert_binary_to_image(binary_data):
    """Converts binary data to an image."""

    return base64.b64encode(binary_data).decode("utf-8")
