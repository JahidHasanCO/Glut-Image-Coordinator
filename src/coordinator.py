import tkinter as tk
from tkinter import Menu, X, Label, Toplevel
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import pyperclip
import tkinter.ttk as ttk
import configparser
from util.get_resource import *
from util.normalization import normalizeValue
from tkinter import colorchooser

graph_max = 1
graph_min = 0

# Constants for tool selection
TOOL_SELECTOR = "Selector"
TOOL_PEN = "Pen"
TOOL_HAND = "Hand"
TOOL_COLOR_SELECTOR = "color_selector"


def darkstyle(root):
    style = ttk.Style(root)
    filePath = resource_path("theme/forest-light.tcl")
    root.tk.call('source', filePath)
    style.theme_use('forest-light')
    return style


class ImageViewer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master = master

        if "forest-light" not in ttk.Style().theme_names():
            self.style = darkstyle(self.master)
        self.master.title("Glut Image Coordinator")
        self.master.state('zoomed')
        # self.master.config(bg="skyblue")
        self.master.geometry("500x600")
        self.master.minsize(500, 600)

        # Load configuration file
        self.config = configparser.ConfigParser()
        self.config.read('coordinator.ini')
        # Creating Menubar
        menubar = Menu(master)

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
        self.tool = TOOL_SELECTOR
        self.canvas_zoom_factor = 1.0
        # Inside the create_toolbar method
        self.selector_icon = tk.PhotoImage(file=resource_path("img/mouse.png"))
        self.pen_icon = tk.PhotoImage(file=resource_path("img/pen.png"))
        self.hand_icon = tk.PhotoImage(file=resource_path("img/hand.png"))
        self.color_selector_icon = tk.PhotoImage(
            file=resource_path("img/colorPicker.png"))

        # Initialize pen drawing variables
        self.drawing = False
        self.prev_x = None
        self.prev_y = None
        self.selected_color = "#000000"
        self.pixels = {}
        self.background_color = "white"

        # Adding File Menu and commands
        file = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file)
        file.add_command(label='New Window', command=self.create_new_window)
        file.add_command(label='New Canvas', command=self.set_canvas_size)
        file.add_command(label='Open Image...', command=self.upload_image)
        file.add_command(label='Close Image',
                         command=self.upload_placeholder_image)
        file.add_separator()
        file.add_command(label='Exit', command=master.destroy)

        setting = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Settings', menu=setting)
        setting.add_command(label='Set Graph Range',
                            command=self.open_graph_range_setting)
        setting.add_command(label='Copy Template Code',
                            command=self.templateCodeWindow)
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
        ImageViewer(new_window)

    def create_widgets(self):

        # Create a frame to hold the canvas and scrollbar
        self.frame = tk.Frame(self.master, bg="lightgray",
                              background="#E1E1E1")
        self.frame.grid(row=0, column=0, sticky="nsew")

    # Create the left frame
        self.left_frame = tk.Frame(self.frame, background="#fff")
        self.left_frame.grid(row=0, column=2, sticky="ns")

        # Create tool buttons
        ttk.Label(self.left_frame, text="Tools").grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Separator(self.left_frame).grid(row=1,column=0,sticky="nsew")
        self.selector_button = tk.Button(
            self.left_frame, text="", image=self.selector_icon, command=lambda: self.set_tool(TOOL_SELECTOR))
        self.selector_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.pen_button = tk.Button(
            self.left_frame, text="", image=self.pen_icon,  command=lambda: self.set_tool(TOOL_PEN))
        self.pen_button.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.hand_button = tk.Button(
            self.left_frame, text="", image=self.hand_icon,  command=lambda: self.set_tool(TOOL_HAND))
        self.hand_button.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        self.color_selector = tk.Button(
            self.left_frame, text="", image=self.color_selector_icon, command=lambda: self.set_tool(TOOL_COLOR_SELECTOR))
        self.color_selector.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

        # Inside the create_toolbar method
        button_width = self.selector_icon.width() + 10  # Add padding
        button_height = self.selector_icon.height() + 10  # Add padding

        self.selector_button.config(
            width=button_width, height=button_height, relief="flat", bd=0, text="",background="lightgrey")
        self.pen_button.config(
            width=button_width, height=button_height, relief="flat", bd=0, text="")
        self.hand_button.config(
            width=button_width, height=button_height, relief="flat", bd=0, text="")
        self.color_selector.config(
            width=button_width, height=button_height, relief="flat", bd=0, text="")

        # Create an image canvas to display the uploaded image
        self.image_canvas = tk.Canvas(
            self.frame, borderwidth=1, relief="solid")
        self.image_canvas.grid(row=0, column=0)
        self.image_canvas.config(cursor="circle")

        # Bind the mouse events to the canvas
        self.image_canvas.bind("<Motion>", self.on_mouse_move)
        self.image_canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.image_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.image_canvas.bind("<Control-Motion>", self.on_canvas_drag)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Create a canvas with the specified size
        self.canvas_width = tk.IntVar()
        self.canvas_height = tk.IntVar()
        self.canvas_width.set(500)
        self.canvas_height.set(500)

        # Create a scrollbar for the canvas
        self.scrollbar = ttk.Scrollbar(
            self.frame, orient="vertical", command=self.image_canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.image_canvas.config(yscrollcommand=self.scrollbar.set)

        # self.right_frame = ttk.Frame(self.frame, width=200)
        # self.right_frame.grid(row=0, column=2, sticky="nsew")

        self.scrollbar_h = ttk.Scrollbar(
            self.frame, orient="horizontal", command=self.image_canvas.xview)
        self.scrollbar_h.grid(row=1, column=0, sticky="ew")
        self.image_canvas.config(xscrollcommand=self.scrollbar_h.set)

        # self.zoom_in_button = tk.Button(
        #     self.left_frame, text="", image=self.color_selector_icon, command=self.zoom(1.5))
        # self.zoom_in_button.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        # self.zoom_out_button = tk.Button(
        #     self.left_frame, text="", image=self.color_selector_icon, command=self.zoom(0.9))
        # self.zoom_out_button.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

        tempFrame = tk.Frame(self.frame, background="#fff")
        tempFrame.grid(row=1, column=1, sticky="nsew")
        tempFrame1 = tk.Frame(self.frame, background="#fff")
        tempFrame1.grid(row=1, column=2, sticky="nsew")

        # Create a frame to hold the buttons
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.grid(row=1, column=0, sticky="nsew")

        self.zoom_canvas = tk.Canvas(
            self.bottom_frame, width=100, height=100, borderwidth=1, relief="solid")
        self.zoom_canvas.grid(row=0, column=0,sticky="nsew")
        self.update_zoom_window()

        self.bottom_output_frame = tk.Frame(self.bottom_frame)
        self.bottom_output_frame.grid(row=0, column=1, sticky="nsew")
        # create a label to display "Image Information" text
        label = ttk.Label(
            self.bottom_output_frame, text="Canvas Information", font=("Helvetica", 12))
        label.grid(row=0, column=0, padx=20, sticky="nsew")

        # Create a label to display the height of the image
        self.height_var = tk.StringVar()
        self.height_var.set("Image Height: 0")
        self.height_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.height_var, font=("Helvetica", 10))
        self.height_label.grid(row=1, column=0, padx=20, sticky="nsew")

        # Create a label to display the width of the image
        self.width_var = tk.StringVar()
        self.width_var.set("Image Width: 0")
        self.width_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.width_var, font=("Helvetica", 10))
        self.width_label.grid(row=2, column=0, padx=20, sticky="nsew")

        self.coord_var = tk.StringVar()
        self.coord_var.set("X-Axis=0, Y-Axis=0")
        coord_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.coord_var, font=("Helvetica", 10))
        coord_label.grid(row=3, column=0, padx=20, sticky="nsew")

        self.rgb_var = tk.StringVar()
        self.rgb_var.set("R=0, G=0, B=0")
        rgb_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.rgb_var, font=("Helvetica", 10))
        rgb_label.grid(row=4, column=0, padx=20, sticky="nsew")

        # Configure the grid layout
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.bottom_output_frame.columnconfigure(1, weight=1)

        self.upload_placeholder_image()

    def set_canvas_size(self):
        # Open a dialog to get the canvas size from the user
        self.dialogNewCanvas = tk.Toplevel()
        self.dialogNewCanvas.resizable(False, False)
        filePath = resource_path("img/icon.ico")
        self.dialogNewCanvas.iconbitmap(filePath)
        self.dialogNewCanvas.title("New Canvas")
        ttk.Label(self.dialogNewCanvas, text="   Width:").grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.dialogNewCanvas, textvariable=self.canvas_width).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Label(self.dialogNewCanvas, text="px   ").grid(
            row=0, column=2, padx=5, pady=5)
        ttk.Label(self.dialogNewCanvas, text="   Height:").grid(
            row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.dialogNewCanvas, textvariable=self.canvas_height).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Label(self.dialogNewCanvas, text="px   ").grid(
            row=1, column=2, padx=5, pady=5)
        ttk.Button(self.dialogNewCanvas, text="OK", command=self.update_canvas_size).grid(
            row=2, column=1, padx=5, pady=5)

    def update_canvas_size(self):
        # Update the canvas size and scrollbar
        self.image_canvas.delete("all")
        self.image = Image.new(
            "RGB", (self.canvas_width.get(), self.canvas_height.get()), "white")
        self.image_canvas.config(
            width=self.canvas_width.get(), height=self.canvas_height.get())
        self.image_canvas.config(scrollregion=self.image_canvas.bbox(tk.ALL))
        self.x_max = self.canvas_width.get() - 1
        self.y_max = self.canvas_height.get() - 1
        self.height = self.canvas_height.get()
        self.width = self.canvas_width.get()
        self.height_var.set("Height: {}".format(self.height))
        self.width_var.set("Width: {}".format(self.width))

        # Draw center horizontal line
        self.image_canvas.create_line(
            0, self.height/2, self.width, self.height/2, fill="grey")

        # Draw center vertical line
        self.image_canvas.create_line(
            self.width/2, 0, self.width/2, self.height, fill="grey")

        # Configure the canvas scroll region and scrollbar commands

        self.image_canvas.config(
            scrollregion=self.image_canvas.bbox(tk.ALL))
        self.scrollbar_h.config(command=self.image_canvas.xview)
        self.image_canvas.config(xscrollcommand=self.scrollbar_h.set)
        self.scrollbar.config(command=self.image_canvas.yview)
        self.image_canvas.config(yscrollcommand=self.scrollbar.set)
        # Close the dialog
        self.dialogNewCanvas.destroy()

    def zoom(self, factor):
        self.canvas_zoom_factor *= factor
        self.image_canvas.scale("all", 0, 0, factor, factor)

    def upload_image(self):
        # Open a file dialog to select an image file
        file_path = tk.filedialog.askopenfilename(title="Select Image", filetypes=(
            ("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")))
        if file_path:
            # Load the image and add it to the canvas
            self.image = Image.open(file_path)
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.image_canvas.delete("all")
            self.image_id = self.image_canvas.create_image(
                0, 0, anchor="nw", image=self.image_tk)

            # Update the height and width labels with the image size
            self.height = self.image.height
            self.width = self.image.width
            self.height_var.set("Height: {}".format(self.height))
            self.width_var.set("Width: {}".format(self.width))

            # Configure the canvas scroll region and scrollbar commands
            self.image_canvas.config(
                scrollregion=self.image_canvas.bbox(tk.ALL))
            self.scrollbar_h.config(command=self.image_canvas.xview)
            self.image_canvas.config(xscrollcommand=self.scrollbar_h.set)
            self.scrollbar.config(command=self.image_canvas.yview)
            self.image_canvas.config(yscrollcommand=self.scrollbar.set)

            # Resize the canvas to match the image size
            self.image_canvas.config(width=self.width, height=self.height)
            self.image_canvas.itemconfig(self.image_id, image=self.image_tk)

            self.update_coordinate()

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
        self.image_canvas.delete("all")
        self.image_id = self.image_canvas.create_image(
            0, 0, anchor="nw", image=self.image_tk)

        # Update the height and width labels with the image size
        self.height = self.image.height
        self.width = self.image.width
        self.height_var.set("Height: {}".format(self.image.height))
        self.width_var.set("Width: {}".format(self.image.width))
        # Resize the canvas to match the fixed size
        # Configure the canvas scroll region and scrollbar commands
        self.image_canvas.config(
            scrollregion=self.image_canvas.bbox(tk.ALL))
        self.scrollbar_h.config(command=self.image_canvas.xview)
        self.image_canvas.config(xscrollcommand=self.scrollbar_h.set)
        self.scrollbar.config(command=self.image_canvas.yview)
        self.image_canvas.config(yscrollcommand=self.scrollbar.set)
        self.image_canvas.config(width=500, height=500)
        self.x_max = 500 - 1
        self.y_max = 500 - 1

    def set_tool(self, tool):
        self.tool = tool
        if self.tool == TOOL_SELECTOR:
            self.image_canvas.config(cursor="circle")
            self.selector_button.config(relief="sunken",background="lightgrey")
            self.pen_button.config(relief="raised",background="white")
            self.hand_button.config(relief="raised",background="white")
        elif self.tool == TOOL_PEN:
            self.image_canvas.config(cursor="pencil")
            self.selector_button.config(relief="raised",background="white")
            self.pen_button.config(relief="sunken",background="lightgrey")
            self.hand_button.config(relief="raised",background="white")
        elif self.tool == TOOL_HAND:
            self.image_canvas.config(cursor="hand2")
            self.selector_button.config(relief="raised",background="white")
            self.pen_button.config(relief="raised",background="white")
            self.hand_button.config(relief="sunken",background="lightgrey")
        elif self.tool == TOOL_COLOR_SELECTOR:
            self.open_color_picker()

    def on_canvas_drag(self, event):
        # Update the mouse coordinates
        self.mouse_x = event.x
        self.mouse_y = event.y  # Invert the y-coordinate

        # Calculate the adjusted coordinates based on the scroll position
        x_adjusted = self.mouse_x + \
            self.image_canvas.xview()[0] * self.image.width
        y_adjusted = self.mouse_y + \
            self.image_canvas.yview()[0] * self.image.height

        if self.tool == TOOL_HAND:
            self.image_canvas.scan_dragto(event.x, event.y, gain=1)
        elif self.tool == TOOL_PEN and self.drawing:
            if self.prev_x is not None and self.prev_y is not None:
                self.image_canvas.create_line(
                    self.prev_x, self.prev_y, x_adjusted, y_adjusted, fill=self.selected_color, width=2)
            self.prev_x = x_adjusted
            self.prev_y = y_adjusted

    def on_mouse_release(self, event):
        if self.tool == TOOL_PEN:
            self.drawing = False
            self.prev_x = None
            self.prev_y = None

    def on_mouse_move(self, event):
        # Update the mouse coordinates
        self.mouse_x = event.x
        self.mouse_y = event.y  # Invert the y-coordinate

        # Calculate the adjusted coordinates based on the scroll position
        x_adjusted = self.mouse_x + \
            self.image_canvas.xview()[0] * self.image.width
        y_adjusted = self.mouse_y + \
            self.image_canvas.yview()[0] * self.image.height

        # Update the coordinate text
        self.coord_var.set("X-Axis={}, Y-Axis={}".format(
            normalizeValue(x_adjusted / self.width),
            normalizeValue((self.height - y_adjusted) / self.height)))

        # Update the RGB text
        if self.image:
            x = int((x_adjusted - self.x_center) /
                    self.zoom_factor + self.x_center)
            y = int((y_adjusted - self.y_center) /
                    self.zoom_factor + self.y_center)
            if 0 <= x < self.image.width and 0 <= y < self.image.height:
                try:
                    pixel = self.image.getpixel((x, y))
                    if len(pixel) >= 3:
                        r, g, b = pixel[:3]
                        self.rgb_var.set("R={}, G={}, B={}".format(
                            round(r / 255, 4), round(g / 255, 4), round(b / 255, 4)))
                except IndexError:
                    self.rgb_var.set("Error R={}, G={}, B={}".format(
                        round(0 / 255, 4), round(0 / 255, 4), round(0 / 255, 4)))

        # Update the zoom window if it exists
        if self.zoom_canvas:
            self.update_zoom_window()

    def on_mouse_press(self, event):
        # Copy the coordinates and RGB values to the clipboard
        x_adjusted = self.mouse_x + \
            self.image_canvas.xview()[0] * self.image.width
        y_adjusted = self.mouse_y + \
            self.image_canvas.yview()[0] * self.image.height

        x = int((x_adjusted - self.x_center) /
                self.zoom_factor + self.x_center)
        y = int((y_adjusted - self.y_center) /
                self.zoom_factor + self.y_center)
        if self.tool == TOOL_SELECTOR:
            if self.image:
                if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
                    try:
                        pixel = self.image.getpixel((x, y))
                        if len(pixel) >= 3:
                            r, g, b = pixel[:3]
                        else:
                            r, g, b, *_ = pixel
                    except IndexError:
                        r = 0
                        g = 0
                        b = 0

                    coords = "glVertex3f({}, {}, 0.0f);".format(normalizeValue(
                        x / self.width), normalizeValue((self.height - y) / self.height))
                    rgb = "glColor3f({}, {}, {});".format(
                        round(r / 255, 3), round(g / 255, 3), round(b / 255, 3))
                    text = "{}\n{}".format(rgb, coords)
                    pyperclip.copy(text)
                    messagebox.showinfo("Code Copied", text)
        elif self.tool == TOOL_PEN:
            self.drawing = True
            self.prev_x = x
            self.prev_y = y
        elif self.tool == TOOL_HAND:
            self.image_canvas.scan_mark(event.x, event.y)

    def open_color_picker(self):
        color = colorchooser.askcolor(title="Select Color")
        if color[1] is not None:
            self.selected_color = color[1]
        else:
            self.selected_color = "#ffffff"
        self.tool = TOOL_SELECTOR
        self.set_tool(self.tool)

    def update_zoom_window(self):
        # Create an image for the zoom window
        self.x_center = self.mouse_x / self.zoom_factor
        self.y_center = self.mouse_y / self.zoom_factor
        self.zoom_image = Image.new("RGB", (100, 100), "white")
        self.zoom_image_tk = ImageTk.PhotoImage(self.zoom_image)
        self.zoom_canvas.create_image(
            0, 0, anchor="center", image=self.zoom_image_tk)

        # Create a rectangle to show the zoom area on the canvas
        x1 = self.mouse_x - 25
        y1 = self.mouse_y - 25
        x2 = self.mouse_x + 25
        y2 = self.mouse_y + 25
        self.zoom_rect_id = self.image_canvas.create_rectangle(
            x1, y1, x2, y2, outline="red")

        if self.zoom_rect_id:
            # Hide the zoom rectangle
            self.image_canvas.itemconfigure(self.zoom_rect_id, state='hidden')

        if self.image and self.zoom_canvas:
            # Update the zoom rectangle position and size
            x1 = self.mouse_x - 25
            y1 = self.mouse_y - 25
            x2 = self.mouse_x + 25
            y2 = self.mouse_y + 25
            self.image_canvas.coords(self.zoom_rect_id, x1, y1, x2, y2)

            # Update the zoom center position
            self.zoom_center_x = self.mouse_x / self.zoom_factor
            self.zoom_center_y = self.mouse_y / self.zoom_factor

            # Schedule the zoom image update after a delay
            self.after(25, self.update_zoom_image)

            # Redraw the zoom rectangle
            x1 = self.mouse_x - 25
            y1 = self.mouse_y - 25
            x2 = self.mouse_x + 25
            y2 = self.mouse_y + 25
            self.image_canvas.coords(self.zoom_rect_id, x1, y1, x2, y2)

    def update_zoom_image(self):
        # Update the zoom window image
        x = int(self.zoom_center_x - 50 / self.zoom_factor)
        y = int(self.zoom_center_y - 50 / self.zoom_factor)
        x1 = max(x, 0)
        y1 = max(y, 0)
        x2 = min(x + 100 // self.zoom_factor, self.image.width - 1) 
        y2 = min(y + 100 // self.zoom_factor, self.image.height - 1)

        # add padding if the zoomed image is not complete
        if x2 == self.image.width and x1 > 0:
            x1 = max(x1 - (x2 - self.image.width) - 1, 0)
        if y2 == self.image.height and y1 > 0:
            y1 = max(y1 - (y2 - self.image.height) - 1, 0)

        self.zoom_image = self.image.crop((x1, y1, x2, y2))
        self.zoom_image = self.zoom_image.resize((100, 100), Image.BILINEAR)

        left_pad = 0
        right_pad = 0
        top_pad = 0
        bottom_pad = 0
        # add one pixel padding if the zoomed image is not complete
        if x2 - x1 < 100 or y2 - y1 < 100:
            if self.mouse_x <= 150:
                left_pad = abs(100 - (x2-x1))
            else:
                right_pad = abs(100 - (x2-x1))

            if self.mouse_y <= 150:
                top_pad = abs(100 - (y2-y1))
            else:
                bottom_pad = abs(100 - (y2-y1))

            self.zoom_image = ImageOps.expand(
                self.zoom_image, border=(left_pad - right_pad, top_pad-bottom_pad, right_pad, bottom_pad), fill='white')

        self.zoom_image_tk = ImageTk.PhotoImage(self.zoom_image)
        self.zoom_canvas.create_image(
            0, 0, anchor="nw", image=self.zoom_image_tk)

        # Draw a crosshair in the center of the zoom window
        x1 = 0
        y1 = 50
        x2 = 100
        y2 = 50
        self.zoom_canvas.create_line(x1, y1, x2, y2, fill="red")

        x1 = 50
        y1 = 0
        x2 = 50
        y2 = 100
        self.zoom_canvas.create_line(x1, y1, x2, y2, fill="red")

    def set_coordinates(self, x_min, x_max, y_min, y_max, x_center, y_center):
        # Set the coordinate limits and center point
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min  # Swap y_min and y_max
        self.y_max = y_max
        self.x_center = x_center
        self.y_center = y_center

    def update_coordinate(self):
        # Define the zoomed-in region to cover the entire image
        self.x_min = 0
        self.x_max = self.width - 1
        self.y_min = 0
        self.y_max = self.height - 1

        # Center coordinates of the zoomed-in region
        self.x_center = 0  # (self.x_min + self.x_max) / 2
        self.y_center = 0  # (self.y_min + self.y_max) / 2

    def save_to_clipboard(self):
        # Copy the coordinates and RGB values to the clipboard
        x_adjusted = self.mouse_x + \
            self.image_canvas.xview()[0] * self.image.width
        y_adjusted = self.mouse_y + \
            self.image_canvas.yview()[0] * self.image.height

        x = int((x_adjusted - self.x_center) /
                self.zoom_factor + self.x_center)
        y = int((y_adjusted - self.y_center) /
                self.zoom_factor + self.y_center)

        if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
            try:
                pixel = self.image.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[:3]
                else:
                    r, g, b, *_ = pixel
            except IndexError:
                r = 0
                g = 0
                b = 0

            coords = "glVertex3f({}, {}, 0.0f);".format(normalizeValue(
                x / self.width), normalizeValue((self.height - y) / self.height))
            rgb = "glColor3f({}, {}, {});".format(
                round(r / 255, 3), round(g / 255, 3), round(b / 255, 3))
            text = "{}\n{}".format(rgb, coords)
            pyperclip.copy(text)
            messagebox.showinfo("Code Copied", text)

    def show_about_dialog(self):
        # Create a Toplevel window for the about dialog
        about_window = tk.Toplevel(self.master)
        about_window.minsize(300, 160)
        about_window.maxsize(300, 160)
        about_window.title("About Glut Image Coordinator")
        filePath = resource_path("img/icon.ico")
        about_window.iconbitmap(filePath)

        # Add a label with the program name and version
        label1 = ttk.Label(
            about_window, text="Glut Image Coordinator v1.4", font=("Helvetica", 14))
        label1.pack(pady=10)

        # Add a label with the developer name and email
        label2 = ttk.Label(
            about_window, text="Developed by Jahid Hasan\nEmail: vdjsovaj@gmail.com",  font=("Helvetica", 12))
        label2.pack(padx=10, pady=10)

        # Add a button to close the about dialog
        close_button = ttk.Button(
            about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)

    def on_contact_us_click(self):
        # Create a new Toplevel window for the Contact Us dialog
        top = Toplevel(self.master)
        top.minsize(400, 160)
        top.maxsize(400, 160)
        top.title("Contact Us")
        filePath = resource_path("img/icon.ico")
        top.iconbitmap(filePath)
        # Add some text to the window
        ttk.Label(top, text="For support or inquiries, please email us at:", font=("Helvetica", 14)).pack(
            padx=10, pady=10)
        ttk.Label(top, text="vdjsovaj@gmail.com",
                  font=("Helvetica", 12)).pack()
        ttk.Label(top, text="We usually respond within 24 hours.",
                  font=("Helvetica", 12)).pack()

        # Add a button to close the window
        ttk.Button(top, text="Close", command=top.destroy).pack(
            padx=10, pady=10)

    def open_graph_range_setting(self):
        # Create a new Toplevel window for the Contact Us dialog
        top = tk.Toplevel(self.master)
        top.minsize(400, 200)
        top.maxsize(400, 200)
        top.title("Graph Range Setting")
        filePath = resource_path("img/icon.ico")
        top.iconbitmap(filePath)

        if not self.config.has_section('graph'):
            self.config.add_section('graph')

        # Get initial values for graph_max and graph_min
        graph_max = self.config.getint('graph', 'max', fallback=1)
        graph_min = self.config.getint('graph', 'min', fallback=0)

        # Create a ttk.Scale widget with a range of 0 to 100

        ttk.Label(top, text="Set Graph Max Value", font=(
            "Helvetica", 12)).pack(fill=X, padx=20, pady=2)
        self.graph_max_scale = ttk.Scale(
            top, from_=1.0, to=100.0, command=lambda x: self.on_graph_max_scale_scroll(x))
        self.maxVar = tk.StringVar()
        self.maxVar.set(f"Graph max: {graph_max}")
        self.graph_max_scale.set(float(graph_max))
        # Pack the Scale widget into the window
        self.graph_max_scale.pack(fill=X, padx=20, pady=2)

        self.graph_max_label = ttk.Label(top,
                                         textvariable=self.maxVar, font=("Helvetica", 10))
        self.graph_max_label.pack(fill=X, padx=20, pady=2)

        ttk.Label(top, text="Set Graph Min Value", font=(
            "Helvetica", 12)).pack(fill=X, padx=20, pady=2)

        self.graph_min_scale = ttk.Scale(
            top, from_=0.0, to=100.0, command=lambda x: self.on_graph_min_scale_scroll(x))
        self.minVar = tk.StringVar()
        self.minVar.set(f"Graph min: {0 - graph_min}")
        self.graph_min_scale.set(float(graph_min))
        # Pack the Scale widget into the window
        self.graph_min_scale.pack(fill=X, padx=20, pady=2)

        self.graph_min_label = ttk.Label(top,
                                         textvariable=self.minVar, font=("Helvetica", 10))
        self.graph_min_label.pack(fill=X, padx=20, pady=2)

        # Add a button to close the window
        ttk.Button(top, text="Save", command=lambda: self.on_graph_setting_save_click(top)).pack(
            padx=10, pady=10)

    def on_graph_max_scale_scroll(self, x):
        self.maxVar.set(f"Graph max: {int(float(x))}")

    def on_graph_min_scale_scroll(self, x):
        self.minVar.set(f"Graph min: {0 - int(float(x))}")

    def on_graph_setting_save_click(self, top):
        graph_max = int(self.graph_max_scale.get())
        graph_min = int(self.graph_min_scale.get())
        # Save values to configuration file
        # Save values to configuration file
        self.config.set('graph', 'max', str(graph_max))
        self.config.set('graph', 'min', str(graph_min))
        with open('coordinator.ini', 'w') as f:
            self.config.write(f)
        top.destroy()

    def templateCodeWindow(self):
        top = tk.Toplevel(self.master)
        top.geometry("500x400")
        top.minsize(500, 400)
        top.maxsize(500, 400)
        top.title("Template Code")
        filePath = resource_path("img/icon.ico")
        top.iconbitmap(filePath)

        sample_code_text = '''
            #include<windows.h>
            #include <GL/glut.h>

            void display(){
                glClear(GL_COLOR_BUFFER_BIT);
                // write your code here 
                glutSwapBuffers();
            }


            int main(int argc, char **argv){
                glutInit(&argc, argv);
                glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);

                glutInitWindowSize(500, 500);
                glutCreateWindow("Glut Image Coordinator");
                glClearColor(0.502f, 0.502f, 0.702f, 1.0f);
                glMatrixMode(GL_PROJECTION);
                glLoadIdentity();
                gluOrtho2D(0.0f, 1.0f, 0.0f, 1.0f);
                glMatrixMode(GL_MODELVIEW);
                glutDisplayFunc(display);
                glutMainLoop();
                return 0;
            }
            '''
        sample_code = tk.Text(top, wrap="word")
        sample_code.pack(fill="both", expand=True)
        sample_code.insert(tk.END, sample_code_text)


if __name__ == "__main__":
    try:
        root = tk.Tk()
        filePath = resource_path("img/icon.ico")
        root.iconbitmap(filePath)
        app = ImageViewer(master=root)
        app.set_coordinates(0, 500, 0, 500, 0, 0)
        root.bind("<Control-x>", lambda event: app.save_to_clipboard())
        app.mainloop()
    except Exception as e:
        print("An error occurred: ", e)
