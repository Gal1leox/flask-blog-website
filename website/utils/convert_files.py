def convert_image_to_binary(image_path):
    """Converts an image file to binary data."""

    with open(image_path, "rb") as file:
        return file.read()


def convert_binary_to_image(binary_data, output_name):
    """Convert binary data into an image file."""

    with open(binary_data, "wb") as file:
        return file.write(binary_data)
