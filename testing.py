from PIL import Image
import os

# Function to resize images
def resize_images(input_folder, output_folder, size):
    # Check if output folder exists; if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all the files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(input_folder, filename)
            with Image.open(img_path) as img:
                # Resize the image
                if (img.width, img.height) == size:
                    print(f'Already processed: {filename}')
                    continue
                img = img.resize(size, Image.Resampling.LANCZOS)
                # Save the image to the output folder
                img.save(os.path.join(output_folder, filename))
                print(f'Resized and saved: {filename}')

# Define the parameters
input_directory = "C:/Users/Lokaalne/.vscode/Riot-Logger/images/border/"
output_directory = "C:/Users/Lokaalne/.vscode/Riot-Logger/images/borderc/"
image_size = (92*3, 119*3)  # Width, Height

# Call the function
resize_images(input_directory, output_directory, image_size)