from pixoo import Pixoo, Channel  # Import Channel enum
from PIL import Image, ImageGrab, ImageTk
import tkinter as tk
import os
from datetime import datetime
import time
import threading
import subprocess  # For opening the folder
import random  # For shuffling images
import pystray  # For system tray functionality
import json  # Add this import for JSON handling

# Function to handle image pasting and display on Pixoo
def paste_and_display_image():
    try:
        # Stop the slideshow if it's running
        stop_slideshow()
        
        # Get the image from the clipboard
        image = ImageGrab.grabclipboard()
        
        if image:
            # Crop the image to a square (1:1 aspect ratio)
            width, height = image.size
            min_dimension = min(width, height)  # Get the smaller dimension
            left = (width - min_dimension) / 2
            top = (height - min_dimension) / 2
            right = (width + min_dimension) / 2
            bottom = (height + min_dimension) / 2
            
            # Crop the image to a square
            cropped_image = image.crop((left, top, right, bottom))
            
            # Resize the cropped image to 64x64 pixels (Pixoo 64 resolution)
            resized_image = cropped_image.resize((64, 64))
            
            # Convert the image to RGB mode (required by Pixoo)
            resized_image = resized_image.convert("RGB")
            
            # Save the resized image temporarily (optional, for debugging)
            resized_image.save("temp_resized_image.png")
            print("Resized image saved as 'temp_resized_image.png'")
            
            # Send the image to the Pixoo 64
            pixoo.draw_image("temp_resized_image.png")
            pixoo.push()
            
            print("Image displayed on Pixoo 64!")
            
            # Store the resized image for saving later
            global current_resized_image
            current_resized_image = resized_image
            
            # Update the image preview in the GUI
            update_image_preview(resized_image)
            
            # Update the tray icon with the current image
            update_tray_icon(resized_image)
        else:
            print("No image found in the clipboard.")
    except Exception as e:
        print(f"Error: {e}")

# Function to save the resized image to the "liked images" folder
def save_resized_image():
    try:
        if not current_resized_image:
            status_label.config(text="No image to save. Please paste an image first.")
            return
        
        # Create the "liked images" folder if it doesn't exist
        if not os.path.exists("liked images"):
            os.makedirs("liked images")
        
        # Generate a unique filename using the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"liked images/liked_image_{timestamp}.png"
        
        # Save the resized image
        current_resized_image.save(filename)
        print(f"Resized image saved as '{filename}'")
        
        # Update the status label with the saved filename
        status_label.config(text=f"Saved: {filename}")
    except Exception as e:
        print(f"Error: {e}")
        status_label.config(text=f"Error: {e}")

# Function to set the Pixoo channel to CLOUD
def set_cloud_channel():
    try:
        # Stop the slideshow if it's running
        stop_slideshow()
        
        # Set the channel to CLOUD
        pixoo.set_channel(Channel.CLOUD)
        status_label.config(text="Channel set to CLOUD.")
        print("Channel set to CLOUD.")
    except Exception as e:
        print(f"Error: {e}")
        status_label.config(text=f"Error: {e}")

# Function to stop the slideshow
def stop_slideshow():
    global slideshow_running
    if slideshow_running:
        slideshow_running = False
        slideshow_button.config(text="Start Slideshow")
        status_label.config(text="Slideshow stopped.")

# Global variables for slideshow control
slideshow_running = False
slideshow_thread = None
shuffle_slideshow = False  # Whether to shuffle the slideshow
slideshow_speed = 1.5  # Starting speed in seconds

# Function to start or stop the slideshow
def toggle_slideshow():
    global slideshow_running, slideshow_thread
    
    if slideshow_running:
        # Stop the slideshow
        stop_slideshow()
    else:
        # Start the slideshow in a separate thread
        slideshow_running = True
        slideshow_button.config(text="Stop Slideshow")
        slideshow_thread = threading.Thread(target=start_slideshow)
        slideshow_thread.start()

# Function to toggle shuffle mode
def toggle_shuffle():
    global shuffle_slideshow
    shuffle_slideshow = not shuffle_slideshow
    shuffle_button.config(text="Shuffle: On" if shuffle_slideshow else "Shuffle: Off")
    status_label.config(text="Slideshow shuffle turned on." if shuffle_slideshow else "Slideshow shuffle turned off.")

