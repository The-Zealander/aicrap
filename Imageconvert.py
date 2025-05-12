# Need to install Pillow: pip install Pillow
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import shutil
from PIL import Image # Import Pillow

class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Image Renamer")

        self.selected_files = []
        self.output_directory = ""

        # --- Widgets ---

        # Base Name
        self.base_name_label = ttk.Label(root, text="Enter Base Name (e.g., laptop):")
        self.base_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.base_name_entry = ttk.Entry(root, width=40)
        self.base_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Select Files
        self.select_files_button = ttk.Button(root, text="Select Images", command=self.select_files)
        self.select_files_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.files_count_label = ttk.Label(root, text="No files selected")
        self.files_count_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Output Directory
        self.select_dir_button = ttk.Button(root, text="Select Output Folder", command=self.select_output_directory)
        self.select_dir_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.output_dir_label = ttk.Label(root, text="No output folder selected")
        self.output_dir_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Process Button
        self.process_button = ttk.Button(root, text="Rename, Convert, and Move Images", command=self.process_images)
        self.process_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Status Label
        self.status_label = ttk.Label(root, text="")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # Configure grid weights for resizing
        root.columnconfigure(1, weight=1)

    def select_files(self):
        # Open file dialog to select multiple image files
        # Added .avif and .webp to the file types
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.avif *.webp"),
            ("All files", "*.*")
        )
        filenames = filedialog.askopenfilenames(
            title="Select Image Files",
            initialdir=".", # Start in current directory
            filetypes=filetypes
        )

        if filenames:
            self.selected_files = list(filenames)
            self.files_count_label.config(text=f"{len(self.selected_files)} files selected")
            self.status_label.config(text="") # Clear status

    def select_output_directory(self):
        # Open dialog to select output folder
        directory = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir="." # Start in current directory
        )

        if directory:
            self.output_directory = directory
            self.output_dir_label.config(text=self.output_directory)
            self.status_label.config(text="") # Clear status


    def process_images(self):
        base_name = self.base_name_entry.get().strip()

        if not base_name:
            messagebox.showwarning("Input Error", "Please enter a base name.")
            return
        if not self.selected_files:
            messagebox.showwarning("Input Error", "Please select image files.")
            return
        if not self.output_directory:
            messagebox.showwarning("Input Error", "Please select an output folder.")
            return

        # Ask for confirmation before deleting original files
        confirm = messagebox.askyesno(
            "Confirm Operation",
            "Are you sure you want to rename, convert, and move the selected images?\n"
            "This will convert images to JPG, rename them, and DELETE the original files from their current locations."
        )
        if not confirm:
            self.status_label.config(text="Operation cancelled.")
            return

        self.status_label.config(text="Processing...")
        self.root.update_idletasks() # Update GUI to show status change

        counter = 1
        processed_count = 0
        errors = []

        for old_filepath in self.selected_files:
            try:
                # Define the desired output extension
                output_extension = ".jpg" # Or ".png" if you prefer PNG

                # Create the new filename with the desired output extension
                new_filename = f"{base_name} {counter}{output_extension}"
                # Create the full path for the destination file
                new_filepath = os.path.join(self.output_directory, new_filename)

                # --- Image Conversion and Saving ---
                img = Image.open(old_filepath)

                # Handle potential transparency issues when saving to JPG
                # If the image has an alpha channel (like some PNGs, WebPs),
                # convert it to RGB before saving as JPG.
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                # Save the image in the desired output format
                img.save(new_filepath, format='JPEG') # Specify format explicitly
                img.close() # Close the image file
                # -----------------------------------

                # --- Delete the original file ---
                os.remove(old_filepath)
                # --------------------------------

                processed_count += 1
                counter += 1
                self.status_label.config(text=f"Processed {processed_count}/{len(self.selected_files)}...")
                self.root.update_idletasks() # Update GUI

            except Exception as e:
                error_msg = f"Failed to process {os.path.basename(old_filepath)}: {e}"
                errors.append(error_msg)
                self.status_label.config(text=f"Error processing {os.path.basename(old_filepath)}...")
                self.root.update_idletasks() # Update GUI


        if not errors:
            self.status_label.config(text=f"Successfully processed {processed_count} images!")
            messagebox.showinfo("Success", f"Successfully processed {processed_count} images and moved to:\n{self.output_directory}")
        else:
            self.status_label.config(text=f"Finished with {len(errors)} errors. Processed {processed_count} images.")
            error_report = "\n".join(errors)
            messagebox.showerror("Processing Complete with Errors",
                                 f"Finished processing with some errors. {processed_count} images processed.\n\nDetails:\n{error_report}")

        # Clear selected files list after processing
        self.selected_files = []
        self.files_count_label.config(text="No files selected")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()