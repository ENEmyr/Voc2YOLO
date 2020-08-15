import tkinter as tk
from tkinter import messagebox
import threading
import time
from tkinter import filedialog
from os import mkdir
from os.path import join, abspath, exists
from voc2yolo import voc2yolo

imgs_folder = ''
labels_folder = ''
out_folder = ''

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder='PLACEHOLDER', color='grey', width=10):
        super().__init__(master, width=width)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind('<FocusIn>', self.foc_in)
        self.bind('<FocusOut>', self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

window = tk.Tk()

window.title('PascalVoc2YoLo')

imgs_path_txt = tk.Label(master=window, text='Path to directory contains PascalVoc Images')
imgs_path_txt.grid(row=1)
imgs_path_btn = tk.Button(master=window, text='Select directory')
imgs_path_btn.grid(row=1, column=1)

labels_path_txt = tk.Label(master=window, text='Path to directory contains PascalVoc Labels')
labels_path_txt.grid(row=2)
labels_path_btn = tk.Button(master=window, text='Select directory')
labels_path_btn.grid(row=2, column=1)

out_path_txt = tk.Label(master=window, text='Path to output directory')
out_path_txt.grid(row=3)
out_path_btn = tk.Button(master=window, text='Select directory')
out_path_btn.grid(row=3, column=1)

ratio_txt = tk.Label(master=window, text='Dataset Spliting Ratio (0-10)')
ratio_txt.grid(row=4)
train_ratio_txt = tk.Label(master=window, text='Train')
train_ratio_txt.grid(row=5, column=0)
train_ratio = EntryWithPlaceholder(master=window, placeholder='0')
train_ratio.grid(row=6, column=1)

test_ratio_txt = tk.Label(master=window, text='Test')
test_ratio_txt.grid(row=7, column=0)
test_ratio = EntryWithPlaceholder(master=window, placeholder='0')
test_ratio.grid(row=7, column=1)

val_ratio_txt = tk.Label(master=window, text='Val')
val_ratio_txt.grid(row=8, column=0)
val_ratio = EntryWithPlaceholder(master=window, placeholder='0')
val_ratio.grid(row=8, column=1)

show_imgs_path_txt = tk.Label(master=window, text='PascalVoc Images Path : ')
show_imgs_path_txt.grid(row=9)
show_imgs_path_txt_2 = tk.Label(master=window, text='None')
show_imgs_path_txt_2.grid(row=9, column=1)

show_labels_path_txt = tk.Label(master=window, text='PascalVoc Labels Path : ')
show_labels_path_txt.grid(row=10)
show_labels_path_txt_2 = tk.Label(master=window, text='None')
show_labels_path_txt_2.grid(row=10, column=1)

show_out_path_txt = tk.Label(master=window, text='Output Path : ')
show_out_path_txt.grid(row=11)
show_out_path_txt_2 = tk.Label(master=window, text='None')
show_out_path_txt_2.grid(row=11, column=1)

clear_btn = tk.Label(master=window, text='Clear', width=30, height=3, bg='blue', fg='white')
clear_btn.grid(row=12, column=0)
proceed_btn = tk.Label(master=window, text='Proceed', width=30, height=3, bg='green', fg='white')
proceed_btn.grid(row=12, column=1)

def handle_imgs_path_click(event):
    global imgs_folder
    imgs_folder = filedialog.askdirectory()
    if len(imgs_folder) > 30:
        show_imgs_path_txt_2['text'] = f'{imgs_folder[:15]}...{imgs_folder[len(imgs_folder)-15:]}'
    else:
        show_imgs_path_txt_2['text'] = imgs_folder

def handle_labels_path_click(event):
    global labels_folder
    labels_folder = filedialog.askdirectory()
    if len(labels_folder) > 30:
        show_labels_path_txt_2['text'] = f'{imgs_folder[:15]}...{labels_folder[len(labels_folder)-15:]}'
    else:
        show_labels_path_txt_2['text'] = labels_folder

def handle_out_path_click(event):
    global out_folder
    out_folder = filedialog.askdirectory()
    if len(out_folder) > 30:
        show_out_path_txt_2['text'] = f'{imgs_folder[:15]}...{out_folder[len(out_folder)-15:]}'
    else:
        show_out_path_txt_2['text'] = out_folder

def handle_clear_click(event):
    reset()

def reset():
    global imgs_folder
    global labels_folder
    global out_folder
    imgs_folder = ''
    labels_folder = ''
    out_folder = ''
    show_imgs_path_txt_2['text'] = 'None'
    show_labels_path_txt_2['text'] = 'None'
    show_out_path_txt_2['text'] = 'None'
    train_ratio.delete(0, last='end')
    test_ratio.delete(0, last='end')
    val_ratio.delete(0, last='end')
    proceed_btn['text'] = 'Proceed'
    proceed_btn['state'] = tk.NORMAL
    clear_btn['state'] = tk.NORMAL

def convert_dataset():
    out_imgs_path = join(out_folder, 'images')
    out_labels_path = join(out_folder, 'labels')
    ratios = [train_ratio.get(), test_ratio.get(), val_ratio.get()]
    if not exists(out_imgs_path):
        mkdir(out_imgs_path)
    if not exists(out_labels_path):
        mkdir(out_labels_path)
    if all([x in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'] for x in ratios]):
        ratios = list(map(lambda x: int(x), ratios))
        if all(x == 0 for x in ratios):
            voc2yolo(out_folder, imgs_folder, labels_folder)
        else:
            if ratios[0] + ratios[1] != 10 or ratios[0] == ratios[2]:
                messagebox.showinfo('Convert Status', f'Invalid Ratios!!!')
                return reset()
            else:
                mkdir(join(out_imgs_path, 'train'))
                mkdir(join(out_imgs_path, 'test'))
                mkdir(join(out_imgs_path, 'val'))
                mkdir(join(out_labels_path, 'train'))
                mkdir(join(out_labels_path, 'test'))
                mkdir(join(out_labels_path, 'val'))
                voc2yolo(out_folder, imgs_folder, labels_folder, ratios)
    else:
        messagebox.showinfo('Convert Status', f'Invalid Ratios!!!')
        return reset()
    messagebox.showinfo('Convert Status', f'Done!\nYour converted dataset can be found in {out_folder}')
    return reset()

def handle_proceed_click(event):
    global imgs_folder
    global labels_folder
    global out_folder
    worker = threading.Thread(target=convert_dataset, args=())
    worker.start()
    proceed_btn['text'] = 'Running'
    proceed_btn['state'] = tk.DISABLED
    clear_btn['state'] = tk.DISABLED

imgs_path_btn.bind('<Button-1>', handle_imgs_path_click)
labels_path_btn.bind('<Button-1>', handle_labels_path_click)
out_path_btn.bind('<Button-1>', handle_out_path_click)
proceed_btn.bind('<Button-1>', handle_proceed_click)
clear_btn.bind("<Button-1>", handle_clear_click)

window.mainloop()