# Function to run the endless slideshow
def start_slideshow():
    try:
        # Check if the "liked images" folder exists
        if not os.path.exists("liked images"):
            status_label.config(text="No 'liked images' folder found.")
            return
        
        # Get a list of all images in the "liked images" folder
        image_files = [f for f in os.listdir("liked images") if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            status_label.config(text="No images found in 'liked images' folder.")
            return
        
        # Endless slideshow loop
        while slideshow_running:
            if shuffle_slideshow:
                random.shuffle(image_files)  # Shuffle the list of images
            
            for image_file in image_files:
                if not slideshow_running:
                    break  # Exit if slideshow is stopped
                
                image_path = os.path.join("liked images", image_file)
                pixoo.draw_image(image_path)
                pixoo.push()
                status_label.config(text=f"Showing: {image_file}")
                
                # Update the image preview in the GUI
                image = Image.open(image_path)
                update_image_preview(image)
                
                # Update the tray icon with the current image
                update_tray_icon(image)
                
                # Wait for the specified interval before showing the next image
                time.sleep(slideshow_speed)
        
        status_label.config(text="Slideshow stopped.")
    except Exception as e:
        print(f"Error: {e}")
        status_label.config(text=f"Error: {e}")

# Function to update the image preview in the GUI
def update_image_preview(image):
    # Resize the image to 64x64 pixels for the preview
    preview_image = image.resize((64, 64))
    
    # Convert the image to a format tkinter can display
    tk_preview_image = ImageTk.PhotoImage(preview_image)
    
    # Update the canvas with the new image
    canvas.create_image(32, 32, image=tk_preview_image)
    canvas.image = tk_preview_image  # Keep a reference to avoid garbage collection

# Function to open the "liked images" folder
def open_liked_images_folder():
    try:
        # Open the folder in the file explorer
        if os.path.exists("liked images"):
            subprocess.run(["explorer", "liked images"], shell=True)  # For Windows
            # For macOS: subprocess.run(["open", "liked images"])
            # For Linux: subprocess.run(["xdg-open", "liked images"])
        else:
            status_label.config(text="No 'liked images' folder found.")
    except Exception as e:
        print(f"Error: {e}")
        status_label.config(text=f"Error: {e}")

# Function to save the Pixoo IP address and slideshow speed to a file
def save_pixoo_ip():
    ip_address = ip_entry.get().strip()
    if ip_address:
        # Get the current slideshow speed
        global slideshow_speed
        speed = slideshow_speed
        
        # Create a dictionary to store both IP and speed
        data = {
            "ip_address": ip_address,
            "slideshow_speed": speed
        }
        
        # Save the data to the file as JSON
        with open("pixoo_ip.txt", "w") as file:
            json.dump(data, file)
        
        status_label.config(text=f"Saved IP: {ip_address}, Speed: {speed:.1f}s")
    else:
        status_label.config(text="Please enter a valid IP address.")

# Function to load the Pixoo IP address and slideshow speed from a file
def load_pixoo_ip():
    global slideshow_speed  # Move the global declaration to the top of the function
    if os.path.exists("pixoo_ip.txt"):
        with open("pixoo_ip.txt", "r") as file:
            try:
                # Load the data from the file
                data = json.load(file)
                
                # Extract the IP address and slideshow speed
                ip_address = data.get("ip_address", "")
                speed = data.get("slideshow_speed", slideshow_speed)  # Default to current speed if not found
                
                # Update the IP entry box
                ip_entry.insert(0, ip_address)
                
                # Update the slideshow speed
                slideshow_speed = speed
                speed_entry.delete(0, tk.END)
                speed_entry.insert(0, f"{speed:.1f}")
                speed_label.config(text=f"Speed: {speed:.1f}s")
                
                return ip_address
            except json.JSONDecodeError:
                # Handle invalid JSON (e.g., if the file is corrupted)
                print("Error: Invalid JSON in pixoo_ip.txt")
                return None
    return None

# Function to save the slideshow speed to the file
def save_speed_to_file():
    try:
        # Check if the file exists
        if os.path.exists("pixoo_ip.txt"):
            with open("pixoo_ip.txt", "r") as file:
                try:
                    # Load the existing data
                    data = json.load(file)
                except json.JSONDecodeError:
                    # If the file is corrupted, create a new empty dictionary
                    data = {}
        else:
            # If the file doesn't exist, create a new empty dictionary
            data = {}
        
        # Update the slideshow speed in the data
        data["slideshow_speed"] = slideshow_speed
        
        # Save the updated data back to the file
        with open("pixoo_ip.txt", "w") as file:
            json.dump(data, file)
        
        print(f"Slideshow speed saved: {slideshow_speed:.1f}s")
    except Exception as e:
        print(f"Error saving speed to file: {e}")

# Function to validate and update slideshow speed
def update_speed(event=None):
    try:
        # Get the value from the entry box
        new_speed = float(speed_entry.get())
        
        # Ensure the speed is not lower than 0.3
        if new_speed < 0.3:
            new_speed = 0.3
            speed_entry.delete(0, tk.END)
            speed_entry.insert(0, "0.3")  # Reset the entry box to 0.3
        
        # Update the global slideshow speed
        global slideshow_speed
        slideshow_speed = new_speed
        
        # Update the speed label
        speed_label.config(text=f"Speed: {slideshow_speed:.1f}s")
        
        # Save the updated speed to the file
        save_speed_to_file()
    except ValueError:
        # Handle invalid input (non-numeric)
        speed_entry.delete(0, tk.END)
        speed_entry.insert(0, f"{slideshow_speed:.1f}")  # Reset to current speed
        status_label.config(text="Invalid speed value. Please enter a number.")

# Initialize the Pixoo device with the saved IP address
def initialize_pixoo():
    global pixoo
    ip_address = ip_entry.get().strip()
    if ip_address:
        try:
            pixoo = Pixoo(ip_address)
            status_label.config(text=f"Connected to Pixoo at {ip_address}")
        except Exception as e:
            status_label.config(text=f"Error connecting to Pixoo: {e}")
    else:
        status_label.config(text="Please enter a valid IP address.")

# Function to update the tray icon with the current image
def update_tray_icon(image):
    if tray_icon_running and tray_icon:
        # Resize the image to 64x64 pixels for the tray icon
        tray_icon_image = image.resize((64, 64))
        
        # Update the tray icon
        tray_icon.icon = tray_icon_image

# Function to minimize the app to the system tray
def minimize_to_tray():
    root.withdraw()  # Hide the main window

# Function to restore the app from the system tray
def restore_from_tray(icon, item):
    root.deiconify()  # Restore the main window

# Function to exit the app
def exit_app(icon, item):
    global slideshow_running, tray_icon_running

    # Stop the slideshow if it's running
    slideshow_running = False

    # Stop the tray icon
    if tray_icon_running and tray_icon:
        tray_icon.stop()

    # Destroy the Tkinter root window
    if root:
        root.destroy()

    # Exit the application
    os._exit(0)  # Forcefully exit the application

# Function to run the tray icon in a separate thread
def run_tray_icon():
    global tray_icon
    tray_icon = pystray.Icon(
        "Pixoo Controller",
        icon=Image.new("RGB", (64, 64), "black"),
        menu=pystray.Menu(
            pystray.MenuItem("Restore", restore_from_tray),
            pystray.MenuItem("Exit", exit_app)
        )
    )
    # Run the tray icon
    tray_icon.run()

# Function to toggle tray functionality
def toggle_tray():
    global tray_icon_running, tray_thread
    
    if tray_icon_running:
        # Stop the tray icon
        if tray_icon:
            tray_icon.stop()
        tray_icon_running = False
        tray_button.config(text="Enable Tray")
        status_label.config(text="Tray functionality disabled.")
    else:
        # Start the tray icon in a separate thread
        tray_icon_running = True
        tray_button.config(text="Disable Tray")
        status_label.config(text="Tray functionality enabled.")
        tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
        tray_thread.start()

# Create a simple GUI for pasting
root = tk.Tk()
root.title("Paste Image to Pixoo 64")
root.geometry("640x300")  # Increased height to accommodate the new controls

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, padx=10, pady=10)

