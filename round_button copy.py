import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance

class RoundButton(Canvas):
    def __init__(self, parent, width, height, corner_radius, padding=10, bg_color="#ffffff", fg_color="black", alpha=128, text="", font_size=12, command=None):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.corner_radius = corner_radius
        self.alpha = alpha
        self.text = text
        self.font_size = font_size

        self.padding = padding

        self.rect_id = self.create_round_rectangle(padding, padding, width-padding, height-padding, radius=corner_radius)
        self.text_id = self.create_text(width/2, height/2, text=text, fill=fg_color, font=('Helvetica', font_size, 'bold'))

        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.command:
            self.command()

    def create_round_rectangle(self, x1, y1, x2, y2, radius=25):
        width = x2 - x1
        height = y2 - y1
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle((0, 0, width, height), radius, fill=(255, 255, 255, self.alpha))

        shadow = image.filter(ImageFilter.GaussianBlur(10))
        shadow = ImageEnhance.Brightness(shadow).enhance(0.5)

        self.shadow_image = ImageTk.PhotoImage(shadow)
        self.round_rect_image = ImageTk.PhotoImage(image)

        self.create_image(0, 0, image=self.shadow_image, anchor=tk.NW)
        self.create_image(0, 0, image=self.round_rect_image, anchor=tk.NW)

        return self.create_rectangle(x1, y1, x2, y2, outline='', width=0)

    def on_resize(self, event):
        self.update_button()

    def update_button(self):
        self.coords(self.rect_id, self.padding, self.padding, self.winfo_width() - self.padding, self.winfo_height() - self.padding)
        self.update_text_position()

    def update_text_position(self):
        bbox = self.bbox(self.text_id)
        if bbox:
            x1, y1, x2, y2 = bbox
            text_width = x2 - x1
            text_height = y2 - y1
            self.coords(self.text_id, (self.winfo_width() / 2, self.winfo_height() / 2))

    def set_bg_color(self, color):
        self.bg_color = color
        self.itemconfig(self.rect_id, fill=color, outline=color)
        self.update_button()

    def set_fg_color(self, color):
        self.fg_color = color
        self.itemconfig(self.text_id, fill=color)
        self.update_button()

    def set_text(self, text):
        self.text = text
        self.itemconfig(self.text_id, text=text)
        self.update_button()

    def set_font_size(self, font_size):
        self.font_size = font_size
        self.itemconfig(self.text_id, font=('Helvetica', font_size, 'bold'))
        self.update_button()

    def on_resize(self, event):
        self.update_button()
