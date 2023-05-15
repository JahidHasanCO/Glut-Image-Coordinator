import tkinter as tk
from tkinter import Menu, Frame, BOTTOM, X, Label, Toplevel, Button
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import pyperclip
import os
import sys
import tkinter.ttk as ttk
import configparser
from util.get_resource import *
from util.normalization import normalizeValue


graph_max = 1
graph_min = 0


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
        self.master.geometry("800x600")


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

        # Adding File Menu and commands
        file = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file)
        file.add_command(label='New Window', command=self.create_new_window)
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
        image_viewer = ImageViewer(new_window)

    def create_widgets(self):

        # Create a frame to hold the canvas and scrollbar
        self.frame = ttk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Create an image canvas to display the uploaded image
        self.image_canvas = tk.Canvas(self.frame, borderwidth=1, relief="solid")
        self.image_canvas.grid(row=0, column=0)
        self.image_canvas.config(cursor="circle")

        # Bind the mouse events to the canvas
        self.image_canvas.bind("<Motion>", self.on_mouse_move)
        self.image_canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Create a scrollbar for the canvas
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.image_canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.image_canvas.config(yscrollcommand=self.scrollbar.set)

        self.right_frame = ttk.Frame(self.frame,width=200)
        self.right_frame.grid(row=0, column=2, sticky="nsew")

        self.scrollbar_h = ttk.Scrollbar(self.frame, orient="horizontal", command=self.image_canvas.xview)
        self.scrollbar_h.grid(row=1, column=0, sticky="ew")
        self.image_canvas.config(xscrollcommand=self.scrollbar_h.set)


        # Create a frame to hold the buttons
        self.bottom_frame = ttk.Frame(self.master)
        self.bottom_frame.grid(row=1, column=0, sticky="nsew")

        self.zoom_canvas = tk.Canvas(
            self.bottom_frame, width=200, height=200, borderwidth=1, relief="solid")
        self.zoom_canvas.grid(row=0, column=0, sticky="nsew")
        self.update_zoom_window()

        self.bottom_output_frame = tk.Frame(self.bottom_frame)
        self.bottom_output_frame.grid(row=0, column=1, sticky="nsew")
        # create a label to display "Image Information" text
        label = ttk.Label(
            self.bottom_output_frame, text="Image Information", font=("Helvetica", 14))
        label.grid(row=0, column=0, sticky="nsew")

        # Create a label to display the height of the image
        self.height_var = tk.StringVar()
        self.height_var.set("Image Height: 0")
        self.height_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.height_var, font=("Helvetica", 12))
        self.height_label.grid(row=1, column=0, sticky="nsew")

        # Create a label to display the width of the image
        self.width_var = tk.StringVar()
        self.width_var.set("Image Width: 0")
        self.width_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.width_var, font=("Helvetica", 12))
        self.width_label.grid(row=2, column=0, sticky="nsew")

        self.coord_var = tk.StringVar()
        self.coord_var.set("X-Axis=0, Y-Axis=0")
        coord_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.coord_var, font=("Helvetica", 12))
        coord_label.grid(row=3, column=0, sticky="nsew")

        self.rgb_var = tk.StringVar()
        self.rgb_var.set("R=0, G=0, B=0")
        rgb_label = ttk.Label(
            self.bottom_output_frame, textvariable=self.rgb_var, font=("Helvetica", 12))
        rgb_label.grid(row=4, column=0, sticky="nsew")

        # Configure the grid layout
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.bottom_output_frame.columnconfigure(1, weight=1)

        
        self.upload_placeholder_image()

    def upload_image(self):
        # Open a file dialog to select an image file
        file_path = tk.filedialog.askopenfilename(title="Select Image", filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")))
        if file_path:
            # Load the image and add it to the canvas
            self.image = Image.open(file_path)
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.image_id = self.image_canvas.create_image(
            0, 0, anchor="nw", image=self.image_tk)
            self.image_canvas.config(width=self.image.width, height=self.image.height)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor="nw", image=self.image)
            self.image_canvas.config(scrollregion=self.image_canvas.bbox(tk.ALL))
            # Add the horizontal scrollbar
            self.scrollbar_h.config(command=self.image_canvas.xview)
            self.image_canvas.config(xscrollcommand=self.scrollbar_h.set)
            # Add the vertical scrollbar
            self.scrollbar.config(command=self.image_canvas.yview)
            self.image_canvas.config(yscrollcommand=self.scrollbar.set)

            # Update the height and width labels with the image size
            self.height = self.image.height
            self.width = self.image.width
            self.height_var.set("Height: {}".format(self.height))
            self.width_var.set("Width: {}".format(self.width))
            

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
        self.coord_var.set("X-Axis={}, Y-Axis={}".format(normalizeValue(self.mouse_x / self.width),
                        normalizeValue((self.height - self.mouse_y) / self.height)))

        # Update the RGB text
        if self.image:
            x = int((self.mouse_x - self.x_center) /
                    self.zoom_factor + self.x_center)
            y = int((self.mouse_y - self.y_center) /
                    self.zoom_factor + self.y_center)
            if x >= 0 and x < self.image.width and y >= 0 and y < self.image.height:
                try:
                    pixel = self.image.getpixel((x, y))
                    if len(pixel) >= 3:
                        r, g, b = pixel[:3]
                        self.rgb_var.set("R={}, G={}, B={}".format(
                            round(r/255, 4), round(g/255, 4), round(b/255, 4)))
                except IndexError:
                    self.rgb_var.set("Error R={}, G={}, B={}".format(
                        round(0/255, 4), round(0/255, 4), round(0/255, 4)))

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
                try:
                    pixel = self.image.getpixel((x, y))
                    if len(pixel) >= 3:
                        r, g, b = pixel[:3]
                        # rest of the code
                    else:
                        r, g, b, *_ = self.image.getpixel((x, y))
                        # handle the case where the pixel values are not RGB
                except IndexError:
                    r = 0
                    g = 0
                    b = 0
                coords = f"glVertex3f({normalizeValue(x/500)}f, {normalizeValue((self.image_canvas.winfo_height() - y)/500)}f , 0.0f);"
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
                try:
                    pixel = self.image.getpixel((x, y))
                    if len(pixel) >= 3:
                        r, g, b = pixel[:3]
                        # rest of the code
                    else:
                        r, g, b, *_ = self.image.getpixel((x, y))
                        # handle the case where the pixel values are not RGB
                except IndexError:
                    r = 0
                    g = 0
                    b = 0
                coords = f"glVertex3f({normalizeValue(x/500)}f, {normalizeValue((self.image_canvas.winfo_height() - y)/500)}f , 0.0f);"
                rgb = f"glColor3f({round(r/225,3)}f, {round(g/225,3)}f, {round(b/225,3)}f);"
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
            about_window, text="Glut Image Coordinator v1.3", font=("Helvetica", 14))
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
        top.minsize(300, 160)
        top.maxsize(300, 160)
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
        with open('config.ini', 'w') as f:
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
        app.set_coordinates(0, 500, 0, 580, 0, 0)
        root.bind("<Control-x>", lambda event: app.save_to_clipboard())
        # root.bind("<Control-=>", lambda event: app.zoom_in())
        # root.bind("<Control-minus>", lambda event: app.zoom_out())
        app.mainloop()
    except Exception as e:
        print("An error occurred: ", e)