# Add a button to trigger pasting
paste_button = tk.Button(button_frame, text="Paste Image (Ctrl+V)", command=paste_and_display_image)
paste_button.pack(side=tk.LEFT, padx=5)

# Add a button to save the resized image
save_button = tk.Button(button_frame, text="Save to Liked Images", command=save_resized_image)
save_button.pack(side=tk.LEFT, padx=5)

# Add a button to set the channel to CLOUD
cloud_button = tk.Button(button_frame, text="CLOUD", command=set_cloud_channel)
cloud_button.pack(side=tk.LEFT, padx=5)

# Add a button to start/stop the slideshow
slideshow_button = tk.Button(button_frame, text="Start Slideshow", command=toggle_slideshow)
slideshow_button.pack(side=tk.LEFT, padx=5)

# Add a button to toggle shuffle mode
shuffle_button = tk.Button(button_frame, text="Shuffle: Off", command=toggle_shuffle)
shuffle_button.pack(side=tk.LEFT, padx=5)

# Add a button to open the "liked images" folder
open_folder_button = tk.Button(button_frame, text="📁", command=open_liked_images_folder)
open_folder_button.pack(side=tk.LEFT, padx=5)

# Create a frame for the speed controls
speed_frame = tk.Frame(root)
speed_frame.pack(side=tk.TOP, padx=10, pady=10)

