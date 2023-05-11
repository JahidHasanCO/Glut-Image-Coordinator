import tkinter as tk
from tkinter import Menu, Frame, BOTTOM, X, Label, Toplevel, Button
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import pyperclip
import os
import sys


class ImageViewer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Glut Image Coordinator")
        # self.master.config(bg="skyblue")
        self.master.geometry("500x700")
        self.master.minsize(500, 700)
        self.master.maxsize(500, 700)

        # Creating Menubar
        menubar = Menu(master)

        # Adding File Menu and commands
        file = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file)
        file.add_command(label='New Window', command=self.create_new_window)
        file.add_command(label='Open Image...', command=self.upload_image)
        file.add_separator()
        file.add_command(label='Exit', command=master.destroy)

        # Adding Help Menu
        help_ = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=help_)
        help_.add_command(label='Contract Us',
                          command=self.on_contact_us_click)
        help_.add_separator()
        help_.add_command(label='About Us', command=self.show_about_dialog)

        # display Menu
        master.config(menu=menubar)
        self.create_widgets()

    def create_new_window(self):
        new_window = tk.Toplevel(self.master)
        image_viewer = ImageViewer(new_window)

    def create_widgets(self):

        # Create an image canvas to display the uploaded image
        self.image_canvas = tk.Canvas(self.master, width=500, height=500)
        self.image_canvas.pack()

        # Bind the mouse events to the canvas
        self.image_canvas.bind("<Motion>", self.on_mouse_move)
        self.image_canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Initialize variables
        self.image = None
        self.image_tk = None
        self.image_id = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.zoom_factor = 1
        self.zoom_center_x = 0
        self.zoom_center_y = 0
        self.zoom_rect_id = None
        self.zoom_canvas = None
        self.height = 0.0
        self.width = 0.0

        self.dialogBox = Frame(
            master=self.master, bg="#eeeeee", bd=0.8, relief="solid")
        self.dialogBox.pack(side=BOTTOM, fill=X, padx=2, pady=2)

        self.zoom_canvas = tk.Canvas(
            self.dialogBox, width=200, height=200, borderwidth=1, relief="solid")
        self.zoom_canvas.pack(side="left")
        self.update_zoom_window()

        # create a label to display "Image Information" text
        label = tk.Label(
            self.dialogBox, text="Image Information", font=("Arial", 14))
        label.pack(fill=X, padx=10, pady=10)

        # Create a label to display the height of the image
        self.height_var = tk.StringVar()
        self.height_var.set("Height: 0")
        self.height_label = tk.Label(
            self.dialogBox, textvariable=self.height_var, font=("Arial", 12))
        self.height_label.pack()

        # Create a label to display the width of the image
        self.width_var = tk.StringVar()
        self.width_var.set("Width: 0")
        self.width_label = tk.Label(
            self.dialogBox, textvariable=self.width_var, font=("Arial", 12))
        self.width_label.pack()

        self.coord_var = tk.StringVar()
        self.coord_var.set("x=0, y=0")
        coord_label = tk.Label(
            self.dialogBox, textvariable=self.coord_var, font=("Arial", 12))
        coord_label.pack()

        self.rgb_var = tk.StringVar()
        self.rgb_var.set("r=0, g=0, b=0")
        rgb_label = tk.Label(
            self.dialogBox, textvariable=self.rgb_var, font=("Arial", 12))
        rgb_label.pack()

        self.upload_placeholder_image()

    def upload_image(self):
        # Open a file dialog to select an image file
        file_path = filedialog.askopenfilename()
        if file_path:
            # Load the image and display it on the canvas
            self.image = Image.open(file_path)

            # crop the image to a square aspect ratio
            width, height = self.image.size
            if width > height:
                left = (width - height) / 2
                right = left + height
                top, bottom = 0, height
            else:
                top = (height - width) / 2
                bottom = top + width
                left, right = 0, width
            self.image = self.image.crop((left, top, right, bottom))

            # resize the image to fit within the canvas
            self.image = self.image.resize((500, 500), Image.LANCZOS)

            self.image_tk = ImageTk.PhotoImage(self.image)
            self.image_id = self.image_canvas.create_image(
                0, 0, anchor="nw", image=self.image_tk)

            # Update the height and width labels with the image size
            self.height = self.image.height
            self.width = self.image.width
            self.height_var.set("Height: {}".format(self.image.height))
            self.width_var.set("Width: {}".format(self.image.width))
            # Resize the canvas to match the fixed size
            self.image_canvas.config(width=500, height=500)

    def upload_placeholder_image(self):
        # Open a file dialog to select an image file
        filePath = resource_path("img/icon.ico")
        # Load the image and display it on the canvas
        self.image = Image.open(filePath)
        # crop the image to a square aspect ratio
        width, height = self.image.size
        if width > height:
            left = (width - height) / 2
            right = left + height
            top, bottom = 0, height
        else:
            top = (height - width) / 2
            bottom = top + width
            left, right = 0, width
        self.image = self.image.crop((left, top, right, bottom))

        # resize the image to fit within the canvas
        self.image = self.image.resize((500, 500), Image.LANCZOS)

        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_id = self.image_canvas.create_image(
            0, 0, anchor="nw", image=self.image_tk)

        # Update the height and width labels with the image size
        self.height = self.image.height
        self.width = self.image.width
        self.height_var.set("Height: {}".format(self.image.height))
        self.width_var.set("Width: {}".format(self.image.width))
        # Resize the canvas to match the fixed size
        self.image_canvas.config(width=500, height=500)

    def on_mouse_move(self, event):
        # Update the mouse coordinates
        self.mouse_x = event.x
        self.mouse_y = event.y  # Invert the y-coordinate

        # Update the coordinate text
        self.coord_var.set("x={}, y={}".format(round(
            (self.mouse_x / 500), 4), round((self.image_canvas.winfo_height() - event.y) / 500, 4)))

        # Update the RGB text
        if self.image:
            x = int((self.mouse_x - self.x_center) /
                    self.zoom_factor + self.x_center)
            y = int((self.mouse_y - self.y_center) /
                    self.zoom_factor + self.y_center)
            if x >= 0 and x < self.image.width and y >= 0 and y < self.image.height:
                pixel = self.image.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[:3]
                    self.rgb_var.set("r={}, g={}, b={}".format(
                        round(r/255, 4), round(g/255, 4), round(b/255, 4)))

        # Update the zoom window if it exists
        if self.zoom_canvas:
            self.update_zoom_window()

    def on_mouse_press(self, event):
        if self.zoom_rect_id and self.image:
            self.mouse_pressed = True
            # Copy the coordinates and RGB values to the clipboard
        if self.image:
            x = int((self.mouse_x - self.x_center) /
                    self.zoom_factor + self.x_center)
            y = int((self.mouse_y - self.y_center) /
                    self.zoom_factor + self.y_center)
            if x >= self.x_min and x <= self.x_max and y >= self.y_min and y <= self.y_max:
                pixel = self.image.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[:3]
                    # rest of the code
                else:
                    r, g, b, *_ = self.image.getpixel((x, y))
                    # handle the case where the pixel values are not RGB
                coords = f"glVertex3f({x/500}f, {(self.image_canvas.winfo_height() - y)/500}f , 0f);"
                rgb = f"glColor3f({round(r/225,3)}f, {round(g/225,3)}f, {round(b/225,3)}f);"
                text = "{}\n{}".format(rgb, coords)
                pyperclip.copy(text)
                messagebox.showinfo("Code Copied", text)

    def on_mouse_release(self, event):
        # Stop dragging the zoom rectangle
        self.mouse_pressed = False

    def update_zoom_window(self):
        # Create an image for the zoom window
        self.x_center = self.mouse_x / self.zoom_factor
        self.y_center = self.mouse_y / self.zoom_factor
        self.zoom_image = Image.new("RGB", (200, 200), "white")
        self.zoom_image_tk = ImageTk.PhotoImage(self.zoom_image)
        self.zoom_canvas.create_image(
            0, 0, anchor="nw", image=self.zoom_image_tk)

        # Create a rectangle to show the zoom area on the canvas
        x1 = self.mouse_x - 50
        y1 = self.mouse_y - 50
        x2 = self.mouse_x + 50
        y2 = self.mouse_y + 50
        self.zoom_rect_id = self.image_canvas.create_rectangle(
            x1, y1, x2, y2, outline="red")

        if self.zoom_rect_id:
            # Hide the zoom rectangle
            self.image_canvas.itemconfigure(self.zoom_rect_id, state='hidden')

        if self.image and self.zoom_canvas:
            # Update the zoom rectangle position and size
            x1 = self.mouse_x - 50
            y1 = self.mouse_y - 50
            x2 = self.mouse_x + 50
            y2 = self.mouse_y + 50
            self.image_canvas.coords(self.zoom_rect_id, x1, y1, x2, y2)

            # Update the zoom center position
            self.zoom_center_x = self.mouse_x / self.zoom_factor
            self.zoom_center_y = self.mouse_y / self.zoom_factor

            # Schedule the zoom image update after a delay
            self.after(50, self.update_zoom_image)

            # Redraw the zoom rectangle
            x1 = self.mouse_x - 50
            y1 = self.mouse_y - 50
            x2 = self.mouse_x + 50
            y2 = self.mouse_y + 50
            self.image_canvas.coords(self.zoom_rect_id, x1, y1, x2, y2)

    def update_zoom_image(self):
        # Update the zoom window image
        x = int(self.zoom_center_x - 100 / self.zoom_factor)
        y = int(self.zoom_center_y - 100 / self.zoom_factor)
        x1 = max(x, 0)
        y1 = max(y, 0)
        x2 = min(x + 200 // self.zoom_factor, self.image.width)
        y2 = min(y + 200 // self.zoom_factor, self.image.height)

        # add padding if the zoomed image is not complete
        if x2 == self.image.width and x1 > 0:
            x1 = max(x1 - (x2 - self.image.width) - 1, 0)
        if y2 == self.image.height and y1 > 0:
            y1 = max(y1 - (y2 - self.image.height) - 1, 0)

        self.zoom_image = self.image.crop((x1, y1, x2, y2))
        self.zoom_image = self.zoom_image.resize((200, 200), Image.BILINEAR)

        left_pad = 0
        right_pad = 0
        top_pad = 0
        bottom_pad = 0
        # add one pixel padding if the zoomed image is not complete
        if x2 - x1 < 200 or y2 - y1 < 200:
            if self.mouse_x <= 250:
                left_pad = abs(200 - (x2-x1))
            else:
                right_pad = abs(200 - (x2-x1))

            if self.mouse_y <= 250:
                top_pad = abs(200 - (y2-y1))
            else:
                bottom_pad = abs(200 - (y2-y1))

            self.zoom_image = ImageOps.expand(
                self.zoom_image, border=(left_pad - right_pad, top_pad-bottom_pad, right_pad, bottom_pad), fill='white')


        self.zoom_image_tk = ImageTk.PhotoImage(self.zoom_image)
        self.zoom_canvas.create_image(
            0, 0, anchor="nw", image=self.zoom_image_tk)

        # Draw a crosshair in the center of the zoom window
        x1 = 0
        y1 = 100
        x2 = 200 
        y2 = 100
        self.zoom_canvas.create_line(x1, y1, x2, y2, fill="red")

        x1 = 100
        y1 = 0
        x2 = 100
        y2 = 200
        self.zoom_canvas.create_line(x1, y1, x2, y2, fill="red")

    def zoom_in(self):
        # Increase the zoom factor and update the zoom window
        self.zoom_factor *= 2.0
        self.update_zoom_window()

    def zoom_out(self):
        # Decrease the zoom factor and update the zoom window
        self.zoom_factor /= 2.0
        self.update_zoom_window()

    def set_coordinates(self, x_min, x_max, y_min, y_max, x_center, y_center):
        # Set the coordinate limits and center point
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min  # Swap y_min and y_max
        self.y_max = y_max
        self.x_center = x_center
        self.y_center = y_center

    def save_to_clipboard(self):
        # Copy the coordinates and RGB values to the clipboard
        if self.image:
            x = int((self.mouse_x - self.x_center) /
                    self.zoom_factor + self.x_center)
            y = int((self.mouse_y - self.y_center) /
                    self.zoom_factor + self.y_center)
            if x >= self.x_min and x <= self.x_max and y >= self.y_min and y <= self.y_max:
                pixel = self.image.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[:3]
                    # rest of the code
                else:
                    r, g, b, *_ = self.image.getpixel((x, y))
                    # handle the case where the pixel values are not RGB
                coords = f"glVertex3f({x/500}f, {(self.image_canvas.winfo_height() - y)/500}f , 0f);"
                rgb = f"glColor3f({round(r/225,3)}f, {round(g/225,3)}f, {round(b/225,3)}f);"
                text = "{}\n{}".format(rgb, coords)
                pyperclip.copy(text)
                messagebox.showinfo("Code Copied", text)

    def show_about_dialog(self):
        # Create a Toplevel window for the about dialog
        about_window = tk.Toplevel(self.master)
        about_window.minsize(300, 150)
        about_window.maxsize(300, 150)
        about_window.title("About Glut Image Coordinator")
        filePath = resource_path("img/icon.ico")
        about_window.iconbitmap(filePath)

        # Add a label with the program name and version
        label1 = tk.Label(about_window, text="Glut Image Coordinator v1.1")
        label1.pack(pady=10)

        # Add a label with the developer name and email
        label2 = tk.Label(
            about_window, text="Developed by Jahid Hasan\nEmail: vdjsovaj@gmail.com")
        label2.pack(padx=10, pady=10)

        # Add a button to close the about dialog
        close_button = tk.Button(
            about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)

    def on_contact_us_click(self):
        # Create a new Toplevel window for the Contact Us dialog
        top = Toplevel(self.master)
        top.minsize(300, 150)
        top.maxsize(300, 150)
        top.title("Contact Us")
        filePath = resource_path("img/icon.ico")
        top.iconbitmap(filePath)
        # Add some text to the window
        Label(top, text="For support or inquiries, please email us at:").pack(
            padx=10, pady=10)
        Label(top, text="vdjsovaj@gmail.com").pack()
        Label(top, text="We usually respond within 24 hours.").pack()

        # Add a button to close the window
        Button(top, text="Close", command=top.destroy).pack(padx=10, pady=10)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    try:
        root = tk.Tk()
        filePath = resource_path("img/icon.ico")
        root.iconbitmap(filePath)
        app = ImageViewer(master=root)
        app.set_coordinates(0, 500, 0, 580, 0, 0)
        root.bind("<Control-x>", lambda event: app.save_to_clipboard())
        root.bind("<Control-=>", lambda event: app.zoom_in())
        root.bind("<Control-minus>", lambda event: app.zoom_out())
        app.mainloop()
    except Exception as e:
        print("An error occurred: ", e)
