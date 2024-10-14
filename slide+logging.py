import cv2
import os
import numpy as np
import time  # Import the time module


def fit_image_to_frame(img, frame_size):
    """Resizes the image to fit within the frame size, adding padding if necessary."""
    frame_width, frame_height = frame_size
    img_height, img_width = img.shape[:2]

    # Calculate the aspect ratios
    img_aspect_ratio = img_width / img_height
    frame_aspect_ratio = frame_width / frame_height

    if img_aspect_ratio > frame_aspect_ratio:
        # Fit to width
        new_width = frame_width
        new_height = int(frame_width / img_aspect_ratio)
    else:
        # Fit to height
        new_height = frame_height
        new_width = int(frame_height * img_aspect_ratio)

    # Create a black canvas (empty frame) and place the resized image at the center
    canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    # Resize the image
    resized_img = cv2.resize(img, (new_width, new_height))

    # Compute offsets for centering the image
    x_offset = (frame_width - new_width) // 2
    y_offset = (frame_height - new_height) // 2

    # Place the resized image onto the black canvas
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_img

    return canvas

def create_slideshow(image_folder, output_file, fps=30, duration=3, transition_duration=1):
    """Creates a slideshow video with crossfade transitions."""
    start_time = time.time()  # Start timing

    images = [img for img in os.listdir(image_folder) if img.endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()  # auto sort

    if not images:
        print("No images found in the folder.")
        return

    # Use the first image to determine the frame size
    sample_img = cv2.imread(os.path.join(image_folder, images[0]))
    frame_size = (sample_img.shape[1], sample_img.shape[0])  # width, height
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

    transition_frames = int(fps * transition_duration)

    # Load and process all images once
    processed_images = []
    for image in images:
        img_path = os.path.join(image_folder, image)
        img = cv2.imread(img_path)
        if img is not None:
            processed_images.append(fit_image_to_frame(img, frame_size))
            print(f"Processed image: {image}")  # Print the name of each processed image
        else:
            print(f"Could not read image: {img_path}")

    # Pre-compute repeated frames for duration
    duration_frames = int(fps * duration)

    for i in range(len(processed_images) - 1):
        current_img = processed_images[i]
        next_img = processed_images[i + 1]

        # Write the current image for the set duration
        for _ in range(duration_frames):
            video.write(current_img)

        # Crossfade transition
        for t in range(transition_frames):
            alpha = t / transition_frames
            blended_frame = cv2.addWeighted(current_img, 1 - alpha, next_img, alpha, 0)
            video.write(blended_frame)

        print(f"Completed processing transition for image: {images[i]}")

    # Write the last image (no transition after the final image)
    last_img = processed_images[-1]
    for _ in range(duration_frames):
        video.write(last_img)

    print(f"Completed processing final image: {images[-1]}")

    video.release()
    end_time = time.time()  # End timing

    elapsed_time = end_time - start_time  # Calculate time job takes
    print(f"Slideshow created with transitions: {output_file}")
    print(f"Total processing time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    image_folder = "Slideshow Library"  # Replace with your folder path
    output_file = "slideshow_with_fitted_images.mp4"
    create_slideshow(image_folder, output_file)