# Add a label for the slideshow speed
speed_label = tk.Label(speed_frame, text=f"Speed: {slideshow_speed:.1f}s")
speed_label.pack(side=tk.LEFT, padx=5)

# Add an entry box for the slideshow speed
speed_entry = tk.Entry(speed_frame, width=5)
speed_entry.insert(0, f"{slideshow_speed:.1f}")  # Set initial value
speed_entry.pack(side=tk.LEFT, padx=5)

# Bind the Enter key to update the speed
speed_entry.bind("<Return>", update_speed)

# Add a button to apply the speed (optional, for users who prefer clicking)
apply_speed_button = tk.Button(speed_frame, text="Apply", command=update_speed)
apply_speed_button.pack(side=tk.LEFT, padx=5)

# Create a frame for the IP address entry
ip_frame = tk.Frame(root)
ip_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Add a label for the IP address entry
ip_label = tk.Label(ip_frame, text="Pixoo IP:")
ip_label.pack(side=tk.LEFT, padx=5)

# Add an entry box for the IP address
ip_entry = tk.Entry(ip_frame, width=15)
ip_entry.pack(side=tk.LEFT, padx=5)

# Add a button to save the IP address
save_ip_button = tk.Button(ip_frame, text="Save IP", command=save_pixoo_ip)
save_ip_button.pack(side=tk.LEFT, padx=5)

# Add a button to initialize the Pixoo device with the entered IP
connect_button = tk.Button(ip_frame, text="Connect", command=initialize_pixoo)
connect_button.pack(side=tk.LEFT, padx=5)

# Create a canvas for the image preview
canvas = tk.Canvas(root, width=64, height=64, bg="black")
canvas.pack(side=tk.RIGHT, padx=10, pady=10)

# Add a label to display the status at the bottom left
status_label = tk.Label(root, text="", fg="green", anchor="w")
status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Add a button to toggle tray functionality at the bottom-right
tray_icon_running = True  # Tray icon is enabled by default
tray_button = tk.Button(root, text="Disable Tray", command=toggle_tray)
tray_button.pack(side=tk.RIGHT, padx=10, pady=10, anchor="se")  # Anchor to bottom-right

# Load the saved IP address and slideshow speed (if they exist) and automatically connect
saved_ip = load_pixoo_ip()
if saved_ip:
    initialize_pixoo()

# Bind Ctrl+V to the paste function
root.bind("<Control-v>", lambda event: paste_and_display_image())

# Function to handle the window close event
def on_closing():
    if tray_icon_running:
        minimize_to_tray()  # Minimize to tray if tray is enabled
    else:
        root.destroy()  # Close the app if tray is disabled

# Override the default close behavior
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the tray icon in a separate thread (enabled by default)
tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
tray_thread.start()

# Start the main event loop
root.mainloop()