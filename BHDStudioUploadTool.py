import base64
import math
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import threading
import tkinter.scrolledtext as scrolledtextwidget
import webbrowser
import zipfile
from configparser import ConfigParser
from ctypes import windll
from io import BytesIO
from tkinter import filedialog, StringVar, ttk, messagebox, NORMAL, DISABLED, N, S, W, E, Toplevel, \
    LabelFrame, END, Label, Checkbutton, OptionMenu, Entry, HORIZONTAL, SUNKEN, Button, TclError, font, Menu, Text, \
    INSERT, colorchooser, Frame, Scrollbar, VERTICAL, PhotoImage, BooleanVar, Listbox, SINGLE, CENTER, WORD, LEFT, \
    Spinbox

import awsmfunc
import pyperclip
import requests
import torf
import vapoursynth as vs
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from custom_hovertip import CustomTooltipLabel
from imdb import Cinemagoer
from pymediainfo import MediaInfo
from tkinterdnd2 import DND_FILES, TkinterDnD
from torf import Torrent

from Packages.About import openaboutwindow
from Packages.icon import base_64_icon, imdb_icon, tmdb_icon, bhd_upload_icon, bhd_upload_icon_disabled
from Packages.show_streams import stream_menu
from Packages.tmdb_key import tmdb_api_key
from Packages.user_pw_key import crypto_key

# check if program had a file dropped/any commands on the .exe or .pyscript upon launch
try:  # if it does set dropped file/command to a variable
    cli_command = sys.argv[1]
except IndexError:  # if it doesn't set variable to None
    cli_command = None

# determine if program is ran from exe or py
if pathlib.Path(sys.argv[0]).suffix == '.exe':
    app_type = 'bundled'
else:
    app_type = 'script'

# Set variable to True if you want errors to pop up in window + console, False for console only
if app_type == 'bundled':
    enable_error_logger = True  # Change this to false if you don't want to log errors to pop up window
elif app_type == 'script':
    enable_error_logger = False  # Enable this to true for debugging in dev environment

# Set main window title variable
main_root_title = "BHDStudio Upload Tool v1.33"

# create runtime folder if it does not exist
pathlib.Path(pathlib.Path.cwd() / 'Runtime').mkdir(parents=True, exist_ok=True)

# define config file and settings
config_file = 'Runtime/config.ini'  # Creates (if it doesn't exist) and defines location of config.ini
config = ConfigParser()
config.read(config_file)

# torrent settings
if not config.has_section('torrent_settings'):
    config.add_section('torrent_settings')
if not config.has_option('torrent_settings', 'tracker_url'):
    config.set('torrent_settings', 'tracker_url', '')
if not config.has_option('torrent_settings', 'default_path'):
    config.set('torrent_settings', 'default_path', '')

# encoder name
if not config.has_section('encoder_name'):
    config.add_section('encoder_name')
if not config.has_option('encoder_name', 'name'):
    config.set('encoder_name', 'name', '')

# bhd upload api
if not config.has_section('bhd_upload_api'):
    config.add_section('bhd_upload_api')
if not config.has_option('bhd_upload_api', 'key'):
    config.set('bhd_upload_api', 'key', '')

# live release
if not config.has_section('live_release'):
    config.add_section('live_release')
if not config.has_option('live_release', 'password'):
    config.set('live_release', 'password', '')
if not config.has_option('live_release', 'value'):
    config.set('live_release', 'value', '')

# nfo font
if not config.has_section('nfo_pad_font_settings'):
    config.add_section('nfo_pad_font_settings')
if not config.has_option('nfo_pad_font_settings', 'font'):
    config.set('nfo_pad_font_settings', 'font', '')
if not config.has_option('nfo_pad_font_settings', 'style'):
    config.set('nfo_pad_font_settings', 'style', '')
if not config.has_option('nfo_pad_font_settings', 'size'):
    config.set('nfo_pad_font_settings', 'size', '')

# # nfo color scheme
if not config.has_section('nfo_pad_color_settings'):
    config.add_section('nfo_pad_color_settings')
if not config.has_option('nfo_pad_color_settings', 'text'):
    config.set('nfo_pad_color_settings', 'text', '')
if not config.has_option('nfo_pad_color_settings', 'background'):
    config.set('nfo_pad_color_settings', 'background', '')

# check for updates
if not config.has_section('check_for_updates'):
    config.add_section('check_for_updates')
if not config.has_option('check_for_updates', 'value'):
    config.set('check_for_updates', 'value', 'True')
if not config.has_option('check_for_updates', 'ignore_version'):
    config.set('check_for_updates', 'ignore_version', '')

# window location settings
if not config.has_section('save_window_locations'):
    config.add_section('save_window_locations')
if not config.has_option('save_window_locations', 'bhdstudiotool'):
    config.set('save_window_locations', 'bhdstudiotool', '')
if not config.has_option('save_window_locations', 'torrent_window'):
    config.set('save_window_locations', 'torrent_window', '')
if not config.has_option('save_window_locations', 'nfo_pad'):
    config.set('save_window_locations', 'nfo_pad', '')
if not config.has_option('save_window_locations', 'uploader'):
    config.set('save_window_locations', 'uploader', '')
if not config.has_option('save_window_locations', 'movie_info'):
    config.set('save_window_locations', 'movie_info', '')
if not config.has_option('save_window_locations', 'about_window'):
    config.set('save_window_locations', 'about_window', '')
if not config.has_option('save_window_locations', 'image_viewer'):
    config.set('save_window_locations', 'image_viewer', '')

# screenshot settings
if not config.has_section('screenshot_settings'):
    config.add_section('screenshot_settings')
if not config.has_option('screenshot_settings', 'semi_auto_count'):
    config.set('screenshot_settings', 'semi_auto_count', '')

# last used folder
if not config.has_section('last_used_folder'):
    config.add_section('last_used_folder')
if not config.has_option('last_used_folder', 'path'):
    config.set('last_used_folder', 'path', '')

# write options to config if they do not exist
with open(config_file, 'w') as configfile:
    config.write(configfile)


# root
def root_exit_function():
    def save_config_information_root():
        # root exit parser
        root_exit_parser = ConfigParser()
        root_exit_parser.read(config_file)

        # save main gui window position/geometry
        if root.wm_state() == 'normal':
            if root_exit_parser['save_window_locations']['bhdstudiotool'] != root.geometry():
                if int(root.geometry().split('x')[0]) >= root_window_width or \
                        int(root.geometry().split('x')[1].split('+')[0]) >= root_window_height:
                    root_exit_parser.set('save_window_locations', 'bhdstudiotool', root.geometry())
                    with open(config_file, 'w') as root_exit_config_file:
                        root_exit_parser.write(root_exit_config_file)

    # check for opened windows before closing
    open_tops = False  # Set variable for open toplevel windows
    for widget in root.winfo_children():  # Loop through roots children
        if isinstance(widget, Toplevel):  # If any of roots children is a TopLevel window
            open_tops = True  # Set variable for open tops to True
    if open_tops:  # If open_tops is True
        confirm_exit = messagebox.askyesno(title='Prompt', message="Are you sure you want to exit the program?\n\n"
                                                                   "Warning: This will close all windows", parent=root)
        if confirm_exit:  # If user wants to exit, kill app and all of it's children
            save_config_information_root()
            root.destroy()  # root destroy
    if not open_tops:  # If no top levels are found, exit the program without prompt
        save_config_information_root()
        root.destroy()  # root destroy


root = TkinterDnD.Tk()
root.title(main_root_title)
root.iconphoto(True, PhotoImage(data=base_64_icon))
root.configure(background="#363636")
root_window_height = 760
root_window_width = 720
if config['save_window_locations']['bhdstudiotool'] == '':
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (root_window_width / 2))
    y_coordinate = int((screen_height / 2) - (root_window_height / 2))
    root.geometry(f"{root_window_width}x{root_window_height}+{x_coordinate}+{y_coordinate}")
elif config['save_window_locations']['bhdstudiotool'] != '':
    root.geometry(config['save_window_locations']['bhdstudiotool'])
root.protocol('WM_DELETE_WINDOW', root_exit_function)

# Block of code to fix DPI awareness issues on Windows 7 or higher
try:
    windll.shcore.SetProcessDpiAwareness(2)  # if your Windows version >= 8.1
except(Exception,):
    windll.user32.SetProcessDPIAware()  # Windows 8.0 or less
# Block of code to fix DPI awareness issues on Windows 7 or higher

for n in range(4):
    root.grid_columnconfigure(n, weight=1)
for n in range(5):
    root.grid_rowconfigure(n, weight=1)


# hoverbutton class
class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["foreground"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['foreground'] = self['activeforeground']

    def on_leave(self, e):
        self['foreground'] = self.defaultBackground


detect_font = font.nametofont("TkDefaultFont")  # Get default font value into Font object
set_font = detect_font.actual().get("family")
set_font_size = detect_font.actual().get("size")
detect_fixed_font = font.nametofont("TkFixedFont")
set_fixed_font = detect_fixed_font.actual().get("family")
color1 = "#434547"

# Custom Tkinter Theme-----------------------------------------
custom_style = ttk.Style()
custom_style.theme_create('jlw_style', parent='alt', settings={
    # Notebook Theme Settings -------------------
    "TNotebook": {"configure": {"tabmargins": [5, 5, 5, 0], 'background': "#363636"}},
    "TNotebook.Tab": {
        "configure": {"padding": [5, 1], "background": 'grey', 'foreground': 'white', 'focuscolor': ''},
        "map": {"background": [("selected", '#434547')], "expand": [("selected", [1, 1, 1, 0])]}},
    # Notebook Theme Settings -------------------
    # ComboBox Theme Settings -------------------
    'TCombobox': {'configure': {'selectbackground': "#c0c0c0", 'fieldbackground': "#c0c0c0", "lightcolor": "green",
                                'background': "white", 'foreground': "black", 'selectforeground': "black"}}},
                          # ComboBox Theme Settings -------------------
                          )
custom_style.theme_use('jlw_style')  # Enable the use of the custom theme
custom_style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                      {'children': [('Horizontal.Progressbar.pbar',
                                     {'side': 'left', 'sticky': 'ns'})],
                       'sticky': 'nswe'}),
                     ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
# set initial text
custom_style.configure('text.Horizontal.TProgressbar', text='', anchor='center', background="#3498db")
custom_style.master.option_add('*TCombobox*Listbox.background', "grey")
custom_style.master.option_add('*TCombobox*Listbox.selectBackground', "grey")
custom_style.master.option_add('*TCombobox*Listbox.selectForeground', "#3498db")


# ------------------------------------------ Custom Tkinter Theme


# Logger class, handles all traceback/stdout errors for program, writes to file and to window -------------------------
class Logger(object):  # Logger class, this class puts stderr errors into a window and file at the same time
    def __init__(self):
        self.terminal = sys.stderr  # Redirects sys.stderr

    def write(self, message):
        global info_scrolled
        self.terminal.write(message)
        try:
            info_scrolled.config(state=NORMAL)
            if str(message).rstrip():
                info_scrolled.insert(END, str(message).strip())
            if not str(message).rstrip():
                info_scrolled.insert(END, f'{str(message)}\n')
            info_scrolled.see(END)
            info_scrolled.config(state=DISABLED)
        except (NameError, TclError):
            error_window = Toplevel()
            error_window.title('Traceback Error(s)')
            error_window.configure(background="#434547")
            window_height = 400
            window_width = 600
            error_window.geometry(f'{window_width}x{window_height}+{root.geometry().split("+")[1]}+'
                                  f'{root.geometry().split("+")[2]}')
            for e_w in range(4):
                error_window.grid_columnconfigure(e_w, weight=1)
            error_window.grid_rowconfigure(0, weight=1)
            info_scrolled = scrolledtextwidget.ScrolledText(error_window, wrap=WORD)
            info_scrolled.grid(row=0, column=0, columnspan=4, pady=5, padx=5, sticky=E + W + N + S)
            info_scrolled.configure(bg='black', fg='#CFD2D1', bd=8)
            info_scrolled.insert(END, message)
            info_scrolled.see(END)
            info_scrolled.config(state=DISABLED)

            report_error = HoverButton(error_window, text='Report Error',
                                       command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-'
                                                                       'Tool/issues/new?assignees=jlw4049&labels=bug'
                                                                       '&template=bug_report.md&title='),
                                       foreground='white', background='#23272A', borderwidth='3',
                                       activeforeground="#3498db", activebackground="#23272A")
            report_error.grid(row=1, column=3, columnspan=1, padx=10, pady=(5, 4), sticky=S + E + N)

            force_close_root = HoverButton(error_window, text='Force Close Program', command=root.destroy,
                                           foreground='white', background='#23272A', borderwidth='3',
                                           activeforeground="#3498db", activebackground="#23272A")
            force_close_root.grid(row=1, column=0, columnspan=1, padx=10, pady=(5, 4), sticky=S + W + N)

            def right_click_menu_func(x_y_pos):  # Function for mouse button 3 (right click) to pop up menu
                right_click_menu.tk_popup(x_y_pos.x_root, x_y_pos.y_root)  # This gets the position of cursor

            right_click_menu = Menu(info_scrolled, tearoff=False)  # This is the right click menu
            right_click_menu.add_command(label='Copy to clipboard', command=lambda: pyperclip.copy(
                info_scrolled.get(1.0, END).strip()))
            info_scrolled.bind('<Button-3>', right_click_menu_func)  # Uses mouse button 3 to open the menu
            CustomTooltipLabel(info_scrolled, 'Right click to copy', hover_delay=800)  # Hover tip tool-tip
            error_window.grab_set()  # Brings attention to this window until it's closed
            root.bell()  # Error bell sound

    def flush(self):
        pass

    def __exit__(self):  # Class exit function
        sys.stderr = sys.__stderr__  # Redirect stderr back to original stderr
        # self.error_log_file.close()  # Close file


def start_logger():
    if enable_error_logger:  # If True
        sys.stderr = Logger()  # Start the Logger() class to write to console and file


# start logger
threading.Thread(target=start_logger).start()

# variables to be used within the program
source_file_path = StringVar()
source_loaded = StringVar()
source_file_information = {}
encode_file_path = StringVar()
encode_file_resolution = StringVar()
encode_media_info = StringVar()
encode_file_audio = StringVar()
encode_hdr_string = StringVar()
torrent_file_path = StringVar()
nfo_info_var = StringVar()
automatic_workflow_boolean = BooleanVar()
live_boolean = BooleanVar()
anonymous_boolean = BooleanVar()
movie_search_var = StringVar()
movie_search_active = BooleanVar()
tmdb_id_var = StringVar()
imdb_id_var = StringVar()
release_date_var = StringVar()
rating_var = StringVar()
screenshot_comparison_var = StringVar()
screenshot_selected_var = StringVar()
loaded_script_info = StringVar()
script_mode = StringVar()
input_script_path = StringVar()


# function to clear all variables
def clear_all_variables():
    source_file_path.set('')
    source_loaded.set('')
    source_file_information.clear()
    encode_file_path.set('')
    encode_file_resolution.set('')
    encode_media_info.set('')
    encode_file_audio.set('')
    encode_hdr_string.set('')
    torrent_file_path.set('')
    nfo_info_var.set('')
    automatic_workflow_boolean.set(False)
    live_boolean.set(False)
    anonymous_boolean.set(False)
    movie_search_var.set('')
    movie_search_active.set(False)
    tmdb_id_var.set('')
    imdb_id_var.set('')
    release_date_var.set('')
    rating_var.set('')
    screenshot_comparison_var.set('')
    screenshot_selected_var.set('')
    loaded_script_info.set('')
    script_mode.set('')
    input_script_path.set('')


# function to open imdb links with and without the id
def open_imdb_link():
    if imdb_id_var.get() != '':
        webbrowser.open(f'https://imdb.com/title/{imdb_id_var.get()}')
    else:
        webbrowser.open('https://www.imdb.com/')


# function to open tmdb links with and without the id
def open_tmdb_link():
    if tmdb_id_var.get() != '':
        webbrowser.open(f'https://www.themoviedb.org/movie/{tmdb_id_var.get()}')
    else:
        webbrowser.open('https://www.themoviedb.org/movie')


# function to search tmdb for information
def search_movie_global_function(*args):
    # set parser
    movie_window_parser = ConfigParser()
    movie_window_parser.read(config_file)

    # decode imdb img for use with the buttons
    decode_resize_imdb_image = Image.open(BytesIO(base64.b64decode(imdb_icon))).resize((35, 35))
    imdb_img = ImageTk.PhotoImage(decode_resize_imdb_image)

    # decode tmdb img for use with the buttons
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(tmdb_icon))).resize((35, 35))
    tmdb_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    def movie_info_exit_function():
        """movie window exit function"""

        # set stop thread to True
        stop_thread.set()

        # set parser
        exit_movie_window_parser = ConfigParser()
        exit_movie_window_parser.read(config_file)

        # save window position/geometry
        if movie_info_window.wm_state() == 'normal':
            if exit_movie_window_parser['save_window_locations']['movie_info'] != movie_info_window.geometry():
                if int(movie_info_window.geometry().split('x')[0]) >= movie_window_width or \
                        int(movie_info_window.geometry().split('x')[1].split('+')[0]) >= movie_window_height:
                    exit_movie_window_parser.set('save_window_locations', 'movie_info',
                                                 movie_info_window.geometry())
                    with open(config_file, 'w') as root_exit_config_file:
                        exit_movie_window_parser.write(root_exit_config_file)

        # close movie info window
        movie_info_window.destroy()

    def get_imdb_update_filename():
        """function to get imdb title name as well as id's for both imdb and tmdb"""
        # check if imdb id is missing
        if imdb_id_var.get() == "None":
            messagebox.showerror(parent=movie_info_window, title='Missing IMDb ID',
                                 message='Please manually search for the proper IMDb ID and manually '
                                         'add it to the IMDb entry box')
            return  # exit the function

        # if there is an imdb title
        if 't' in imdb_id_var.get():
            imdb_module = Cinemagoer()
            movie = imdb_module.get_movie(str(imdb_id_var.get()).replace('t', ''))
            imdb_movie_name = f"{str(movie['title'])} {str(movie['year'])}"
            source_file_information.update({"imdb_movie_name": imdb_movie_name, "imdb_id": imdb_id_var.get(),
                                            "tmdb_id": tmdb_id_var.get(),
                                            "source_movie_year": f"{str(movie['year'])}"})

        # if user has not selected anything in the window
        elif imdb_id_var.get().strip() == '':
            messagebox.showinfo(parent=movie_info_window, title='Prompt',
                                message='You must select a movie before clicking "Confirm"')
            return  # exit the function

        movie_info_exit_function()  # close movie_info_window

    # movie info window
    movie_info_window = Toplevel()
    movie_info_window.configure(background="#363636")  # Set's the background color
    movie_info_window.title('Movie Selection')  # Toplevel Title
    movie_window_height = 600
    movie_window_width = 1000
    if movie_window_parser['save_window_locations']['movie_info'] == '':
        movie_screen_width = movie_info_window.winfo_screenwidth()
        movie_screen_height = movie_info_window.winfo_screenheight()
        movie_x_coordinate = int((movie_screen_width / 2) - (movie_window_width / 2))
        movie_y_coordinate = int((movie_screen_height / 2) - (movie_window_height / 2))
        movie_info_window.geometry(f"{movie_window_width}x{movie_window_height}+"
                                   f"{movie_x_coordinate}+{movie_y_coordinate}")
    elif movie_window_parser['save_window_locations']['movie_info'] != '':
        movie_info_window.geometry(movie_window_parser['save_window_locations']['movie_info'])
    movie_info_window.grab_set()
    movie_info_window.protocol('WM_DELETE_WINDOW', movie_info_exit_function)

    # Row/Grid configures
    for m_i_w_c in range(6):
        movie_info_window.grid_columnconfigure(m_i_w_c, weight=1)
    for m_i_w_r in range(4):
        movie_info_window.grid_rowconfigure(m_i_w_r, weight=1)
    # Row/Grid configures

    movie_listbox_frame = Frame(movie_info_window)  # Set dynamic listbox frame
    movie_listbox_frame.grid(column=0, columnspan=6, row=0, padx=5, pady=(5, 3), sticky=N + S + E + W)
    movie_listbox_frame.grid_rowconfigure(0, weight=1)
    movie_listbox_frame.grid_columnconfigure(0, weight=1)

    right_scrollbar = Scrollbar(movie_listbox_frame, orient=VERTICAL)  # Scrollbars
    bottom_scrollbar = Scrollbar(movie_listbox_frame, orient=HORIZONTAL)

    # Create listbox
    movie_listbox = Listbox(movie_listbox_frame, xscrollcommand=bottom_scrollbar.set, activestyle="none",
                            yscrollcommand=right_scrollbar.set, bd=2, bg="black", fg="#3498db", height=10,
                            selectbackground='black', selectforeground='lime green', selectmode=SINGLE,
                            font=(set_font, set_font_size + 2))
    movie_listbox.grid(row=0, column=0, columnspan=5, sticky=N + E + S + W)

    # add scrollbars to the listbox
    right_scrollbar.config(command=movie_listbox.yview)
    right_scrollbar.grid(row=0, column=5, sticky=N + W + S)
    bottom_scrollbar.config(command=movie_listbox.xview)
    bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

    # define stop thread event
    stop_thread = threading.Event()

    # define api check function
    def run_api_check():
        if movie_search_active.get():
            return
        movie_search_active.set(True)

        movie_listbox.delete(0, END)
        movie_listbox.insert(END, 'Loading, please wait...')

        collect_title = re.finditer(r'\d{4}', movie_search_var.get().strip())

        title_span = []
        for title_only in collect_title:
            title_span.append(title_only.span())

        try:
            movie_title = str(movie_search_var.get()[0:title_span[-1][0]]).replace('.', ' ').replace(
                '(', '').replace(')', '').strip()
        except IndexError:
            movie_title = str(movie_search_var.get().strip())

        collect_year = re.findall(r'\d{4}', movie_search_var.get().strip())
        if collect_year:
            movie_year = collect_year[-1]
        else:
            movie_year = ''

        try:
            search_movie = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&language"
                                        f"=en-US&page=1&include_adult=false&query={movie_title}&year={movie_year}")
        except requests.exceptions.ConnectionError:
            source_file_information.update({"imdb_movie_name": 'None'})
            messagebox.showerror(parent=movie_info_window, title='Connection Error',
                                 message='There was an error connecting to the internet.\n\n'
                                         'Title name will be determined from source file only')
            movie_info_exit_function()
            return  # exit this function

        movie_dict = {}

        for results in search_movie.json()['results']:
            # find imdb_id data through tmdb
            imdb_id = requests.get(
                f"https://api.themoviedb.org/3/movie/{results['id']}/external_ids?api_key={tmdb_api_key}")
            # if release date string isn't nothing
            if imdb_id.json()['imdb_id'] and results['release_date']:
                # convert release date to standard month/day/year
                release_date = str(results['release_date']).split('-')
                full_release_date = f"{release_date[1]}-{release_date[2]}-{release_date[0]}"
                # update dictionary
                movie_dict.update({f"{results['title']} ({release_date[0]})": {
                    "tvdb_id": f"{results['id']}", "imdb_id": f"{imdb_id.json()['imdb_id']}",
                    "plot": f"{results['overview']}", "vote_average": f"{str(results['vote_average'])}",
                    "full_release_date": full_release_date}})
                # if thread event stop was called
                if stop_thread.is_set():
                    movie_search_active.set(False)  # set active search to false
                    break  # break from loop

        # if stop_thread was called and closed the loop
        if not movie_search_active.get():
            return  # exit function

        # clear movie list box
        movie_listbox.delete(0, END)

        # add all the movies into the listbox
        for key in movie_dict.keys():
            movie_listbox.insert(END, key)

        # function that is run each time a movie is selected to update all the information in the window
        def update_movie_info(event):
            selection = event.widget.curselection()  # get current selection
            # if there is a selection
            if selection:
                movie_listbox_index = selection[0]  # define index of selection
                movie_data = event.widget.get(movie_listbox_index)

                # delete plot text and update it
                plot_scrolled_text.delete("1.0", END)
                plot_scrolled_text.insert(END, movie_dict[movie_data]['plot'])

                # update imdb and tmdb entry box's
                imdb_id_var.set(movie_dict[movie_data]['imdb_id'])
                tmdb_id_var.set(movie_dict[movie_data]['tvdb_id'])

                # update release date label
                release_date_var.set(movie_dict[movie_data]['full_release_date'])

                # update rating label
                rating_var.set(f"{movie_dict[movie_data]['vote_average']} / 10")

        movie_listbox.bind("<<ListboxSelect>>", update_movie_info)  # bind listbox select event to the updater
        movie_search_active.set(False)  # once listbox has been updated, set active to False

    # plot frame
    plot_frame = LabelFrame(movie_info_window, text=' Plot ', labelanchor="nw")
    plot_frame.grid(column=0, row=1, columnspan=6, padx=5, pady=(5, 3), sticky=E + W)
    plot_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 9, 'bold'))
    plot_frame.grid_rowconfigure(0, weight=1)
    plot_frame.grid_columnconfigure(0, weight=1)

    # plot text window
    plot_scrolled_text = scrolledtextwidget.ScrolledText(plot_frame, height=6, wrap=WORD)
    plot_scrolled_text.grid(row=0, column=0, columnspan=6, pady=(0, 5), padx=5, sticky=E + W)
    plot_scrolled_text.config(bg='black', fg='#CFD2D1', bd=2)

    # internal search frame
    internal_search_frame = LabelFrame(movie_info_window, text=' Search ', labelanchor="nw")
    internal_search_frame.grid(column=0, row=2, columnspan=6, padx=5, pady=(5, 3), sticky=E + W)
    internal_search_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 9, 'bold'))
    internal_search_frame.grid_rowconfigure(0, weight=1)
    internal_search_frame.grid_rowconfigure(1, weight=1)
    internal_search_frame.grid_columnconfigure(0, weight=1)

    # movie selection label frame
    movie_selection_lbl_frame = LabelFrame(internal_search_frame, bg="#363636", border=0)
    movie_selection_lbl_frame.grid(column=0, row=0, columnspan=6, sticky=E + W)
    movie_selection_lbl_frame.grid_rowconfigure(0, weight=1)
    movie_selection_lbl_frame.grid_columnconfigure(0, weight=1)
    movie_selection_lbl_frame.grid_columnconfigure(1, weight=100)

    source_input_lbl_ms = Label(movie_selection_lbl_frame,
                                text=f'Source Name:',
                                background='#363636', fg="#3498db", font=(set_font, set_font_size - 1, "bold"))
    source_input_lbl_ms.grid(row=0, column=0, columnspan=1, padx=(5, 0), pady=(5, 3), sticky=W)

    source_input_lbl_ms2 = Label(movie_selection_lbl_frame, wraplength=960,
                                 text=str(pathlib.Path(pathlib.Path(source_file_information["source_path"]).name
                                                       ).with_suffix("")),
                                 background='#363636', fg="white", font=(set_fixed_font, set_font_size - 1))
    source_input_lbl_ms2.grid(row=0, column=1, columnspan=5, padx=(2, 5), pady=(5, 3), sticky=W)

    # internal search box
    search_entry_box2 = Entry(internal_search_frame, borderwidth=4, bg="#565656", fg='white',
                              disabledforeground='white', disabledbackground="#565656",
                              textvariable=movie_search_var)
    search_entry_box2.grid(row=1, column=0, columnspan=5, padx=5, pady=(5, 3), sticky=E + W)
    movie_search_var.set(*args)

    # function to search again
    def start_search_again(*enter_args):
        stop_thread.clear()  # set stop thread to false
        threading.Thread(target=run_api_check).start()

    # bind "Enter" key to run the function
    search_entry_box2.bind("<Return>", start_search_again)

    # internal search button
    search_button2 = HoverButton(internal_search_frame, text="Search", activebackground="#23272A",
                                 command=start_search_again,
                                 foreground="white", background="#23272A",
                                 borderwidth="3", activeforeground="#3498db", width=12)
    search_button2.grid(row=1, column=5, columnspan=1, padx=5, pady=(5, 3), sticky=E + S + N)

    # function to enable and disable the internal search button if a current search is active
    def enable_disable_internal_search_btn():
        try:
            if movie_search_active.get():  # if search is active disable button
                search_button2.config(state=DISABLED)
            else:  # if search is not active enable button
                search_button2.config(state=NORMAL)
        except TclError:
            pass
        movie_info_window.after(50, enable_disable_internal_search_btn)

    # start loop to check internal button
    enable_disable_internal_search_btn()

    # information frame
    information_frame = Frame(movie_info_window, bd=0, bg="#363636")
    information_frame.grid(column=0, row=3, columnspan=7, padx=5, pady=(5, 3), sticky=E + W)
    information_frame.grid_rowconfigure(0, weight=1)
    information_frame.grid_rowconfigure(1, weight=1)
    information_frame.grid_columnconfigure(0, weight=1)
    information_frame.grid_columnconfigure(1, weight=100)
    information_frame.grid_columnconfigure(2, weight=1000)
    information_frame.grid_columnconfigure(3, weight=10000)
    information_frame.grid_columnconfigure(4, weight=100000)
    information_frame.grid_columnconfigure(5, weight=1000000)
    information_frame.grid_columnconfigure(6, weight=1)

    # imdb clickable icon button
    imdb_button2 = Button(information_frame, image=imdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                          activebackground="#363636", command=open_imdb_link)
    imdb_button2.grid(row=0, column=0, columnspan=1, rowspan=2, padx=5, pady=(5, 2), sticky=W)
    imdb_button2.photo = imdb_img

    # imdb entry box internal
    imdb_entry_box2 = Entry(information_frame, borderwidth=4, bg="#565656", fg='white',
                            disabledforeground='white', disabledbackground="#565656", textvariable=imdb_id_var)
    imdb_entry_box2.grid(row=0, column=1, rowspan=2, padx=5, pady=(5, 2), sticky=W)

    # tmdb clickable icon button
    tmdb_button2 = Button(information_frame, image=tmdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                          activebackground="#363636", command=open_tmdb_link)
    tmdb_button2.grid(row=0, column=2, rowspan=2, padx=5, pady=(5, 2), sticky=W)
    tmdb_button2.photo = tmdb_img

    # tmdb internal entry box
    tmdb_entry_box2 = Entry(information_frame, borderwidth=4, bg="#565656", fg='white',
                            disabledforeground='white', disabledbackground="#565656", textvariable=tmdb_id_var)
    tmdb_entry_box2.grid(row=0, column=3, rowspan=2, padx=5, pady=(5, 2), sticky=W)

    # release date labels
    release_date_label = Label(information_frame, text='Release Date:', background='#363636', fg="#3498db",
                               font=(set_font, set_font_size + 1, "bold"))
    release_date_label.grid(row=0, column=4, sticky=W, padx=(5, 0), pady=(5, 2))

    release_date_label2 = Label(information_frame, textvariable=release_date_var, width=10,
                                background='#363636', fg="#3498db", font=(set_font, set_font_size))
    release_date_label2.grid(row=0, column=5, sticky=W, padx=(1, 5), pady=(5, 2))

    # rating labels
    rating_label = Label(information_frame, text='           Rating:', background='#363636', fg="#3498db",
                         font=(set_font, set_font_size + 1, "bold"))
    rating_label.grid(row=1, column=4, sticky=W, padx=(5, 0), pady=(5, 2))

    rating_label2 = Label(information_frame, textvariable=rating_var, width=10,
                          background='#363636', fg="#3498db", font=(set_font, set_font_size))
    rating_label2.grid(row=1, column=5, sticky=W, padx=(1, 5), pady=(5, 2))

    # confirm movie button
    confirm_movie_btn = HoverButton(information_frame, text="Confirm", command=get_imdb_update_filename,
                                    foreground="white", background="#23272A", borderwidth="3", width=10,
                                    activeforeground="#3498db", activebackground="#23272A")
    confirm_movie_btn.grid(row=1, column=6, padx=5, pady=(5, 2), sticky=E)

    movie_info_window.focus_set()  # focus's id window
    stop_thread.clear()  # set stop thread event to false
    threading.Thread(target=run_api_check).start()  # start thread to search for movie title
    movie_info_window.wait_window()  # wait for window to close


def source_input_function(*args):
    # define parser
    source_input_parser = ConfigParser()
    source_input_parser.read(config_file)

    # update last used folder
    source_input_parser.set('last_used_folder', 'path', str(pathlib.Path(*args).parent))
    with open(config_file, 'w') as s_i_c_config:
        source_input_parser.write(s_i_c_config)

    # check if script is the correct script
    if str(pathlib.Path(pathlib.Path(*args).name).with_suffix('')).endswith('_source'):
        messagebox.showinfo(parent=root, title='Wrong script file',
                            message='You must select the script without the suffix "_source" '
                                    'in the filename before the scripts extension')
        return  # exit this function

    # clear variables and boxes
    image_listbox.config(state=NORMAL)  # enable image list box
    image_listbox.delete(0, END)  # delete image list box contents
    image_listbox.config(state=DISABLED)  # disable image list box
    screenshot_scrolledtext.delete("1.0", END)  # clear contents of url notebook tab
    tabs.select(image_tab)  # select first tab in the image box
    delete_encode_entry()  # clear encode entry
    source_file_information.clear()  # clear dictionary
    delete_source_entry()  # clear source entry
    audio_pop_up_var = StringVar()  # audio pop up var

    # check if script is avisynth
    if pathlib.Path(*args).suffix == '.avs':
        script_mode.set('avs')
    # check if script is vapoursynth
    elif pathlib.Path(*args).suffix == '.vpy':
        script_mode.set('vpy')
    # if input is not a script
    else:
        messagebox.showerror(parent=root, title='Incorrect File',
                             message='Dropped file must be an AviSynth or VapourSynth script')
        return  # exit the function

    # assign path to script file for later use
    input_script_path.set(*args)

    # open avisynth script
    if script_mode.get() == 'avs':
        with open(*args, 'rt') as encode_script:
            # search file for info
            search_file = encode_script.read()
            get_source_file = re.search(r'FFVideoSource\("(.+?)",', search_file)
            get_crop = re.search(r"Crop\((.+)\)", search_file)
            get_resize = re.search(r"Spline\d\d.*\((.+)\)", search_file)

            # load search file to global string var to be used by encode function
            loaded_script_info.set(search_file)

    # open vapoursynth script
    elif script_mode.get() == 'vpy':
        with open(*args, 'rt') as encode_script:
            # search file for info
            search_file = encode_script.read()
            get_source_file = re.search(r'else core\.ffms2\.Source\(r"(.+?)",', search_file)
            get_crop = re.search(r"Crop\(clip,\s(.+)\)", search_file)
            get_resize = re.search(r"Spline\d\d\(clip,\s(.+)\)", search_file)

            # load search file to global string var to be used by encode function
            loaded_script_info.set(search_file)

    # if we cannot locate the source file
    if not get_source_file or not pathlib.Path(get_source_file.group(1)).is_file():
        find_source = messagebox.askyesno(parent=root, title='Missing Source',
                                          message='Cannot locate source file. Would you like to manually find this?')
        if find_source:
            # check if last used folder exists
            if pathlib.Path(source_input_parser['last_used_folder']['path']).is_dir():
                s_i_f_initial_dir = pathlib.Path(source_input_parser['last_used_folder']['path'])
            else:
                s_i_f_initial_dir = '/'

            # open prompt to navigate to file
            source_file_input = filedialog.askopenfilename(parent=root, title='Select Source File',
                                                           initialdir=s_i_f_initial_dir,
                                                           filetypes=[("Media Files", "*.*")])
            if source_file_input:
                loaded_source_file = source_file_input

        # if user does not want to find the source exit the function
        elif not find_source:
            return  # exit the function

    # if we find the source file
    else:
        loaded_source_file = get_source_file.group(1)

    try:
        media_info = MediaInfo.parse(pathlib.Path(loaded_source_file))
    except UnboundLocalError:
        return  # exit the function

    # check to ensure file dropped has a video track
    if not media_info.general_tracks[0].count_of_video_streams:
        messagebox.showerror(parent=root, title='Error', message='Incorrect file format or missing video stream')
        return  # exit the function

    # set video track
    video_track = media_info.video_tracks[0]

    # set general track
    general_track = media_info.general_tracks[0]

    # calculate average video bitrate
    if video_track.stream_size and video_track.duration:
        calculate_average_video_bitrate = round((float(video_track.stream_size) / 1000) /
                                                ((float(video_track.duration) / 60000) * 0.0075) / 1000)

    # if one of the above metrics is missing attempt to calculate it roughly with the general track info
    elif general_track.file_size and general_track.duration:
        calculate_average_video_bitrate = round((float(general_track.file_size) / 1000) /
                                                ((float(general_track.duration) / 60000) * 0.0075) / 1000 * 0.88)

    # if for some reason neither can produce the bitrate
    else:
        calculate_average_video_bitrate = 'N/A'

    # get stream size
    if video_track.other_stream_size:
        v_stream_size = video_track.other_stream_size[3]
    # if video track is missing the above metrics get it from general
    elif general_track.other_file_size[3]:
        v_stream_size = general_track.other_file_size[3]
    # if for some reason general and video are missing the metrics just print it as N/A
    else:
        v_stream_size = 'N/A'

    # update source labels
    update_source_label = f"Avg BR:  {str(calculate_average_video_bitrate)} kbps  |  " \
                          f"Res:  {str(video_track.width)}x{str(video_track.height)}  |  " \
                          f"FPS:  {str(video_track.frame_rate)}  |  " \
                          f"Size:  {str(v_stream_size)}"
    hdr_string = ''
    if video_track.other_hdr_format:
        hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
    elif not video_track.other_hdr_format:
        hdr_string = ''

    # if source has 0 audio streams (this should never happen)
    if not media_info.general_tracks[0].count_of_audio_streams:
        messagebox.showerror(parent=root, title='Error', message='Source has no audio track')
        return

    # if source file only has 2 or more tracks
    if int(media_info.general_tracks[0].count_of_audio_streams) >= 2:
        audio_track_win = Toplevel()  # Toplevel window
        audio_track_win.configure(background='#363636')  # Set color of audio_track_win background
        audio_track_win.title('Audio Track Selection')
        # Open on top left of root window
        audio_track_win.geometry(f'{480}x{160}+{str(int(root.geometry().split("+")[1]) + 108)}+'
                                 f'{str(int(root.geometry().split("+")[2]) + 80)}')
        audio_track_win.resizable(False, False)  # makes window not resizable
        audio_track_win.grab_set()  # forces audio_track_win to stay on top of root
        audio_track_win.wm_overrideredirect(True)
        root.wm_attributes('-alpha', 0.92)  # set main gui to be slightly transparent
        audio_track_win.grid_rowconfigure(0, weight=1)
        audio_track_win.grid_columnconfigure(0, weight=1)

        track_frame = Frame(audio_track_win, highlightbackground="white", highlightthickness=2, bg="#363636",
                            highlightcolor='white')
        track_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        for e_n_f in range(3):
            track_frame.grid_columnconfigure(e_n_f, weight=1)
            track_frame.grid_rowconfigure(e_n_f, weight=1)

        # create label
        track_selection_label = Label(track_frame, text='Select audio source that down-mix was encoded from:',
                                      background='#363636', fg="#3498db", font=(set_font, set_font_size, "bold"))
        track_selection_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

        # create drop down menu set
        audio_stream_track_counter = {}
        for i in range(int(media_info.general_tracks[0].count_of_audio_streams)):
            audio_stream_track_counter[f'Track #{i + 1}  |  {stream_menu(loaded_source_file)[i]}'] = i

        audio_pop_up_var.set(next(iter(audio_stream_track_counter)))  # set the default option
        audio_pop_up_menu = OptionMenu(track_frame, audio_pop_up_var, *audio_stream_track_counter.keys())
        audio_pop_up_menu.config(background="#23272A", foreground="white", highlightthickness=1,
                                 width=48, anchor='w', activebackground="#23272A", activeforeground="#3498db")
        audio_pop_up_menu.grid(row=1, column=0, columnspan=3, padx=10, pady=6, sticky=N + W + E)
        audio_pop_up_menu["menu"].configure(background="#23272A", foreground="white", activebackground="#23272A",
                                            activeforeground="#3498db")

        # create 'OK' button
        def audio_ok_button_function():
            audio_pop_up_var.set(audio_stream_track_counter[audio_pop_up_var.get()])
            root.wm_attributes('-alpha', 1.0)  # restore transparency
            audio_track_win.destroy()

        audio_track_okay_btn = HoverButton(track_frame, text="OK", command=audio_ok_button_function, foreground="white",
                                           background="#23272A", borderwidth="3", width=8, activeforeground="#3498db",
                                           activebackground="#23272A")
        audio_track_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)
        audio_track_win.wait_window()

    # if source file only has 1 audio track
    elif int(media_info.general_tracks[0].count_of_audio_streams) == 1:
        audio_pop_up_var.set('0')

    # set source variables
    source_loaded.set('loaded')  # set string var to loaded

    # update dictionary
    # source input path
    source_file_information.update({"source_path": str(pathlib.Path(loaded_source_file))})

    # selected source audio track info
    source_file_information.update(
        {"source_selected_audio_info": media_info.audio_tracks[int(audio_pop_up_var.get())].to_data()})

    # audio track selection
    source_file_information.update({"audio_track": audio_pop_up_var.get()})

    # resolution
    source_file_information.update({"resolution": f"{str(video_track.width)}x{str(video_track.height)}"})

    # crop
    if get_crop:
        # convert crop for VapourSynth
        if script_mode.get() == "vpy":
            get_left = get_crop.group(1).split(',')[0].strip()
            get_right = get_crop.group(1).split(',')[1].strip()
            get_top = get_crop.group(1).split(',')[2].strip()
            get_bottom = get_crop.group(1).split(',')[3].strip()
        # convert crop for AviSynth
        elif script_mode.get() == 'avs':
            get_left = get_crop.group(1).split(',')[0].replace('-', '').strip()
            get_right = get_crop.group(1).split(',')[2].replace('-', '').strip()
            get_top = get_crop.group(1).split(',')[1].replace('-', '').strip()
            get_bottom = get_crop.group(1).split(',')[3].replace('-', '').strip()

        # add converted crop info to dictionary
        source_file_information.update({"crop": {"left": get_left, "right": get_right,
                                                 "top": get_top, "bottom": get_bottom}})
    # if crop is None
    if not get_crop:
        source_file_information.update({"crop": "None"})

    # resize
    if get_resize:
        source_file_information.update({"resize": f"{str(get_resize.group(1))}"})
    else:
        source_file_information.update({"resize": "None"})

    # hdr
    if hdr_string != '':
        source_file_information.update({'hdr': 'True'})
    else:
        source_file_information.update({'hdr': 'False'})

    # video format
    if video_track.format:
        source_file_information.update({'format': f"{str(video_track.format)}"})

    # get source input title name only
    # find all 4-digit numbers
    source_movie_name = re.finditer(r'\d{4}(?!p)', str(pathlib.Path(loaded_source_file).name), re.IGNORECASE)

    # create empty list and add all numbers to the list
    movie_name_extraction = []
    for digit_matches in source_movie_name:
        movie_name_extraction.append(digit_matches.span())

    # attempt to get only the title and year
    try:
        source_name = str(pathlib.Path(loaded_source_file).name)[0:int(movie_name_extraction[-1][-1])].replace(
            '.', ' ').replace('(', '').replace(')', '')
    # if the file name is already in the correct format set it to this
    except IndexError:
        source_name = str(pathlib.Path(loaded_source_file).name).replace(
            '.', ' ').replace('(', '').replace(')', '').replace(':', '').strip()

    # use imdb to check to double-check detected title
    root.withdraw()  # hide root window
    search_movie_global_function(source_name)  # run movie search function
    advanced_root_deiconify()  # re-open root window

    # edition check
    edition_testing = re.search('collector.*edition|director.*cut|extended.*cut|limited.*edition|'
                                'special.*edition|theatrical.*cut|uncut|unrated', loaded_source_file, re.IGNORECASE)
    # if edition is detected add it to the name
    if edition_testing:
        extracted_edition = f" {edition_testing.group()}"
    else:
        extracted_edition = ''

    # add 'UHD' to filename if it's 2160p
    source_file_width = video_track.width
    if int(source_file_width) <= 1920:
        uhd_string = ''
    elif int(source_file_width) <= 3840:
        uhd_string = 'UHD'

    # add full final name and year to the dictionary
    try:
        if source_file_information['imdb_movie_name'] != 'None':
            source_file_information.update({'source_file_name': f"{source_file_information['imdb_movie_name']}"
                                                                f"{uhd_string}{extracted_edition} BluRay"})
        # if there was a connection error key 'imdb_movie_name' will be 'None', get title name manually
        elif source_file_information['imdb_movie_name'] == 'None':
            source_file_information.update({'source_file_name': f"{source_name}{uhd_string}"
                                                                f"{extracted_edition} BluRay"})
    except KeyError:
        return  # exit this function

    # update labels
    source_label.config(text=update_source_label)
    source_hdr_label.config(text=hdr_string)
    source_file_path.set(str(pathlib.Path(loaded_source_file)))

    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.insert(END, pathlib.Path(loaded_source_file).name)
    source_entry_box.config(state=DISABLED)

    # return function
    return loaded_source_file


def encode_input_function(*args):
    # define parser
    encode_input_function_parser = ConfigParser()
    encode_input_function_parser.read(config_file)

    # check if source is loaded
    if source_loaded.get() == '':
        messagebox.showinfo(parent=root, title='Info', message='You must open a source file first')
        return  # exit function

    # code to check input extension
    if pathlib.Path(*args).suffix != '.mp4':
        messagebox.showerror(parent=root, title='Incorrect container',
                             message=f'Incorrect container/extension "{pathlib.Path(*args).suffix}":\n\n'
                                     f'BHDStudio encodes are muxed into MP4 containers and should have a '
                                     f'".mp4" extension')
        delete_encode_entry()
        return  # exit function

    # if file has the correct extension type parse it
    media_info = MediaInfo.parse(pathlib.Path(*args))

    # function to generate generic errors
    def encode_input_error_box(media_info_count, track_type, error_string):
        error_message = f'"{pathlib.Path(*args).stem}":\n\nHas {media_info_count} {track_type} track' \
                        f'(s)\n\n{error_string}'
        messagebox.showerror(parent=root, title='Incorrect Format', message=error_message)
        delete_encode_entry()

    # video checks ----------------------------------------------------------------------------------------------------
    # if encode is missing the video track
    if not media_info.general_tracks[0].count_of_video_streams:
        encode_input_error_box('0', 'video', 'BHDStudio encodes should have 1 video track')
        return  # exit function

    # if encode has more than 1 video track
    if int(media_info.general_tracks[0].count_of_video_streams) > 1:
        encode_input_error_box(media_info.general_tracks[0].count_of_video_streams, 'video',
                               'BHDStudio encodes should only have 1 video track')
        return  # exit function

    # select video track for parsing
    video_track = media_info.video_tracks[0]

    # calculate average video bit rate for encode
    # calculate_average_video_bit_rate = round((float(video_track.stream_size) / 1000) /
    #                                          ((float(video_track.duration) / 60000) * 0.0075) / 1000)

    # check for un-even crops
    width_value = int(str(source_file_information.get('resolution')).split('x')[0]) - int(video_track.width)
    height_value = int(str(source_file_information.get('resolution')).split('x')[1]) - int(video_track.height)
    if (int(width_value) % 2) != 0 or (int(height_value) % 2) != 0:
        messagebox.showerror(parent=root, title='Crop Error',
                             message=f'Resolution: "{str(video_track.width)}x{str(video_track.height)}"\n\n'
                                     f'BHDStudio encodes should only be cropped in even numbers')
        delete_encode_entry()
        return  # exit function

    # error function for resolution check and miss match bit rates
    def resolution_bit_rate_miss_match_error(res_error_string):
        messagebox.showerror(parent=root, title='Resolution/Bit rate Miss Match', message=res_error_string)
        delete_encode_entry()

    # detect resolution and check miss match bit rates
    encode_settings_used_bit_rate = int(str(video_track.encoding_settings).split('bitrate=')[1].split('/')[0].strip())
    if video_track.width <= 1280:  # 720p
        encoded_source_resolution = '720p'
        if encode_settings_used_bit_rate != 4000:
            resolution_bit_rate_miss_match_error(f'Input bit rate: {str(encode_settings_used_bit_rate)} kbps\n\n'
                                                 f'Bit rate for 720p encodes should be 4000 kbps')
            return  # exit function
    elif video_track.width <= 1920:  # 1080p
        encoded_source_resolution = '1080p'
        if encode_settings_used_bit_rate != 8000:
            resolution_bit_rate_miss_match_error(f'Input bit rate: {str(encode_settings_used_bit_rate)} kbps\n\n'
                                                 f'Bit rate for 1080p encodes should be 8000 kbps')
            return  # exit function
        if source_file_information['resize'] != 'None':
            messagebox.showinfo(parent=root, title='Incorrect resolution',
                                message='Source script indicates that the encode file was resized.\n\nYou must either '
                                        'open a 720p encode or open a new source script')
            return  # exit function
    elif video_track.width <= 3840:  # 2160p
        encoded_source_resolution = '2160p'
        if encode_settings_used_bit_rate != 16000:
            resolution_bit_rate_miss_match_error(f'Input bit rate: {str(encode_settings_used_bit_rate)} kbps\n\n'
                                                 f'Bit rate for 2160p encodes should be 16000 kbps')
            return  # exit function
        if source_file_information['resize'] != 'None':
            messagebox.showinfo(parent=root, title='Incorrect resolution',
                                message='Source script indicates that the encode file was resized.\n\nYou must either '
                                        'open a 720p encode or open a new source script')
            return  # exit function

    # set encode file resolution string var
    encode_file_resolution.set(encoded_source_resolution)

    # check for source resolution vs encode resolution (do not allow 2160p encode on a 1080p source)
    source_width = str(source_file_information['resolution']).split('x')[0]
    if int(source_width) <= 1920:  # 1080p
        source_resolution = '1080p'
        allowed_encode_resolutions = ['720p', '1080p']
    elif int(source_width) <= 3840:  # 2160p
        source_resolution = '2160p'
        allowed_encode_resolutions = ['2160p']
    if encoded_source_resolution not in allowed_encode_resolutions:
        messagebox.showerror(parent=root, title='Error',
                             message=f'Source resolution {source_resolution}:\n'
                                     f'Encode resolution {encoded_source_resolution}\n\n'
                                     f'Allowed encode resolutions based on source:\n'
                                     f'"{", ".join(allowed_encode_resolutions)}"')
        return  # exit function

    # audio checks ----------------------------------------------------------------------------------------------------
    # if encode is missing the audio track
    if not media_info.general_tracks[0].count_of_audio_streams:
        encode_input_error_box('0', 'audio', 'BHDStudio encodes should have 1 audio track')
        return  # exit function

    # if encode has more than 1 audio track
    if int(media_info.general_tracks[0].count_of_audio_streams) > 1:
        encode_input_error_box(media_info.general_tracks[0].count_of_audio_streams, 'audio',
                               'BHDStudio encodes should only have 1 audio track')
        return  # exit function

    # select audio track #1
    audio_track = media_info.audio_tracks[0]

    # check audio track format
    if str(audio_track.format) != 'AC-3':
        messagebox.showerror(parent=root, title='Error',
                             message=f'Audio format "{str(audio_track.format)}" '
                                     f'is not correct.\n\nBHDStudio encodes should be in "Dolby Digital (AC-3)" only')
        return  # exit function

    # check if audio channels was properly encoded from source
    source_audio_channels = int(source_file_information["source_selected_audio_info"]["channel_s"])
    # 720p check, define accepted bhd audio channels
    if encoded_source_resolution == '720p':
        if source_audio_channels == 1:
            bhd_accepted_audio_channels = 1
        elif source_audio_channels >= 2:
            bhd_accepted_audio_channels = 2

    # 1080p/2160p check, define accepted bhd audio channels
    elif encoded_source_resolution == '1080p' or encoded_source_resolution == '2160p':
        if source_audio_channels == 1:
            bhd_accepted_audio_channels = 1
        elif source_audio_channels in (2, 3, 4, 5):
            bhd_accepted_audio_channels = 2
        elif source_audio_channels in (6, 7, 8):
            bhd_accepted_audio_channels = 6

    # compare encoded audio channels against BHD accepted audio channels, if they are not the same prompt an error
    if int(audio_track.channel_s) != bhd_accepted_audio_channels:
        # generate cleaner audio strings for source
        if source_audio_channels == 1:
            source_audio_string = '1.0'
        elif source_audio_channels == 2:
            source_audio_string = '2.0'
        elif source_audio_channels == 3:
            source_audio_string = '2.1'
        elif source_audio_channels == 6:
            source_audio_string = '5.1'
        elif source_audio_channels == 7:
            source_audio_string = '6.1'
        elif source_audio_channels == 8:
            source_audio_string = '7.1'
        else:
            source_audio_string = str(source_audio_channels)

        # generate cleaner audio strings for encode
        if bhd_accepted_audio_channels == 1:
            encode_audio_string = '1.0'
        elif bhd_accepted_audio_channels == 2:
            encode_audio_string = '2.0 (dplII)'
        elif bhd_accepted_audio_channels == 6:
            encode_audio_string = '5.1'
        messagebox.showerror(parent=root, title='Error',
                             message=f'Source audio is {source_audio_string}\n\n'
                                     f'{encoded_source_resolution} BHDStudio audio should be Dolby Digital '
                                     f'{encode_audio_string}')
        return  # exit function

    # update audio channel string var for use with the uploader
    if bhd_accepted_audio_channels == 1:
        encode_file_audio.set('DD1.0')
    elif bhd_accepted_audio_channels == 2:
        encode_file_audio.set('DD2.0')
    elif bhd_accepted_audio_channels == 6:
        encode_file_audio.set('DD5.1')

    # audio channel string conversion and error check
    if audio_track.channel_s == 1:
        audio_channels_string = '1.0'
    elif audio_track.channel_s == 2:
        audio_channels_string = '2.0'
    elif audio_track.channel_s == 6:
        audio_channels_string = '5.1'
    else:
        messagebox.showerror(parent=root, title='Incorrect Format',
                             message=f'Incorrect audio channel format {str(audio_track.channel_s)}:\n\nBHDStudio '
                                     f'encodes audio channels should be 1.0, 2.0 (dplII), or 5.1')
        delete_encode_entry()
        return  # exit function

    calculate_average_video_bitrate = round((float(video_track.stream_size) / 1000) /
                                            ((float(video_track.duration) / 60000) * 0.0075) / 1000)

    update_source_label = f"Avg BR:  {str(calculate_average_video_bitrate)} kbps  |  " \
                          f"Res:  {str(video_track.width)}x{str(video_track.height)}  |  " \
                          f"FPS:  {str(video_track.frame_rate)}  |  " \
                          f"Audio:  {str(audio_track.format)} / {audio_channels_string} / " \
                          f"{str(audio_track.other_bit_rate[0]).replace('kb/s', '').strip().replace(' ', '')} kbps"
    hdr_string = ''
    if video_track.other_hdr_format:
        hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
        if 'hdr10' in hdr_string.lower():
            encode_hdr_string.set('HDR')
    elif not video_track.other_hdr_format:
        hdr_string = ''
        encode_hdr_string.set('')

    release_notes_scrolled.config(state=NORMAL)
    release_notes_scrolled.delete('1.0', END)
    release_notes_scrolled.insert(END, '-Optimized for PLEX, emby, Jellyfin, and other streaming platforms')
    if audio_channels_string == '1.0':
        release_notes_scrolled.insert(END, '\n-Downmixed Lossless audio track to Dolby Digital 1.0')
    elif audio_channels_string == '2.0':
        release_notes_scrolled.insert(END, '\n-Downmixed Lossless audio track to Dolby Pro Logic II 2.0')
    elif audio_channels_string == '5.1':
        release_notes_scrolled.insert(END, '\n-Downmixed Lossless audio track to Dolby Digital 5.1')
    if 'HDR10+' in str(video_track.hdr_format_compatibility):
        release_notes_scrolled.insert(END, '\n-HDR10+ compatible')
        release_notes_scrolled.insert(END, '\n-Screenshots tone mapped for comparison')
    elif 'HDR10' in str(video_track.hdr_format_compatibility):
        release_notes_scrolled.insert(END, '\n-HDR10 compatible')
        release_notes_scrolled.insert(END, '\n-Screenshots tone mapped for comparison')
    release_notes_scrolled.config(state=DISABLED)

    # update release notes automatically
    # clear all check buttons
    enable_clear_all_checkbuttons()

    # create empty list
    script_info_list = []

    # search each line of the opened file in memory
    for each_line in loaded_script_info.get().splitlines():
        # remove any commented lines
        if not each_line.startswith('#'):
            # remove all ending newlines and ignore empty strings
            if each_line.rstrip() != '':
                # append the remaining data to a list to be parsed
                script_info_list.append(each_line.rstrip())

    # parse list to update release notes for vapoursynth scripts
    if script_mode.get() == 'vpy':
        # find fill border info
        for info in script_info_list:
            fill_border_info = re.search(r"fillborders\((.+)\)", info, re.IGNORECASE)
            if fill_border_info:
                get_digits = re.findall(r"\d+", fill_border_info.group(1))[:-1]
                check_if_all_zero = any(int(i) != 0 for i in get_digits)
                # if any numbers are not equal to 0 (meaning fill borders was actually used)
                if check_if_all_zero:
                    # set fill borders var to 'on' and run fill border update function
                    fill_borders_var.set('on')
                    update_fill_borders()
                # break from loop
                break

        # check for hard coded subs
        hard_code_subs = re.search(r"textsubmod", str(script_info_list), re.IGNORECASE)
        # if hard code subs are found update forced sub var
        if hard_code_subs:
            forced_subtitles_burned_var.set('on')
            update_forced_var()

        # check for balance borders
        for info in script_info_list:
            balance_border_info = re.search(r"bbmod\((.+)\)", info, re.IGNORECASE)
            if balance_border_info:
                bb_digits = re.findall(r"\d+", balance_border_info.group(1))[:-2]
                bb_all_zero = any(int(i) != 0 for i in bb_digits)
                # if any numbers are not equal to 0 (meaning balance borders was actually used)
                if bb_all_zero:
                    # set balance borders to 'on' and run the update function
                    balance_borders_var.set('on')
                    update_balanced_borders()
                # break from the loop
                break

    # parse list to update release notes for avisynth scripts
    elif script_mode.get() == 'avs':
        # find fill border info
        for info in script_info_list:
            fill_border_info = re.search(r"fill.+\(([\s\d,]*)\)", info, re.IGNORECASE)
            if fill_border_info:
                get_digits = re.findall(r"\d+", fill_border_info.group(1))
                check_if_all_zero = any(int(i) != 0 for i in get_digits)
                # if any numbers are not equal to 0 (meaning fill borders was actually used)
                if check_if_all_zero:
                    # set fill borders var to 'on' and run fill border update function
                    fill_borders_var.set('on')
                    update_fill_borders()
                # break from loop
                break

        # check for hard coded subs
        hard_code_subs = re.search(r"textsub", str(script_info_list), re.IGNORECASE)
        # if hard code subs are found update forced sub var
        if hard_code_subs:
            forced_subtitles_burned_var.set('on')
            update_forced_var()

        # check for balance borders
        for info in script_info_list:
            balance_border_info = re.search(r"balanceborders\((.+)\)", info, re.IGNORECASE)
            if balance_border_info:
                bb_digits = re.findall(r"\d+", balance_border_info.group(1))[:-2]
                bb_all_zero = any(int(i) != 0 for i in bb_digits)
                # if any numbers are not equal to 0 (meaning balance borders was actually used)
                if bb_all_zero:
                    # set balance borders to 'on' and run the update function
                    balance_borders_var.set('on')
                    update_balanced_borders()
                # break from the loop
                break

    # set torrent name
    if encode_input_function_parser['torrent_settings']['default_path'] != '':
        torrent_file_path.set(str(pathlib.Path(encode_input_function_parser['torrent_settings']['default_path']) /
                                  pathlib.Path(pathlib.Path(*args).name).with_suffix('.torrent')))
    else:
        torrent_file_path.set(str(pathlib.Path(*args).with_suffix('.torrent')))

    # set media info memory file
    media_info_original = MediaInfo.parse(pathlib.Path(*args), full=False, output="")  # parse identical to mediainfo
    encode_media_info.set(media_info_original)

    # update labels
    encode_label.config(text=update_source_label)
    encode_hdr_label.config(text=hdr_string)
    encode_file_path.set(str(pathlib.Path(*args)))
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.insert(END, pathlib.Path(*args).name)
    encode_entry_box.config(state=DISABLED)

    # ensure encode file is named correctly to BHDStudio standards based off of source file input
    if encode_hdr_string.get() != '':
        enc_dropped_hdr = ' HDR'
    else:
        enc_dropped_hdr = ''

    suggested_bhd_filename = f"{source_file_information['source_file_name']} {encoded_source_resolution} " \
                             f"{str(encode_file_audio.get()).replace('DD', 'DD.')}{enc_dropped_hdr} " \
                             f"{video_track.encoded_library_name}-BHDStudio" \
                             f"{str(pathlib.Path(*args).suffix)}".replace(' ', '.')

    source_file_information.update({"suggested_bhd_title": suggested_bhd_filename.replace('DD.', 'DD')})

    if str(pathlib.Path(*args).name) != suggested_bhd_filename:
        # rename encode window
        rename_encode_window = Toplevel()
        rename_encode_window.title('Confirm Filename')
        rename_encode_window.configure(background="#363636")
        rename_encode_window.geometry(f'{600}x{300}+{str(int(root.geometry().split("+")[1]) + 60)}+'
                                      f'{str(int(root.geometry().split("+")[2]) + 230)}')
        rename_encode_window.resizable(False, False)
        rename_encode_window.grab_set()
        rename_encode_window.protocol('WM_DELETE_WINDOW', lambda: rename_file_func())
        root.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
        rename_encode_window.grid_rowconfigure(0, weight=1)
        rename_encode_window.grid_columnconfigure(0, weight=1)

        # rename encode frame
        rename_enc_frame = Frame(rename_encode_window, highlightbackground="white", highlightthickness=2, bg="#363636",
                                 highlightcolor='white')
        rename_enc_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        for col_e_f in range(3):
            rename_enc_frame.grid_columnconfigure(col_e_f, weight=1)
        for row_e_f in range(7):
            rename_enc_frame.grid_rowconfigure(row_e_f, weight=1)

        # create label
        rename_info_lbl = Label(rename_enc_frame, text=f'Source Name:',
                                background='#363636', fg="#3498db", font=(set_font, set_font_size, "bold"))
        rename_info_lbl.grid(row=0, column=0, columnspan=3, sticky=W + S + E, padx=5, pady=(2, 0))

        # create label
        rename_info_lbl1 = Label(rename_enc_frame, wraplength=598,
                                 text=str(pathlib.Path(source_file_information["source_path"]).name),
                                 background='#363636', fg="white", font=(set_fixed_font, set_font_size))
        rename_info_lbl1.grid(row=1, column=0, columnspan=3, sticky=W + N + E, padx=5, pady=(2, 0))

        # create label
        rename_info_lbl2 = Label(rename_enc_frame, text='Encode Name:',
                                 background='#363636', fg="#3498db", font=(set_font, set_font_size, "bold"))
        rename_info_lbl2.grid(row=2, column=0, columnspan=3, sticky=W + S + E, padx=5, pady=(2, 0))

        # create label
        rename_info_lbl2 = Label(rename_enc_frame, wraplength=598, text=str(pathlib.Path(*args).name),
                                 background='#363636', fg="white", font=(set_fixed_font, set_font_size))
        rename_info_lbl2.grid(row=3, column=0, columnspan=3, sticky=W + N + E, padx=5, pady=(2, 0))

        # create label
        rename_info_lbl3 = Label(rename_enc_frame, text='Suggested Name:',
                                 background='#363636', fg="#3498db", font=(set_font, set_font_size, "bold"))
        rename_info_lbl3.grid(row=4, column=0, sticky=W + S, padx=5, pady=(2, 0))

        # create entry box
        custom_entry_box = Entry(rename_enc_frame, borderwidth=4, bg="#565656", fg='white')
        custom_entry_box.grid(row=5, column=0, columnspan=3, padx=10, pady=(0, 5), sticky=E + W + N)
        custom_entry_box.insert(END, str(suggested_bhd_filename))

        def rename_file_func():
            """Rename encode input to the correct name"""
            if not custom_entry_box.get().strip().endswith('.mp4'):
                messagebox.showerror(parent=rename_encode_window, title='Missing Suffix',
                                     message='Filename must have ".mp4" suffix!\n\ne.g. "MovieName.mp4"')
                return  # exit function

            # rename the file
            try:
                renamed_enc = pathlib.Path(*args).rename(pathlib.Path(*args).parent / custom_entry_box.get().strip())
            # if file exists delete old file and rename
            except FileExistsError:
                pathlib.Path(pathlib.Path(*args).parent / custom_entry_box.get().strip()).unlink(missing_ok=True)
                renamed_enc = pathlib.Path(*args).rename(pathlib.Path(*args).parent / custom_entry_box.get().strip())

            root.wm_attributes('-alpha', 1.0)  # restore transparency
            rename_encode_window.destroy()  # close window
            encode_input_function(pathlib.Path(renamed_enc))  # re-run encode input with the renamed file
            encode_file_path.set(renamed_enc)  # update global variable

        # create 'Rename' button
        rename_okay_btn = HoverButton(rename_enc_frame, text="Rename", command=rename_file_func, foreground="white",
                                      background="#23272A", borderwidth="3", activeforeground="#3498db", width=8,
                                      activebackground="#23272A")
        rename_okay_btn.grid(row=6, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

        # create 'Cancel' button
        rename_cancel_btn = HoverButton(rename_enc_frame, text="Cancel", activeforeground="#3498db", width=8,
                                        command=lambda: [rename_encode_window.destroy(),
                                                         root.wm_attributes('-alpha', 1.0), reset_gui()],
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activebackground="#23272A")
        rename_cancel_btn.grid(row=6, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

        rename_encode_window.wait_window()  # wait for window to be closed


def drop_function(event):
    file_input = [x for x in root.splitlist(event.data)][0]

    # directory is dropped run the staxrip function
    if pathlib.Path(file_input).is_dir():
        staxrip_working_directory(file_input)

    # if a file is dropped run the manual function
    elif pathlib.Path(file_input).is_file():
        widget_source = str(event.widget.cget('text')).strip()
        # if widget is in source frame run source input function
        if 'source' in widget_source.lower():
            source_input_function(file_input)
        # if the widget is in encode frame run encode input function
        elif 'encode' in widget_source.lower():
            encode_input_function(file_input)


# source --------------------------------------------------------------------------------------------------------------
source_frame = LabelFrame(root, text=' Source (*.avs / *.vpy / StaxRip Temp Directory) ', labelanchor="nw")
source_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
source_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
source_frame.grid_rowconfigure(0, weight=1)
source_frame.grid_rowconfigure(1, weight=1)
source_frame.grid_columnconfigure(0, weight=10)
source_frame.grid_columnconfigure(1, weight=100)
source_frame.grid_columnconfigure(2, weight=0)
# Hover tip tool-tip
CustomTooltipLabel(anchor_widget=source_frame, hover_delay=400, background="#363636", foreground="#3498db",
                   font=(set_fixed_font, 9, 'bold'),
                   text='Select Open\nor\nDrag and Drop either the StaxRip Temp Dir or the *.avs/*.vpy script')
source_frame.drop_target_register(DND_FILES)
source_frame.dnd_bind('<<Drop>>', drop_function)


def manual_source_input():
    # define parser
    manual_source_parser = ConfigParser()
    manual_source_parser.read(config_file)

    # check if last used folder exists
    if pathlib.Path(manual_source_parser['last_used_folder']['path']).is_dir():
        manual_initial_dir = pathlib.Path(manual_source_parser['last_used_folder']['path'])
    else:
        manual_initial_dir = '/'

    # get source file input
    source_file_input = filedialog.askopenfilename(parent=root, title='Select Source Script '
                                                                      '(script file without suffix "_source")',
                                                   initialdir=manual_initial_dir,
                                                   filetypes=[("AviSynth, Vapoursynth", "*.avs *.vpy")])
    if source_file_input:
        source_input_function(source_file_input)


# multiple source input button and pop up menu
def source_input_popup_menu(*args):  # Menu for input button
    source_input_menu = Menu(root, tearoff=False, font=(set_font, set_font_size + 1), background="#23272A",
                             foreground="white", activebackground="#23272A", activeforeground="#3498db")  # menu
    source_input_menu.add_command(label='Open Script', command=manual_source_input)
    source_input_menu.add_separator()
    source_input_menu.add_command(label='Open StaxRip Temp Dir', command=staxrip_manual_open)
    source_input_menu.tk_popup(source_button.winfo_rootx(), source_button.winfo_rooty() + 5)


# source button
source_button = HoverButton(source_frame, text="Open", command=source_input_popup_menu, foreground="white",
                            background="#23272A", borderwidth="3", activeforeground="#3498db",
                            activebackground="#23272A")
source_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=N + S + E + W)

# source entry box
source_entry_box = Entry(source_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
source_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=(7, 0), sticky=E + W + N)

# source info frame
source_info_frame = LabelFrame(source_frame, text='Info:', bd=0, bg="#363636", fg="#3498db",
                               font=(set_font, set_font_size))
source_info_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=0, sticky=N + S + E + W)
for s_i_f in range(4):
    source_info_frame.grid_columnconfigure(s_i_f, weight=1)
source_info_frame.grid_rowconfigure(0, weight=1)
source_info_frame.grid_rowconfigure(1, weight=1)

# source labels
source_label = Label(source_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636', foreground="white")
source_label.grid(column=0, row=0, columnspan=4, pady=3, padx=3, sticky=W)
source_hdr_label = Label(source_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636',
                         foreground="white")
source_hdr_label.grid(column=0, row=1, columnspan=4, pady=3, padx=3, sticky=W)


# function to delete source entry
def delete_source_entry():
    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.config(state=DISABLED)
    source_label.config(text=' ' * 100)
    source_hdr_label.config(text=' ' * 100)
    source_file_path.set('')
    source_loaded.set('')
    delete_encode_entry()


reset_source_input = HoverButton(source_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db",
                                 activebackground="#23272A", width=3)
reset_source_input.grid(row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=N + E + W)

# encode --------------------------------------------------------------------------------------------------------------
encode_frame = LabelFrame(root, text=' Encode (*.mp4) ', labelanchor="nw")
encode_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
encode_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
encode_frame.grid_rowconfigure(0, weight=1)
encode_frame.grid_rowconfigure(1, weight=1)
encode_frame.grid_columnconfigure(0, weight=10)
encode_frame.grid_columnconfigure(1, weight=100)
encode_frame.grid_columnconfigure(3, weight=0)

encode_frame.drop_target_register(DND_FILES)
encode_frame.dnd_bind('<<Drop>>', drop_function)


def manual_encode_input():
    # define parser
    manual_encode_parser = ConfigParser()
    manual_encode_parser.read(config_file)

    # check if last used folder exists
    if pathlib.Path(manual_encode_parser['last_used_folder']['path']).is_dir():
        manual_initial_enc_dir = pathlib.Path(manual_encode_parser['last_used_folder']['path'])
    else:
        manual_initial_enc_dir = '/'

    # get encode input
    encode_file_input = filedialog.askopenfilename(parent=root, title='Select Encode',
                                                   initialdir=manual_initial_enc_dir,
                                                   filetypes=[("Media Files", "*.*")])
    if encode_file_input:
        encode_input_function(encode_file_input)


encode_button = HoverButton(encode_frame, text="Open", command=manual_encode_input, foreground="white",
                            background="#23272A", borderwidth="3", activeforeground="#3498db",
                            activebackground="#23272A")
encode_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=N + E + W)

encode_entry_box = Entry(encode_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
encode_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=(7, 0), sticky=E + W + N)

encode_info_frame = LabelFrame(encode_frame, text='Info:', bd=0, bg="#363636", fg="#3498db",
                               font=(set_font, set_font_size))
encode_info_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=0, sticky=N + S + E + W)
for s_i_f in range(4):
    encode_info_frame.grid_columnconfigure(s_i_f, weight=1)
encode_info_frame.grid_rowconfigure(0, weight=1)
encode_info_frame.grid_rowconfigure(1, weight=1)

encode_label = Label(encode_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636', foreground="white")
encode_label.grid(column=0, row=0, columnspan=1, pady=3, padx=3, sticky=W)
encode_hdr_label = Label(encode_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636',
                         foreground="white")
encode_hdr_label.grid(column=0, row=1, columnspan=1, pady=3, padx=3, sticky=W)


def delete_encode_entry():
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.config(state=DISABLED)
    encode_label.config(text=' ' * 100)
    encode_hdr_label.config(text=' ' * 100)
    release_notes_scrolled.config(state=NORMAL)
    release_notes_scrolled.delete('1.0', END)
    release_notes_scrolled.config(state=DISABLED)
    disable_clear_all_checkbuttons()
    torrent_file_path.set('')
    open_torrent_window_button.config(state=DISABLED)
    generate_nfo_button.config(state=DISABLED)
    encode_file_path.set('')
    encode_file_resolution.set('')
    encode_media_info.set('')
    encode_file_audio.set('')
    encode_hdr_string.set('')


reset_encode_input = HoverButton(encode_frame, text="X", command=delete_encode_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db",
                                 activebackground="#23272A", width=3)
reset_encode_input.grid(row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=N + E + W)


# staxrip directory ---------------------------------------------------------------------------------------------------
def staxrip_working_directory(stax_dir_path):
    # get source and encode paths
    def get_source_and_encode_paths(log_path):
        # open log path file
        with open(pathlib.Path(log_path), 'rt') as source_log:
            # load logfile into memory
            log_file_loaded = source_log.read()
            # check for script type
            if '- AviSynth Script -' in log_file_loaded:
                # get source path
                get_source_path = pathlib.Path(log_path.replace('_staxrip.log', '.avs'))
            elif '- VapourSynth Script -' in log_file_loaded:
                # get source path
                get_source_path = pathlib.Path(log_path.replace('_staxrip.log', '.vpy'))

                # if AviSynth or VapourSynth is not inside the log file
            else:
                messagebox.showerror(parent=root, title='Error',
                                     message='Working directory does not contain the correct information needed.'
                                             '\n\nYou will need to manually input the source (encode.avs/vpy) script')
                # restore transparency
                root.wm_attributes('-alpha', 1.0)
                # exit the function
                return

            # find encode file output path
            get_encode_path = re.search(r"Saving\s(.+\.mp4):", log_file_loaded)

        # if both paths are located load them into the program
        if get_source_path and get_encode_path:
            # restore transparency
            root.wm_attributes('-alpha', 1.0)
            # run source input function
            if pathlib.Path(get_source_path).is_file():
                run_source_func = source_input_function(get_source_path)
            else:
                messagebox.showinfo(title='Info', message='Could not load source script, please input this manually')

            # if user cancels source_input_function code exit this function as well
            if not run_source_func:
                return  # exit this function

            try:
                if pathlib.Path(get_encode_path.group(1)).is_file():
                    encode_input_function(get_encode_path.group(1))
                else:
                    messagebox.showinfo(title='Info', message='Could not load encode "*BHDStudio.mp4", please input '
                                                              'this manually')
            except OSError:
                messagebox.showinfo(title='Info', message='Could not load encode "*BHDStudio.mp4", please input '
                                                          'this manually')

        # if both paths are not located
        else:
            messagebox.showerror(title='Error',
                                 message='Could not locate source and/or encode path.\n\nLoad these manually.')
            # restore transparency
            root.wm_attributes('-alpha', 1.0)
            return  # exit function

    # create empty dictionary
    dict_of_stax_logs = {}

    # check for log files with filters
    for log_file in pathlib.Path(stax_dir_path).glob("*.log"):
        if '720p' in log_file.name.lower() and 'bhdstudio' in log_file.name.lower():
            dict_of_stax_logs.update({str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))})
        if '1080p' in log_file.name.lower() and 'bhdstudio' in log_file.name.lower():
            dict_of_stax_logs.update({str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))})
        if '2160p' in log_file.name.lower() and 'bhdstudio' in log_file.name.lower():
            dict_of_stax_logs.update({str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))})

    # if "bhd" log files was not found remove filters and search again
    if not dict_of_stax_logs:
        for log_file in pathlib.Path(stax_dir_path).glob("*.log"):
            dict_of_stax_logs.update({str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))})

    # check if any logs exist now...
    # if logs are not found
    if not dict_of_stax_logs:
        messagebox.showinfo(parent=root, title='Info', message='Unable to find any log files. Please manually '
                                                               'open source and encode files.')
        # restore transparency
        root.wm_attributes('-alpha', 1.0)
        return  # exit this function

    # if logs are found
    elif dict_of_stax_logs:
        # if there is more than 1 log file
        if len(dict_of_stax_logs) >= 2:
            stax_log_win = Toplevel()  # Toplevel window
            stax_log_win.configure(background='#363636')  # Set color of stax_log_win background
            stax_log_win.title('Log Files')
            # Open on top left of root window
            stax_log_win.geometry(f'{480}x{160}+{str(int(root.geometry().split("+")[1]) + 108)}+'
                                  f'{str(int(root.geometry().split("+")[2]) + 80)}')
            stax_log_win.resizable(False, False)  # makes window not resizable
            stax_log_win.grab_set()  # forces stax_log_win to stay on top of root
            stax_log_win.wm_overrideredirect(True)
            root.wm_attributes('-alpha', 0.92)  # set main gui to be slightly transparent
            stax_log_win.grid_rowconfigure(0, weight=1)
            stax_log_win.grid_columnconfigure(0, weight=1)

            stax_frame = Frame(stax_log_win, highlightbackground="white", highlightthickness=2, bg="#363636",
                               highlightcolor='white')
            stax_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
            for e_n_f in range(3):
                stax_frame.grid_columnconfigure(e_n_f, weight=1)
                stax_frame.grid_rowconfigure(e_n_f, weight=1)

            # create label
            stax_info_label = Label(stax_frame, text='Select logfile to parse information from:',
                                    background='#363636', fg="#3498db", font=(set_font, set_font_size, "bold"))
            stax_info_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

            # create menu
            log_pop_up_var = StringVar()
            log_pop_up_var.set(next(iter(reversed(dict_of_stax_logs))))
            log_pop_up_menu = OptionMenu(stax_frame, log_pop_up_var, *reversed(dict_of_stax_logs.keys()))
            log_pop_up_menu.config(background="#23272A", foreground="white", highlightthickness=1,
                                   width=48, anchor='w', activebackground="#23272A", activeforeground="#3498db")
            log_pop_up_menu.grid(row=1, column=0, columnspan=3, padx=10, pady=6, sticky=N + W + E)
            log_pop_up_menu["menu"].configure(background="#23272A", foreground="white", activebackground="#23272A",
                                              activeforeground="#3498db")

            # create 'OK' button
            def stax_ok_function():
                # close stax_log_window
                stax_log_win.destroy()
                # run function to parse log file
                get_source_and_encode_paths(dict_of_stax_logs[log_pop_up_var.get()])

            stax_okay_btn = HoverButton(stax_frame, text="OK", command=stax_ok_function, foreground="white",
                                        background="#23272A", borderwidth="3", width=8, activeforeground="#3498db",
                                        activebackground="#23272A")
            stax_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

            # create 'Cancel' button
            def stax_cancel_function():
                # restore transparency
                root.wm_attributes('-alpha', 1.0)
                # close window
                stax_log_win.destroy()
                # reset main gui
                reset_gui()

            stax_cancel_btn = HoverButton(stax_frame, text="Cancel", command=stax_cancel_function,
                                          foreground="white", background="#23272A", borderwidth="3", width=8,
                                          activeforeground="#3498db", activebackground="#23272A")
            stax_cancel_btn.grid(row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

            # wait for the window to be closed to do anything else
            stax_log_win.wait_window()

        # if there is only 1 log file
        else:
            # get the only value in the dictionary
            get_source_and_encode_paths(next(iter(dict_of_stax_logs.values())))


# staxrip manual open
def staxrip_manual_open():
    # open filedialog
    parse_stax_temp_dir = filedialog.askdirectory(parent=root, title='StaxRip Working Directory')

    if parse_stax_temp_dir:
        staxrip_working_directory(parse_stax_temp_dir)


# release notes -------------------------------------------------------------------------------------------------------
release_notes_frame = LabelFrame(root, text=' Release Notes ', labelanchor="nw")
release_notes_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
release_notes_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))

for rl_row in range(3):
    release_notes_frame.grid_rowconfigure(rl_row, weight=1)
for rl_f in range(3):
    release_notes_frame.grid_columnconfigure(rl_f, weight=1)


def update_forced_var():
    release_notes_scrolled.config(state=NORMAL)
    if forced_subtitles_burned_var.get() == 'on':
        release_notes_scrolled.insert(END, '\n-Forced English subtitles embedded for non English dialogue')
    elif forced_subtitles_burned_var.get() == 'off':
        delete_forced = release_notes_scrolled.search(
            "-Forced English subtitles embedded for non English dialogue", '1.0', END)
        if delete_forced != '':
            release_notes_scrolled.delete(str(delete_forced), str(float(delete_forced) + 1.0))
    release_notes_scrolled.config(state=DISABLED)


forced_subtitles_burned_var = StringVar()
forced_subtitles_burned = Checkbutton(release_notes_frame, text='Forced Subtitles',
                                      variable=forced_subtitles_burned_var, takefocus=False,
                                      onvalue='on', offvalue='off', command=update_forced_var,
                                      background="#363636", foreground="white", activebackground="#363636",
                                      activeforeground="white", selectcolor="#434547",
                                      font=(set_font, set_font_size + 1), state=DISABLED)
forced_subtitles_burned.grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N)
forced_subtitles_burned_var.set('off')


def update_balanced_borders():
    release_notes_scrolled.config(state=NORMAL)
    if balance_borders_var.get() == 'on':
        release_notes_scrolled.insert(END, '\n-Cleaned dirty edges with BalanceBorders')
    elif balance_borders_var.get() == 'off':
        delete_balanced_borders = release_notes_scrolled.search("-Cleaned dirty edges with BalanceBorders", '1.0', END)
        if delete_balanced_borders != '':
            release_notes_scrolled.delete(str(delete_balanced_borders), str(float(delete_balanced_borders) + 1.0))
    release_notes_scrolled.config(state=DISABLED)


balance_borders_var = StringVar()
balance_borders = Checkbutton(release_notes_frame, text='Balance Borders',
                              variable=balance_borders_var, takefocus=False,
                              onvalue='on', offvalue='off', command=update_balanced_borders,
                              background="#363636", foreground="white", activebackground="#363636",
                              activeforeground="white", selectcolor="#434547",
                              font=(set_font, set_font_size + 1), state=DISABLED)
balance_borders.grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N)
balance_borders_var.set('off')


def update_fill_borders():
    release_notes_scrolled.config(state=NORMAL)
    if fill_borders_var.get() == 'on':
        release_notes_scrolled.insert(END, '\n-Fill borders with FillBorders')
    elif fill_borders_var.get() == 'off':
        delete_fill_borders = release_notes_scrolled.search("-Fill borders with FillBorders", '1.0', END)
        if delete_fill_borders != '':
            release_notes_scrolled.delete(str(delete_fill_borders), str(float(delete_fill_borders) + 1.0))
    release_notes_scrolled.config(state=DISABLED)


fill_borders_var = StringVar()
fill_borders = Checkbutton(release_notes_frame, text='Fill Borders',
                           variable=fill_borders_var, takefocus=False,
                           onvalue='on', offvalue='off', command=update_fill_borders,
                           background="#363636", foreground="white", activebackground="#363636",
                           activeforeground="white", selectcolor="#434547",
                           font=(set_font, set_font_size + 1), state=DISABLED)
fill_borders.grid(row=0, column=2, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N)
fill_borders_var.set('off')

release_notes_scrolled = scrolledtextwidget.ScrolledText(release_notes_frame, height=5, bg="#565656", bd=4, fg='white')
release_notes_scrolled.grid(row=1, column=0, columnspan=4, pady=(0, 2), padx=5, sticky=E + W)
release_notes_scrolled.config(state=DISABLED)
# Hover tip tool-tip
CustomTooltipLabel(anchor_widget=release_notes_scrolled, hover_delay=400, background="#363636", foreground="#3498db",
                   font=(set_fixed_font, 9, 'bold'), text='Right click for more options')


# right click menu for screenshot box
def popup_auto_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
    enable_edits_menu.tk_popup(e.x_root, e.y_root)  # This gets the position of 'e'


# pop up menu to enable/disable manual edits in release notes
enable_edits_menu = Menu(release_notes_scrolled, tearoff=False, font=(set_font, set_font_size + 1),
                         background="#23272A", foreground="white", activebackground="#23272A",
                         activeforeground="#3498db")  # Right click menu
enable_edits_menu.add_command(label='Enable Manual Edits', command=lambda: release_notes_scrolled.config(state=NORMAL))
enable_edits_menu.add_command(label='Disable Manual Edits',
                              command=lambda: release_notes_scrolled.config(state=DISABLED))
enable_edits_menu.add_separator()
enable_edits_menu.add_command(label='Open Script In Default Viewer',
                              command=lambda: os.startfile(pathlib.Path(input_script_path.get())))
release_notes_scrolled.bind('<Button-3>', popup_auto_e_b_menu)  # Uses mouse button 3 (right click) to open


def disable_clear_all_checkbuttons():
    forced_subtitles_burned.config(state=NORMAL)
    balance_borders.config(state=NORMAL)
    fill_borders.config(state=NORMAL)
    forced_subtitles_burned_var.set('off')
    balance_borders_var.set('off')
    fill_borders_var.set('off')
    forced_subtitles_burned.config(state=DISABLED)
    balance_borders.config(state=DISABLED)
    fill_borders.config(state=DISABLED)


def enable_clear_all_checkbuttons():
    forced_subtitles_burned.config(state=NORMAL)
    balance_borders.config(state=NORMAL)
    fill_borders.config(state=NORMAL)
    forced_subtitles_burned_var.set('off')
    balance_borders_var.set('off')
    fill_borders_var.set('off')


# screenshots ---------------------------------------------------------------------------------------------------------
screenshot_frame = LabelFrame(root, text=' Sreenshots ', labelanchor="nw")
screenshot_frame.grid(column=0, row=3, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
screenshot_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
screenshot_frame.grid_rowconfigure(0, weight=1)
screenshot_frame.grid_columnconfigure(0, weight=1)

# Settings Notebook Frame -----------------------------------------------------------------------------------------
tabs = ttk.Notebook(screenshot_frame, height=150)
tabs.grid(row=0, column=0, columnspan=4, sticky=E + W + N + S, padx=0, pady=0)
tabs.grid_columnconfigure(0, weight=1)
tabs.grid_rowconfigure(0, weight=1)

# image input tab
image_tab = Frame(tabs, background='#434547')
tabs.add(image_tab, text=' Images ')
image_tab.grid_rowconfigure(0, weight=1)
image_tab.grid_columnconfigure(0, weight=100)
image_tab.grid_columnconfigure(3, weight=1)

# image frame
image_frame = Frame(image_tab, bg="#363636", bd=0)
image_frame.grid(column=0, columnspan=3, row=0, pady=4, padx=4, sticky=W + E + N + S)
image_frame.grid_columnconfigure(0, weight=1)
image_frame.grid_rowconfigure(0, weight=1)

# image listbox
image_right_scrollbar = Scrollbar(image_frame, orient=VERTICAL)  # scrollbar
image_bottom_scrollbar = Scrollbar(image_frame, orient=HORIZONTAL)  # scrollbar
image_listbox = Listbox(image_frame, selectbackground="#565656", background="#565656", disabledforeground="white",
                        selectforeground="#3498db", foreground="white", height=12, state=DISABLED, highlightthickness=0,
                        yscrollcommand=image_right_scrollbar.set, selectmode=SINGLE, bd=4, activestyle="none",
                        xscrollcommand=image_bottom_scrollbar.set)
image_listbox.grid(row=0, column=0, rowspan=1, sticky=N + E + S + W)
image_right_scrollbar.config(command=image_listbox.yview)
image_right_scrollbar.grid(row=0, column=1, rowspan=2, sticky=N + W + S)
image_bottom_scrollbar.config(command=image_listbox.xview)
image_bottom_scrollbar.grid(row=1, column=0, sticky=E + W + N)

# image button frame
image_btn_frame = Frame(image_tab, bg='#434547', bd=0)
image_btn_frame.grid(column=3, row=0, padx=5, pady=(5, 3), sticky=E + W + N + S)
image_btn_frame.grid_rowconfigure(0, weight=1)
image_btn_frame.grid_rowconfigure(1, weight=1)
image_btn_frame.grid_rowconfigure(2, weight=1)
image_btn_frame.grid_columnconfigure(0, weight=1)
image_btn_frame.grid_columnconfigure(1, weight=1)


# function to add images to listbox
def update_image_listbox(list_of_images):
    # check if source is loaded
    if source_loaded.get() == '':
        messagebox.showinfo(parent=root, title='Info', message='You must open a source file first')
        return  # exit function

    # check if source is loaded
    if encode_file_path.get() == '':
        messagebox.showinfo(parent=root, title='Info', message='You must open a encode file first')
        return  # exit function

    # check dropped data to ensure files are .png and correct size
    for dropped_files in list_of_images:
        # png check
        if pathlib.Path(dropped_files).suffix != ".png":
            messagebox.showerror(parent=root, title='Error', message='Can only drop .PNG files')
            return  # exit this function
        # size check
        if os.stat(pathlib.Path(dropped_files)).st_size > 30000000:
            messagebox.showerror(parent=root, title='Error', message='File must be under 30MB')
            return  # exit this function

    # check for resolution miss-match
    for opened_image_file in list_of_images:
        # get opened file resolution
        media_info = MediaInfo.parse(pathlib.Path(opened_image_file))
        image_track_width = media_info.image_tracks[0].width

        # check if both image files and encode resolution is 720p
        if image_track_width <= 1280:  # 720p
            if encode_file_resolution.get() != '720p':
                messagebox.showinfo(parent=root, title='Resolution Error',
                                    message=f"Encode source resolution is {encode_file_resolution.get()}.\n\nYour "
                                            f"screenshots should be the same resolution")
                return  # exit this function

        # check if both image files and encode resolution is 1080p
        elif image_track_width <= 1920:  # 1080p
            if encode_file_resolution.get() != '1080p':
                messagebox.showinfo(parent=root, title='Resolution Error',
                                    message=f"Encode source resolution is {encode_file_resolution.get()}.\n\nYour "
                                            f"screenshots should be the same resolution")
                return  # exit this function

        # check if both image files and encode resolution is 2160p
        elif image_track_width <= 3840:  # 2160p
            if encode_file_resolution.get() != '2160p':
                messagebox.showinfo(parent=root, title='Resolution Error',
                                    message=f"Encode source resolution is {encode_file_resolution.get()}.\n\nYour "
                                            f"screenshots should be the same resolution")
                return  # exit this function

    # check that screenshots are in multiples of 2
    if not len(list_of_images) % 2 == 0:  # if not multiples of 2
        messagebox.showerror(parent=root, title='Error', message='Screen shots must be even numbers')
        return  # exit this function

    # add images to the list box
    image_listbox.config(state=NORMAL)
    image_listbox.delete(0, END)
    for img_num, png_img in enumerate(list_of_images, start=1):
        image_listbox.insert(END, f"{img_num}) {png_img}")
    image_listbox.config(state=DISABLED)

    # enable upload button
    upload_ss_button.config(state=NORMAL)


# open screenshot directory function
def open_ss_directory():
    # file dialog to get directory of input files
    ss_dir = filedialog.askdirectory(parent=root, title='Select Directory')

    if ss_dir:
        # disable upload button
        upload_ss_button.config(state=DISABLED)

        # create empty list to be filled
        ss_dir_files_list = []

        # get all .png files from directory
        for ss_files in pathlib.Path(ss_dir).glob('*.png'):
            ss_dir_files_list.append(pathlib.Path(ss_files))

        # call update image listbox function
        update_image_listbox(ss_dir_files_list)


# open files function
def open_ss_files():
    # file dialog to get directory of input files
    ss_files_input = filedialog.askopenfilenames(parent=root, title='Select Files', filetypes=[("PNG", "*.png")])

    # if user opens files
    if ss_files_input:
        # disable upload button
        upload_ss_button.config(state=DISABLED)

        # create empty list to be filled
        ss_files_input_files_list = []

        for ss_files in ss_files_input:
            ss_files_input_files_list.append(pathlib.Path(ss_files))

        # call update image listbox function
        update_image_listbox(ss_files_input_files_list)


# multiple input button and pop up menu
def input_popup_menu(*args):  # Menu for input button
    input_menu = Menu(image_btn_frame, tearoff=False, font=(set_font, set_font_size + 1), background="#23272A",
                      foreground="white", activebackground="#23272A", activeforeground="#3498db")  # Menu
    input_menu.add_command(label='Open Files', command=open_ss_files)
    input_menu.add_separator()
    input_menu.add_command(label='Open Directory', command=open_ss_directory)
    input_menu.tk_popup(input_button.winfo_rootx(), input_button.winfo_rooty() + 5)


input_button = HoverButton(image_btn_frame, text="Open...", command=input_popup_menu,
                           foreground="white", background="#23272A", borderwidth="3",
                           activeforeground="#3498db", activebackground="#23272A", width=12)
input_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + W)
input_button.bind('<Button-3>', input_popup_menu)  # Right click to pop up menu in frame


# png and drop function for image list box
def png_file_drag_and_drop(event):
    # disable upload button
    upload_ss_button.config(state=DISABLED)

    # get dropped data
    png_file_dropped = [x for x in root.splitlist(event.data)]

    # call update image listbox function
    update_image_listbox(png_file_dropped)


# bind frame to drop images into listbox
image_frame.drop_target_register(DND_FILES)
image_frame.dnd_bind('<<Drop>>', png_file_drag_and_drop)


# clear button function
def clear_image_list():
    # remove everything from image listbox
    image_listbox.config(state=NORMAL)
    image_listbox.delete(0, END)
    image_listbox.config(state=DISABLED)
    # disable upload button
    upload_ss_button.config(state=DISABLED)


# clear button
clear_ss_win_btn = HoverButton(image_btn_frame, text="Clear", command=clear_image_list,
                               foreground="white", background="#23272A", borderwidth="3",
                               activeforeground="#3498db", activebackground="#23272A", width=12)
clear_ss_win_btn.grid(row=0, column=1, columnspan=1, padx=5, pady=(7, 0), sticky=N + E)


# function to automatically generate screenshots
def automatic_screenshot_generator():
    # define parser
    auto_screenshot_parser = ConfigParser()
    auto_screenshot_parser.read(config_file)

    # create image viewer
    image_viewer = Toplevel()
    image_viewer.title('Image Viewer')
    image_viewer.configure(background="#434547")
    iv_window_height = 720
    iv_window_width = 1400
    if auto_screenshot_parser['save_window_locations']['image_viewer'] == '':
        iv_screen_width = root.winfo_screenwidth()
        iv_screen_height = root.winfo_screenheight()
        iv_x_coordinate = int((iv_screen_width / 2) - (iv_window_width / 2))
        iv_y_coordinate = int((iv_screen_height / 2) - (iv_window_height / 2))
        image_viewer.geometry(f"{iv_window_width}x{iv_window_height}+{iv_x_coordinate}+{iv_y_coordinate}")
    elif auto_screenshot_parser['save_window_locations']['image_viewer'] != '':
        image_viewer.geometry(auto_screenshot_parser['save_window_locations']['image_viewer'])

    # row and column configure
    for i_v_r in range(3):
        image_viewer.grid_rowconfigure(i_v_r, weight=1)
    for i_v_c in range(5):
        image_viewer.grid_columnconfigure(i_v_c, weight=1)

    # image info frame
    image_info_frame = LabelFrame(image_viewer, bg="#434547", text=' Image Info ', labelanchor="nw",
                                  fg="#3498db", bd=3, font=(set_font, 10, 'bold'))
    image_info_frame.grid(column=0, row=0, columnspan=4, pady=2, padx=2, sticky=N + S + E + W)
    image_info_frame.grid_columnconfigure(0, weight=1)
    image_info_frame.grid_columnconfigure(1, weight=100)
    image_info_frame.grid_columnconfigure(2, weight=1)
    image_info_frame.grid_rowconfigure(0, weight=1)

    # create name label
    image_name_label = Label(image_info_frame, background="#434547", fg="white", font=(set_font, set_font_size - 1))
    image_name_label.grid(row=0, column=0, columnspan=1, sticky=W, padx=5, pady=(2, 0))

    # create image resolution label
    image_resolution_label = Label(image_info_frame, background="#434547", fg="white",
                                   font=(set_font, set_font_size - 1))
    image_resolution_label.grid(row=0, column=1, columnspan=1, sticky=E, padx=10, pady=(2, 0))

    # create image number label
    image_number_label = Label(image_info_frame, background="#434547", fg="white",
                               font=(set_font, set_font_size - 1))
    image_number_label.grid(row=0, column=2, columnspan=1, sticky=E, padx=5, pady=(2, 0))

    # create image preview frame
    image_preview_frame = LabelFrame(image_viewer, bg="#434547", text=' Image Preview ', labelanchor="nw",
                                     fg="#3498db", bd=3, font=(set_font, 10, 'bold'))
    image_preview_frame.grid(column=0, row=1, columnspan=4, pady=2, padx=2, sticky=N + S + E + W)
    image_preview_frame.grid_columnconfigure(0, weight=1)
    image_preview_frame.grid_rowconfigure(0, weight=1)

    # create emtpy image list
    comparison_img_list = []

    # loop through comparison directory and get all images
    for x_img in pathlib.Path(screenshot_comparison_var.get()).glob("*.png"):
        comparison_img_list.append(x_img)

    # set index variable
    comparison_index = 0

    # update image name label with first image from list
    image_name_label.config(text=f"{pathlib.Path(comparison_img_list[comparison_index]).name}")

    # parse first image from list to get resolution
    media_info_img = MediaInfo.parse(pathlib.Path(comparison_img_list[comparison_index]))
    image_track = media_info_img.image_tracks[0]

    # update image resolution label
    image_resolution_label.config(text=f"{image_track.width}x{image_track.height}")

    # label to print what photo of amount of total photos you are on
    image_number_label.config(text=f"{comparison_index + 1} of {len(comparison_img_list)}")

    # create image instance and resize the photo
    loaded_image = Image.open(comparison_img_list[comparison_index])
    loaded_image.thumbnail((1000, 562), Image.Resampling.LANCZOS)
    resized_image = ImageTk.PhotoImage(loaded_image)

    # put resized image into label
    image_preview_label = Label(image_preview_frame, image=resized_image, background="#434547", cursor='hand2')
    image_preview_label.image = resized_image
    image_preview_label.grid(column=0, row=0, columnspan=1)

    # add a left click function to open the photo in your default os viewer
    image_preview_label.bind("<Button-1>", lambda event: Image.open(comparison_img_list[comparison_index]).show())

    # create image button frame
    img_button_frame = Frame(image_viewer, bg="#434547")
    img_button_frame.grid(column=0, row=2, columnspan=4, pady=2, padx=2, sticky=N + S + E + W)
    img_button_frame.grid_columnconfigure(0, weight=1000)
    img_button_frame.grid_columnconfigure(1, weight=1000)
    img_button_frame.grid_rowconfigure(0, weight=1)

    # function to load next image
    def load_next_image(*e_right):
        nonlocal image_preview_label, comparison_index
        # if next image is not disabled (this prevents the keystrokes from doing anything when it should be disabled)
        if next_img.cget('state') != DISABLED:
            # increase the comparison index value by 1
            comparison_index += 1

            # open the image in the viewer
            im = Image.open(comparison_img_list[comparison_index])
            im.thumbnail((1000, 562), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            image_preview_label.config(image=photo)
            image_preview_label.image = photo

            # update the left click photo to open in OS photo viewer
            image_preview_label.bind("<Button-1>", lambda event: Image.open(
                comparison_img_list[comparison_index]).show())

            # update all the labels
            image_name_label.config(text=f"{pathlib.Path(comparison_img_list[comparison_index]).name}")
            media_info_img_next = MediaInfo.parse(pathlib.Path(comparison_img_list[comparison_index]))
            image_track_next = media_info_img_next.image_tracks[0]
            image_resolution_label.config(text=f"{image_track_next.width}x{image_track_next.height}")
            image_number_label.config(text=f"{comparison_index + 1} of {len(comparison_img_list)}")

    # button to run next image function
    next_img = HoverButton(img_button_frame, text=">>", command=load_next_image, foreground="white",
                           background="#23272A", borderwidth="3", activeforeground="#3498db",
                           activebackground="#23272A", width=4)
    next_img.grid(row=0, column=1, columnspan=1, padx=5, pady=(7, 0), sticky=W)

    # bind right arrow key (on key release) to load the next image
    image_viewer.bind("<KeyRelease-Right>", load_next_image)

    # function to load last image
    def load_last_image(*e_left):
        nonlocal image_preview_label, comparison_index
        # if back image is not disabled (this prevents the keystrokes from doing anything when it should be disabled)
        if back_img.cget('state') != DISABLED:
            # subtract the comparison index by 1
            comparison_index -= 1

            # update the image in the image viewer
            im = Image.open(comparison_img_list[comparison_index])
            im.thumbnail((1000, 562), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            image_preview_label.config(image=photo)
            image_preview_label.image = photo

            # load new image to be opened when left clicked in OS native viewer
            image_preview_label.bind("<Button-1>", lambda event: Image.open(
                comparison_img_list[comparison_index]).show())

            # update all the labels
            image_name_label.config(text=f"{pathlib.Path(comparison_img_list[comparison_index]).name}")
            media_info_img_back = MediaInfo.parse(pathlib.Path(comparison_img_list[comparison_index]))
            image_track_back = media_info_img_back.image_tracks[0]
            image_resolution_label.config(text=f"{image_track_back.width}x{image_track_back.height}")
            image_number_label.config(text=f"{comparison_index + 1} of {len(comparison_img_list)}")

    # button to run last image function
    back_img = HoverButton(img_button_frame, text="<<", command=load_last_image, foreground="white",
                           background="#23272A", borderwidth="3", activeforeground="#3498db",
                           activebackground="#23272A", width=4)
    back_img.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=E)

    # bind the left arrow key (on key release)
    image_viewer.bind("<KeyRelease-Left>", load_last_image)

    # info frame for the image viewer
    set_info_frame = LabelFrame(image_viewer, bg="#434547", text=' Info ', labelanchor="nw",
                                fg="#3498db", bd=3, font=(set_font, 10, 'bold'))
    set_info_frame.grid(column=4, row=0, columnspan=1, pady=2, padx=2, sticky=N + S + E + W)
    set_info_frame.grid_columnconfigure(0, weight=1)
    set_info_frame.grid_columnconfigure(1, weight=100)
    set_info_frame.grid_columnconfigure(2, weight=1)
    set_info_frame.grid_rowconfigure(0, weight=1)

    # image viewer frame
    img_viewer_frame = Frame(image_viewer, bg="#434547", bd=0)
    img_viewer_frame.grid(column=4, columnspan=1, row=1, rowspan=1, pady=3, padx=4, sticky=W + E + N + S)
    img_viewer_frame.grid_columnconfigure(0, weight=1)
    img_viewer_frame.grid_rowconfigure(0, weight=200)
    img_viewer_frame.grid_rowconfigure(1, weight=200)
    img_viewer_frame.grid_rowconfigure(1, weight=1)

    # create image name label
    image_name_label2 = Label(set_info_frame, text="0 sets (0 images)", background="#434547", fg="white",
                              font=(set_font, set_font_size - 1))
    image_name_label2.grid(row=0, column=0, columnspan=1, sticky=E, padx=5, pady=(2, 0))

    # create image info label
    image_name1_label = Label(set_info_frame, text="6 sets (12 images) required", background="#434547", fg="white",
                              font=(set_font, set_font_size - 1, "italic"))
    image_name1_label.grid(row=0, column=1, columnspan=1, sticky=E, padx=5, pady=(2, 0))

    # right scroll bar for selected listbox
    image_v_right_scrollbar = Scrollbar(img_viewer_frame, orient=VERTICAL)

    # create selected list box
    img_viewer_listbox = Listbox(img_viewer_frame, selectbackground="#565656", background="#565656",
                                 disabledforeground="white", selectforeground="#3498db", foreground="white",
                                 highlightthickness=0, width=40, yscrollcommand=image_v_right_scrollbar.set,
                                 selectmode=SINGLE, bd=4, activestyle="none")
    img_viewer_listbox.grid(row=0, column=0, rowspan=2, sticky=N + E + S + W, pady=(8, 0))
    image_v_right_scrollbar.config(command=img_viewer_listbox.yview)
    image_v_right_scrollbar.grid(row=0, column=2, rowspan=2, sticky=N + W + S, pady=(8, 0))

    # image button frame for selected list box
    img_button2_frame = Frame(image_viewer, bg="#434547")
    img_button2_frame.grid(column=4, row=2, columnspan=1, pady=2, padx=2, sticky=N + S + E + W)
    img_button2_frame.grid_columnconfigure(0, weight=100)
    img_button2_frame.grid_columnconfigure(1, weight=100)
    img_button2_frame.grid_columnconfigure(2, weight=1)
    img_button2_frame.grid_rowconfigure(0, weight=1)

    # create variable to be updated for index purposes
    selected_index_var = 0

    # remove pair from listbox function
    def remove_pair_from_listbox():
        nonlocal comparison_index, comparison_img_list, selected_index_var
        # if something is selected in the list box
        if img_viewer_listbox.curselection():
            # get the selected item from list box
            for i in img_viewer_listbox.curselection():
                get_frame_number = re.search(r"__(\d+)", str(img_viewer_listbox.get(i)))

            # get the frame number to match the pairs
            for images_with_prefix in img_viewer_listbox.get(0, END):
                get_pair = re.findall(rf".+__{get_frame_number.group(1)}\.png", images_with_prefix)
                # once pair is found
                if get_pair:
                    # use pathlib rename feature to move the file back to the comparison directory/out of the listbox
                    pathlib.Path(pathlib.Path(screenshot_selected_var.get()) / get_pair[0]).rename(
                        pathlib.Path(pathlib.Path(screenshot_comparison_var.get()) / get_pair[0]))

            # delete the list box and update it with what ever is left
            img_viewer_listbox.delete(0, END)
            for x in pathlib.Path(screenshot_selected_var.get()).glob("*.png"):
                img_viewer_listbox.insert(END, x.name)

            # clear the comparison image list
            comparison_img_list.clear()

            # update the comparison image list with everything in the directory
            for x in pathlib.Path(screenshot_comparison_var.get()).glob("*.png"):
                comparison_img_list.append(x)

            # if there is at least 1 item in the list
            if comparison_img_list:
                # refresh the image viewer with the updated list (attempt to retain position)
                comparison_index = selected_index_var
                im = Image.open(comparison_img_list[comparison_index])
                im.thumbnail((1000, 562), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(im)
                image_preview_label.grid()
                image_preview_label.config(image=photo)
                image_preview_label.image = photo
                image_preview_label.bind("<Button-1>",
                                         lambda event: Image.open(comparison_img_list[comparison_index]).show())

                # update labels
                image_name_label.config(text=f"{pathlib.Path(comparison_img_list[comparison_index]).name}")
                media_info_img_rem = MediaInfo.parse(pathlib.Path(comparison_img_list[comparison_index]))
                image_track_rem = media_info_img_rem.image_tracks[0]
                image_resolution_label.config(text=f"{image_track_rem.width}x{image_track_rem.height}")
                image_number_label.config(text=f"{comparison_index + 1} of {len(comparison_img_list)}")
                image_name_label2.config(text=f"{int(img_viewer_listbox.size() * .5)} sets "
                                              f"({img_viewer_listbox.size()} images)")

    # create minis/reverse button
    minus_btn = HoverButton(img_button2_frame, text="<<<", command=remove_pair_from_listbox, foreground="white",
                            background="#23272A", borderwidth="3", activeforeground="#3498db",
                            activebackground="#23272A", width=4)
    minus_btn.grid(row=0, column=0, padx=5, sticky=E)

    # function to add pair to the selected listbox
    def add_pair_to_listbox():
        nonlocal comparison_index, comparison_img_list, image_preview_label, selected_index_var

        # find the frame number of the pair
        get_frame_number = re.search(r"__(\d+)", str(pathlib.Path(comparison_img_list[comparison_index]).name))
        for full_name in comparison_img_list:
            get_pair = re.findall(rf".+__{get_frame_number.group(1)}\.png", full_name.name)
            # once a pair is found use pathlib rename to move them from the comparison list/dir to the selected dir/list
            if get_pair:
                pathlib.Path(pathlib.Path(screenshot_comparison_var.get()) / get_pair[0]).rename(pathlib.Path(
                    screenshot_selected_var.get()) / pathlib.Path(get_pair[0]).name)

                # take the last item that is moved and update the selected index var
                selected_index_var = int(comparison_img_list.index(pathlib.Path(
                    screenshot_comparison_var.get()) / get_pair[0])) - 1

        # clear the listbox
        img_viewer_listbox.delete(0, END)

        # update the listbox
        for x_l in pathlib.Path(screenshot_selected_var.get()).glob("*.png"):
            img_viewer_listbox.insert(END, x_l.name)

        # update image info and preview info
        comparison_img_list.clear()
        for x_c in pathlib.Path(screenshot_comparison_var.get()).glob("*.png"):
            comparison_img_list.append(x_c)

        # if there is anything left in the comparison img list
        if comparison_img_list:
            # attempt to use the same index (to keep position the same/close to the same) and update the image viewer
            try:
                comparison_index = selected_index_var
                im = Image.open(comparison_img_list[comparison_index])
            # if unable to use that index subtract 2 from it (this prevents errors at the end of the list)
            except IndexError:
                comparison_index = selected_index_var - 2
                im = Image.open(comparison_img_list[comparison_index])
            im.thumbnail((1000, 562), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            image_preview_label.config(image=photo)
            image_preview_label.image = photo
            image_preview_label.bind("<Button-1>", lambda event: Image.open(
                comparison_img_list[comparison_index]).show())

            # update the labels
            image_name_label.config(text=f"{pathlib.Path(comparison_img_list[comparison_index]).name}")
            media_info_img_add = MediaInfo.parse(pathlib.Path(comparison_img_list[comparison_index]))
            image_track_add = media_info_img_add.image_tracks[0]
            image_resolution_label.config(text=f"{image_track_add.width}x{image_track_add.height}")
            image_number_label.config(text=f"{comparison_index + 1} of {len(comparison_img_list)}")
            image_name_label2.config(text=f"{int(img_viewer_listbox.size() * .5)} sets "
                                          f"({img_viewer_listbox.size()} images)")
        # if there is nothing left in the comparison image box, clear the box and all the labels
        else:
            image_preview_label.grid_forget()
            image_name_label.config(text="")
            image_resolution_label.config(text="")
            image_number_label.config(text="")

    # move right button
    move_right = HoverButton(img_button2_frame, text=">>>", command=add_pair_to_listbox, foreground="white",
                             background="#23272A", borderwidth="3", activeforeground="#3498db",
                             activebackground="#23272A", width=4)
    move_right.grid(row=0, column=1, padx=5, sticky=W)

    # add images to list box function
    def add_images_to_listbox_func():
        # define parser
        add_img_exit_parser = ConfigParser()
        add_img_exit_parser.read(config_file)

        # save window position to config if different
        if image_viewer.wm_state() == 'normal':
            if add_img_exit_parser['save_window_locations']['image_viewer'] != image_viewer.geometry():
                if int(image_viewer.geometry().split('x')[0]) >= iv_window_width or \
                        int(image_viewer.geometry().split('x')[1].split('+')[0]) >= iv_window_height:
                    add_img_exit_parser.set('save_window_locations', 'image_viewer', image_viewer.geometry())
                    with open(config_file, 'w') as nfo_configfile:
                        add_img_exit_parser.write(nfo_configfile)

        # re-open root and all top levels
        advanced_root_deiconify()
        open_all_toplevels()

        # create list of images to autoload into the program
        list_of_selected_images = []
        for selected_img in pathlib.Path(screenshot_selected_var.get()).glob("*.png"):
            list_of_selected_images.append(selected_img)

        # run the function to load screenshots into the main gui
        update_image_listbox(list_of_selected_images)

        # close image viewer window
        image_viewer.destroy()

    # add to image list box button
    add_images_to_listbox = HoverButton(img_button2_frame, text="Apply", command=add_images_to_listbox_func,
                                        state=DISABLED, foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", activebackground="#23272A", width=10)
    add_images_to_listbox.grid(row=0, column=2, padx=5, sticky=E)

    # change 'X' button on image viewer (use the Apply button function)
    image_viewer.protocol('WM_DELETE_WINDOW', add_images_to_listbox_func)

    # loop to enable/disable buttons depending on index
    def enable_disable_buttons_by_index():
        # disable both buttons if list is empty
        if not comparison_img_list:
            back_img.config(state=DISABLED)
            next_img.config(state=DISABLED)
        # enable back or next button depending on the list
        elif comparison_img_list:
            # enable or disable back button
            if comparison_index == 0:
                back_img.config(state=DISABLED)
            else:
                back_img.config(state=NORMAL)
            # enable or disable next button
            if comparison_index == len(comparison_img_list) - 1:
                next_img.config(state=DISABLED)
            else:
                next_img.config(state=NORMAL)

        # enable apply button (check label to see if required amount of sets are met)
        if int(str(image_name_label2.cget('text'))[0]) >= 6:
            add_images_to_listbox.config(state=NORMAL)
        else:
            add_images_to_listbox.config(state=DISABLED)

        image_viewer.after(50, enable_disable_buttons_by_index)

    # start loop for button checker
    enable_disable_buttons_by_index()

    # hide root
    root.withdraw()


# pop up window that allows the user to select which indexer they'd like to use
def choose_indexer_func():
    # hide all top levels if they are opened
    hide_all_toplevels()

    # exit the window
    def exit_index_window():
        index_selection_win.destroy()  # close window
        advanced_root_deiconify()  # restore root

    # index selection window
    index_selection_win = Toplevel()
    index_selection_win.title('Index')
    index_selection_win.configure(background="#363636")
    index_selection_win.geometry(f'{350}x{350}+{str(int(root.geometry().split("+")[1]) + 180)}+'
                                 f'{str(int(root.geometry().split("+")[2]) + 230)}')
    index_selection_win.resizable(False, False)
    index_selection_win.grab_set()  # force this window on top of all others
    root.wm_withdraw()  # hide root
    index_selection_win.protocol('WM_DELETE_WINDOW', exit_index_window)
    index_selection_win.grid_rowconfigure(0, weight=1)
    index_selection_win.grid_columnconfigure(0, weight=1)

    # index select frame
    index_sel_frame = Frame(index_selection_win, highlightbackground="white", highlightthickness=2, bg="#363636",
                            highlightcolor='white')
    index_sel_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)

    # grid/column configure
    for e_n_f in range(3):
        index_sel_frame.grid_columnconfigure(e_n_f, weight=1)
    for e_n_r in range(5):
        index_sel_frame.grid_rowconfigure(e_n_r, weight=1)

    # create label
    index_label = Label(index_sel_frame, text='Select index method', background='#363636', fg="#3498db",
                        font=(set_font, set_font_size, "bold"))
    index_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

    # variable to be returned
    index_selection_var = ''

    # update variable to ffms
    def update_var_ffms():
        nonlocal index_selection_var
        index_selection_var = 'ffms'
        index_selection_win.destroy()  # exit the window

    # create 'FFMS' button
    ffms_btn = HoverButton(index_sel_frame, text="FFMS", command=update_var_ffms, foreground="white",
                           background="#23272A", borderwidth="3", activeforeground="#3498db",
                           activebackground="#23272A")
    ffms_btn.grid(row=1, column=0, columnspan=3, padx=25, pady=0, sticky=E + W + S)

    # create ffms label
    ffms_label = Label(index_sel_frame, font=(set_fixed_font, set_font_size - 1),
                       text="FFMS supports virtually all formats, however it's not 100% frame accurate. You may "
                            "notice a miss-match frame between the source and encode in some occasions.",
                       background='#363636', fg="white", wraplength=320, justify=CENTER)
    ffms_label.grid(row=2, column=0, columnspan=3, sticky=E + W + N, padx=5, pady=(4, 0))

    # update variable to lwlibav
    def update_var_lwlibav():
        nonlocal index_selection_var
        index_selection_var = 'lwlibav'
        index_selection_win.destroy()  # exit the window

    # create 'LWLibavSource' button
    lwlibavsource_btn = HoverButton(index_sel_frame, text="LWLibavSource", command=update_var_lwlibav,
                                    foreground="white", background="#23272A", borderwidth="3",
                                    activeforeground="#3498db", activebackground="#23272A")
    lwlibavsource_btn.grid(row=3, column=0, columnspan=3, padx=25, pady=0, sticky=E + W + S)

    # create lwlibav label
    lwlibav_label = Label(index_sel_frame, font=(set_fixed_font, set_font_size - 1),
                          text="LWLibavSource (L-Smash) is 100% frame accurate. However, it doesn't have full "
                               "support for some video codecs and containers. If you notice black/grey "
                               "images being generated with a specific source use FFMS. "
                               "If your source is MKV/AVC this is the best option.",
                          background='#363636', fg="white", wraplength=320, justify=CENTER)
    lwlibav_label.grid(row=4, column=0, columnspan=3, sticky=W + N + E, padx=5, pady=(4, 0))

    # create 'Cancel' button
    index_cancel_btn = HoverButton(index_sel_frame, text="Cancel", activeforeground="#3498db", width=8,
                                   command=lambda: [index_selection_win.destroy(), advanced_root_deiconify()],
                                   foreground="white", background="#23272A", borderwidth="3",
                                   activebackground="#23272A")
    index_cancel_btn.grid(row=5, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    # disable/enable indexers depending on known sources
    if source_file_path.get().endswith(".m2ts"):
        ffms_btn.config(state=DISABLED)
        ffms_label.config(text='FFMS disabled for m2ts')
    if str(source_file_information['format']).lower() == 'vc-1':
        lwlibavsource_btn.config(state=DISABLED)
        lwlibav_label.config(text='LwLibavSource disabled for video codec VC-1')

    index_selection_win.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist

    # return index variable
    return index_selection_var


# function to check crop
def check_crop_values():
    # exit the window
    def exit_index_window():
        check_crop_win.destroy()  # close window
        advanced_root_deiconify()  # restore root

    # index selection window
    check_crop_win = Toplevel()
    check_crop_win.title('Check Crop')
    check_crop_win.configure(background="#363636")
    check_crop_win.geometry(f'{350}x{180}+{str(int(root.geometry().split("+")[1]) + 180)}+'
                            f'{str(int(root.geometry().split("+")[2]) + 230)}')
    check_crop_win.resizable(False, False)
    check_crop_win.grab_set()  # force this window on top of all others
    root.wm_withdraw()  # hide root
    check_crop_win.protocol('WM_DELETE_WINDOW', exit_index_window)
    check_crop_win.grid_rowconfigure(0, weight=1)
    check_crop_win.grid_columnconfigure(0, weight=1)

    # index select frame
    check_crop_frame = LabelFrame(check_crop_win, text=' Crop: ', bd=0, bg="#363636", fg="#3498db",
                                  font=(set_font, set_font_size + 1, 'bold'))
    check_crop_frame.grid(column=0, row=0, columnspan=4, sticky=N + S + E + W)

    # grid/column configure
    # for c_c_f in range(4):
    #     check_crop_frame.grid_columnconfigure(c_c_f, weight=1)
    check_crop_frame.grid_columnconfigure(0, weight=1)
    check_crop_frame.grid_columnconfigure(1, weight=1000)
    check_crop_frame.grid_columnconfigure(2, weight=1000)
    check_crop_frame.grid_columnconfigure(3, weight=1)

    for c_cc_f in range(3):
        check_crop_frame.grid_rowconfigure(c_cc_f, weight=1)

    # variable to be returned
    crop_var = {}

    # update variable for crop
    def update_crop_var():
        nonlocal crop_var
        crop_var.update({"crop": {"left": left_entry_box.get().strip(),
                                  "right": right_entry_box.get().strip(),
                                  "top": top_entry_box.get().strip(),
                                  "bottom": bottom_entry_box.get().strip()}})

        # ensure all values are only numbers
        try:
            int(left_entry_box.get().strip())
            int(right_entry_box.get().strip())
            int(top_entry_box.get().strip())
            int(bottom_entry_box.get().strip())
        except ValueError:
            messagebox.showerror(parent=check_crop_win, title='Error', message='Values can only be numbers!\n\n'
                                                                               'If crop is nothing leave this at 0')
            return  # exit the function

        if left_entry_box.get().strip() == '' or left_entry_box.get().strip() == '0':
            dict_left_crop = '0'
        else:
            dict_left_crop = left_entry_box.get().strip()

        if right_entry_box.get().strip() == '' or right_entry_box.get().strip() == '0':
            dict_right_crop = '0'
        else:
            dict_right_crop = right_entry_box.get().strip()

        if top_entry_box.get().strip() == '' or top_entry_box.get().strip() == '0':
            dict_top_crop = '0'
        else:
            dict_top_crop = top_entry_box.get().strip()

        if bottom_entry_box.get().strip() == '' or bottom_entry_box.get().strip() == '0':
            dict_bottom_crop = '0'
        else:
            dict_bottom_crop = bottom_entry_box.get().strip()

        # update dictionary crop info
        source_file_information.update({"crop": {"left": dict_left_crop, "right": dict_right_crop,
                                                 "top": dict_top_crop, "bottom": dict_bottom_crop}})

        check_crop_win.destroy()  # exit the window

    # left crop label
    left_label = Label(check_crop_frame, font=(set_fixed_font, set_font_size - 1), text="Left:",
                       background='#363636', fg="white")
    left_label.grid(row=0, column=0, sticky=W + S, padx=5, pady=(7, 10))

    # left entry box
    left_entry_box = Entry(check_crop_frame, borderwidth=4, bg="#565656", fg='white', width=8,
                           disabledforeground='white', disabledbackground="#565656")
    left_entry_box.grid(row=0, column=1, padx=5, pady=(7, 10), sticky=W + S)

    # right crop label
    right_label = Label(check_crop_frame, font=(set_fixed_font, set_font_size - 1), text="Right:",
                        background='#363636', fg="white")
    right_label.grid(row=0, column=2, sticky=E + S, padx=5, pady=(7, 10))

    # right entry box
    right_entry_box = Entry(check_crop_frame, borderwidth=4, bg="#565656", fg='white', width=8,
                            disabledforeground='white', disabledbackground="#565656")
    right_entry_box.grid(row=0, column=3, padx=5, pady=(7, 10), sticky=E + S)

    # top crop label
    top_label = Label(check_crop_frame, font=(set_fixed_font, set_font_size - 1), text="Top:",
                      background='#363636', fg="white")
    top_label.grid(row=1, column=0, sticky=W + N, padx=5, pady=(16, 0))

    # top entry box
    top_entry_box = Entry(check_crop_frame, borderwidth=4, bg="#565656", fg='white', width=8,
                          disabledforeground='white', disabledbackground="#565656")
    top_entry_box.grid(row=1, column=1, padx=5, pady=(7, 0), sticky=W + N)

    # bottom crop label
    bottom_label = Label(check_crop_frame, font=(set_fixed_font, set_font_size - 1), text="Bottom:",
                         background='#363636', fg="white")
    bottom_label.grid(row=1, column=2, sticky=E + N, padx=5, pady=(16, 0))

    # bottom entry box
    bottom_entry_box = Entry(check_crop_frame, borderwidth=4, bg="#565656", fg='white', width=8,
                             disabledforeground='white', disabledbackground="#565656")
    bottom_entry_box.grid(row=1, column=3, padx=5, pady=(7, 0), sticky=E + N)

    # create button frame
    crop_btn_frame = Frame(check_crop_frame, bg="#363636")
    crop_btn_frame.grid(column=0, row=2, columnspan=4, sticky=N + S + E + W)
    for c_b_f in range(3):
        crop_btn_frame.grid_columnconfigure(c_b_f, weight=1)
    crop_btn_frame.grid_rowconfigure(0, weight=1)

    # create 'Cancel' button
    crop_cancel_btn = HoverButton(crop_btn_frame, text="Cancel", activeforeground="#3498db", width=8,
                                  command=lambda: [check_crop_win.destroy(), advanced_root_deiconify()],
                                  foreground="white", background="#23272A", borderwidth="3",
                                  activebackground="#23272A")
    crop_cancel_btn.grid(row=0, column=0, padx=7, pady=5, sticky=S + W)

    # create 'view script' button
    view_script = HoverButton(crop_btn_frame, text="View Script", activeforeground="#3498db", width=8,
                              command=lambda: os.startfile(pathlib.Path(input_script_path.get())),
                              foreground="white", background="#23272A", borderwidth="3",
                              activebackground="#23272A")
    view_script.grid(row=0, column=1, padx=7, pady=5, sticky=W + E + S)

    # create 'Accept' button
    accept_btn = HoverButton(crop_btn_frame, text="Accept", activeforeground="#3498db", width=8,
                             command=update_crop_var, foreground="white", background="#23272A", borderwidth="3",
                             activebackground="#23272A")
    accept_btn.grid(row=0, column=2, padx=7, pady=5, sticky=S + E)

    # update all the crop values to be displayed in the window
    if source_file_information['crop'] != 'None':
        # left crop
        if source_file_information['crop']['left'] == '':
            left_entry_box.insert(0, '0')
        else:
            left_entry_box.insert(0, source_file_information['crop']['left'])
        # right crop
        if source_file_information['crop']['right'] == '':
            right_entry_box.insert(0, '0')
        else:
            right_entry_box.insert(0, source_file_information['crop']['right'])
        # top crop
        if source_file_information['crop']['top'] == '':
            top_entry_box.insert(0, '0')
        else:
            top_entry_box.insert(0, source_file_information['crop']['top'])
        # bottom crop
        if source_file_information['crop']['bottom'] == '':
            bottom_entry_box.insert(0, '0')
        else:
            bottom_entry_box.insert(0, source_file_information['crop']['bottom'])

    # if there was no crop fill the window with 0's
    else:
        left_entry_box.insert(0, '0')
        right_entry_box.insert(0, '0')
        top_entry_box.insert(0, '0')
        bottom_entry_box.insert(0, '0')

    check_crop_win.wait_window()  # wait for window to be closed

    # return index variable
    return crop_var


# auto screenshot status window
def auto_screen_shot_status_window():
    # select desired amount of screenshots
    screen_amount_check = screen_shot_count_spinbox()

    if screen_amount_check == '':
        return  # exit this function

    # check crop
    checking_crop = check_crop_values()

    if not checking_crop:
        return  # exit this function

    # choose indexer
    get_indexer = choose_indexer_func()

    if get_indexer == '':
        return  # exit this function

    # screenshot status window
    screenshot_status_window = Toplevel()
    screenshot_status_window.configure(background="#363636")
    screenshot_status_window.title('')
    screenshot_status_window.geometry(f'{500}x{400}+{str(int(root.geometry().split("+")[1]) + 126)}+'
                                      f'{str(int(root.geometry().split("+")[2]) + 230)}')
    screenshot_status_window.resizable(False, False)
    root.wm_withdraw()  # hide root
    screenshot_status_window.grid_rowconfigure(0, weight=1)
    screenshot_status_window.grid_columnconfigure(0, weight=1)

    # screenshot output frame
    ss_output_frame = Frame(screenshot_status_window, highlightbackground="white", highlightthickness=2,
                            bg="#363636", highlightcolor='white')
    ss_output_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        ss_output_frame.grid_columnconfigure(e_n_f, weight=1)
        ss_output_frame.grid_rowconfigure(e_n_f, weight=1)

    # create scrolled text widget
    ss_status_info = scrolledtextwidget.ScrolledText(ss_output_frame, height=18, bg='#565656', fg='white', bd=4,
                                                     wrap=WORD)
    ss_status_info.grid(row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W)
    ss_status_info.config(state=DISABLED)

    force_cancel = False

    # function to exit the status window
    def screenshot_close_button():
        nonlocal force_cancel
        check_exit = messagebox.askyesno(parent=screenshot_status_window, title='Close?',
                                         message='Closing this window will kill the entire program. This is the only '
                                                 'way to ensure all threads are safely destroyed.\n\nWould you like '
                                                 'to exit?')
        if check_exit:
            force_cancel = True
            # kill root (fully destroy root to close all threads)
            root.destroy()

    # create 'Close' button
    ss_close_btn = HoverButton(ss_output_frame, text="Close", command=screenshot_close_button,
                               foreground="white", background="#23272A", borderwidth="3",
                               activeforeground="#3498db", width=8, activebackground="#23272A")
    ss_close_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=E)
    screenshot_status_window.protocol('WM_DELETE_WINDOW', screenshot_close_button)

    # image comparison code (semi automatic)
    def semi_automatic_screenshots():
        # define config parser
        semi_auto_img_parser = ConfigParser()
        semi_auto_img_parser.read(config_file)

        # define vs core
        core = vs.core

        # load needed plugins
        try:
            core.std.LoadPlugin("Runtime/Apps/image_comparison/SubText.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("Runtime/Apps/image_comparison/libimwri.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("Runtime/Apps/image_comparison/libvslsmashsource.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("Runtime/Apps/image_comparison/libfpng.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("Runtime/Apps/image_comparison/ffms2.dll")
        except vs.Error:
            pass

        # define variable to update within function for ffms
        ffms_final_source_path = ''
        ffms_cache_path = ''

        # function to index source file
        def index_source_file_func():
            nonlocal ffms_final_source_path, ffms_cache_path
            # index the source file with lwlibavsource
            if get_indexer == 'lwlibav':
                # if index file already exists
                if pathlib.Path(source_file_path.get() + '.lwi').is_file():
                    src_use_existing = messagebox.askyesno(parent=screenshot_status_window, title='Indexing: Source',
                                                           message='Source index file already exists. '
                                                                   'Would you like to use existing index file?')
                    # if user does not want to use existing index file
                    if not src_use_existing:
                        # delete index
                        pathlib.Path(source_file_path.get() + '.lwi').unlink(missing_ok=True)
                        # create new index
                        core.lsmas.LWLibavSource(source_file_path.get())
                # if index does not exist create index file
                else:
                    core.lsmas.LWLibavSource(source_file_path.get())

            # index the source file with ffms
            elif get_indexer == 'ffms':
                # if index file already exists on same path as the source
                if pathlib.Path(source_file_path.get() + '.ffindex').is_file():
                    # ask user if they want to use the index
                    src_use_existing = messagebox.askyesno(parent=screenshot_status_window, title='Indexing: Source',
                                                           message='Source index file already exists. '
                                                                   'Would you like to use existing index file?')
                    # if user does not want to use existing index file
                    if not src_use_existing:
                        # delete index
                        pathlib.Path(source_file_path.get() + '.ffindex').unlink(missing_ok=True)
                        # create new index
                        core.ffms2.Source(source_file_path.get())
                        # update variable
                        ffms_final_source_path = source_file_path.get()
                    # if user wants to use existing index
                    elif src_use_existing:
                        ffms_final_source_path = pathlib.Path(source_file_path.get())

                # check for staxrip ffindex file in temp folder
                elif pathlib.Path(str(pathlib.Path(source_file_path.get()).with_suffix('')) + '_temp/'
                                  ).is_dir() and pathlib.Path(str(pathlib.Path(source_file_path.get()).with_suffix('')
                                                                  ) + '_temp/temp.ffindex').is_file():
                    # ask user if they want to use the index
                    src_use_existing = messagebox.askyesno(parent=screenshot_status_window,
                                                           title='Indexing: Source',
                                                           message='Source index file already exists. '
                                                                   'Would you like to use existing index file?')
                    # if user does not want to use existing index file
                    if not src_use_existing:
                        # create new index
                        core.ffms2.Source(source=source_file_path.get())
                        # update variable
                        ffms_final_source_path = pathlib.Path(source_file_path.get())
                    # if user wants to use existing index
                    elif src_use_existing:
                        ffms_final_source_path = pathlib.Path(source_file_path.get())
                        ffms_cache_path = pathlib.Path(str(pathlib.Path(
                            source_file_path.get()).with_suffix('')) + '_temp/temp.ffindex')

                # if index does not exist create index file beside the source file and update variable
                else:
                    core.ffms2.Source(source=source_file_path.get())
                    ffms_final_source_path = pathlib.Path(source_file_path.get())

            # update status window
            ss_status_info.config(state=NORMAL)
            ss_status_info.insert(END, "\nSource index completed!\n\n")
            ss_status_info.see(END)
            ss_status_info.config(state=DISABLED)

        # function to index encode file
        def index_encode_file_func():
            # index the source file with lwlibavsource
            if get_indexer == 'lwlibav':
                # if index file already exists
                if pathlib.Path(encode_file_path.get() + '.lwi').is_file():
                    enc_use_existing = messagebox.askyesno(parent=screenshot_status_window, title='Indexing: Encode',
                                                           message='Encode index file already exists. '
                                                                   'Would you like to use existing index file?')
                    # if user does not want to use existing index file
                    if not enc_use_existing:
                        # delete index
                        pathlib.Path(encode_file_path.get() + '.lwi').unlink(missing_ok=True)
                        # create new index
                        core.lsmas.LWLibavSource(encode_file_path.get())
                # if index does not exist create index file
                else:
                    core.lsmas.LWLibavSource(encode_file_path.get())

            # index the source file with ffms
            elif get_indexer == 'ffms':
                # if index file already exists
                if pathlib.Path(encode_file_path.get() + '.ffindex').is_file():
                    enc_use_existing = messagebox.askyesno(parent=screenshot_status_window, title='Indexing: Encode',
                                                           message='Encode index file already exists. '
                                                                   'Would you like to use existing index file?')
                    # if user does not want to use existing index file
                    if not enc_use_existing:
                        # delete index
                        pathlib.Path(encode_file_path.get() + '.ffindex').unlink(missing_ok=True)
                        # create new index
                        core.ffms2.Source(encode_file_path.get())
                # if index does not exist create index file
                else:
                    core.ffms2.Source(encode_file_path.get())

            # update status window
            ss_status_info.config(state=NORMAL)
            ss_status_info.insert(END, "\nEncode index completed!\n\n")
            ss_status_info.see(END)
            ss_status_info.config(state=DISABLED)

        # update status window
        ss_status_info.config(state=NORMAL)
        ss_status_info.insert(END, f"Indexing {str(pathlib.Path(source_file_path.get()).name)} and  "
                                   f"{str(pathlib.Path(encode_file_path.get()).name)} with {get_indexer}. "
                                   f"This could take a while depending on your systems storage speed...\n\n")
        ss_status_info.see(END)
        ss_status_info.config(state=DISABLED)

        # run index functions
        # if files are on separate drives execute them both at the same time
        if pathlib.Path(source_file_path.get()).drive != pathlib.Path(encode_file_path.get()).drive:
            # define threads
            t1 = threading.Thread(target=index_source_file_func)
            t2 = threading.Thread(target=index_encode_file_func)

            # start threads
            t1.start()
            t2.start()

            # wait for threads to finish
            t1.join()
            t2.join()

        # if files are on the same drive execute them 1 at a time
        else:
            index_source_file_func()
            index_encode_file_func()

        # define source and encode file index files as variables
        if get_indexer == 'lwlibav':
            source_file = core.lsmas.LWLibavSource(source_file_path.get())
            encode_file = core.lsmas.LWLibavSource(encode_file_path.get())
        elif get_indexer == 'ffms':
            # try to load index file
            try:
                if ffms_cache_path != '':
                    source_file = core.ffms2.Source(source=ffms_final_source_path, cachefile=ffms_cache_path)
                else:
                    source_file = core.ffms2.Source(source=ffms_final_source_path)
            # if index file is a different version than the included ffms
            except vs.Error:
                # update status window with error
                ss_status_info.config(state=NORMAL)
                ss_status_info.insert(END, '\nFailed to open existing source index.\nIndexing source file now with '
                                           'included FFMS. Please wait...')
                ss_status_info.see(END)
                ss_status_info.config(state=DISABLED)

                # index source file
                source_file = core.ffms2.Source(source=source_file_path.get())

                # update status window
                ss_status_info.config(state=NORMAL)
                ss_status_info.insert(END, 'Done!\n\n')
                ss_status_info.see(END)
                ss_status_info.config(state=DISABLED)

            # encode file variable
            encode_file = core.ffms2.Source(encode_file_path.get())

        # get the total number of frames from source file
        num_source_frames = len(source_file)

        # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic,
        # Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL,
        # MarginR, MarginV,

        # set subtitle scale style
        selected_sub_style = "Segoe UI,16,&H000ac7f5,&H00000000,&H00000000,&H00000000," \
                             "1,0,0,0,100,100,0,0,1,1,0,7,5,0,0,1"

        # check for custom user image amount
        if semi_auto_img_parser['screenshot_settings']['semi_auto_count'] != '':
            comparison_img_count = int(semi_auto_img_parser['screenshot_settings']['semi_auto_count'])
        else:
            comparison_img_count = 20

        # update status window
        ss_status_info.config(state=NORMAL)
        ss_status_info.insert(END, f"Collecting {str(comparison_img_count)} random 'B' frames to generate "
                                   "comparison images from...")
        ss_status_info.see(END)
        ss_status_info.config(state=DISABLED)

        # collect a range of random b frames from encode and put them in a list
        b_frames = []
        while len(b_frames) < int(comparison_img_count):
            random_frame = random.randint(5000, num_source_frames - 10000)
            if encode_file.get_frame(random_frame).props['_PictType'].decode() == 'B':
                b_frames.append(random_frame)

        # update status window
        ss_status_info.config(state=NORMAL)
        ss_status_info.insert(END, f" Completed!\n\nGenerating {str(comparison_img_count)} sets of comparisons... "
                                   f"This depends on system storage speed...")
        ss_status_info.see(END)
        ss_status_info.config(state=DISABLED)

        # make temporary image folder
        image_output_dir = pathlib.Path(pathlib.Path(
            encode_file_path.get()).parent / f"{pathlib.Path(encode_file_path.get()).stem}_images")

        # check if temp image dir exists, if so delete it!
        if image_output_dir.exists():
            shutil.rmtree(image_output_dir, ignore_errors=True)

        # create main image dir
        image_output_dir.mkdir(exist_ok=True)

        # create comparison image directory and define it as variable
        pathlib.Path(pathlib.Path(image_output_dir) / "img_comparison").mkdir(exist_ok=True)
        screenshot_comparison_var.set(str(pathlib.Path(pathlib.Path(image_output_dir) / "img_comparison")))

        # create selected image directory and define it as variable
        pathlib.Path(pathlib.Path(image_output_dir) / "img_selected").mkdir(exist_ok=True)
        screenshot_selected_var.set(str(pathlib.Path(pathlib.Path(image_output_dir) / "img_selected")))

        # crop
        if str(source_file_information['crop']) != 'None':
            source_file = core.std.Crop(source_file,
                                        left=int(source_file_information['crop']['left']),
                                        right=int(source_file_information['crop']['right']),
                                        top=int(source_file_information['crop']['top']),
                                        bottom=int(source_file_information['crop']['bottom']))

        # if resolutions are not the same, resize the source to match encode resolution
        if source_file.width != encode_file.width and source_file.height != encode_file.height:
            source_file = core.resize.Spline36(source_file, width=int(encode_file.width),
                                               height=int(encode_file.height), dither_type="error_diffusion")

        # hdr tone-map
        if source_file_information['hdr'] == 'True':
            source_file = awsmfunc.DynamicTonemap(clip=source_file)
            encode_file = awsmfunc.DynamicTonemap(clip=encode_file)

        # define the subtitle/frame info for source and encode
        vs_source_info = core.sub.Subtitle(clip=source_file, text='Source', style=selected_sub_style)
        vs_encode_info = awsmfunc.FrameInfo(clip=encode_file, title='BHDStudio', style=selected_sub_style)

        # generate comparisons
        awsmfunc.ScreenGen([vs_source_info, vs_encode_info], frame_numbers=b_frames, fpng_compression=2,
                           folder=screenshot_comparison_var.get(), suffix=["a_source__%d", "b_encode__%d"])

        # close status window
        screenshot_status_window.destroy()  # close screenshot status window

    # multithread the image comparison code and start the function
    auto_ss_thread = threading.Thread(target=semi_automatic_screenshots, daemon=True)

    # start thread
    auto_ss_thread.start()

    # wait on screenshot status to close
    screenshot_status_window.wait_window()

    if not force_cancel:
        # open image viewer
        automatic_screenshot_generator()


# auto generate button
auto_screens_multi_btn = HoverButton(image_btn_frame, text="Generate IMGs", command=auto_screen_shot_status_window,
                                     foreground="white", background="#23272A", borderwidth="3", state=DISABLED,
                                     activeforeground="#3498db", activebackground="#23272A", width=12)
auto_screens_multi_btn.grid(row=1, column=0, rowspan=2, padx=5, pady=(7, 7), sticky=S + W)


# upload pictures to beyond.co and return medium linked images
def upload_to_beyond_hd_co_window():
    # define upload error variable
    upload_error = BooleanVar()

    # function to manipulate scrolled text box to reduce code
    def manipulate_ss_upload_window(update_string):
        try:
            upload_ss_info.config(state=NORMAL)
            upload_ss_info.delete("1.0", END)
            upload_ss_info.insert(END, update_string)
            upload_ss_info.config(state=DISABLED)
        except TclError:
            return  # exit the function

    # function to upload to beyond hd
    def upload_to_beyond_hd_co():
        # if user and pass bin exists
        if pathlib.Path('Runtime/user.bin').is_file() and pathlib.Path('Runtime/pass.bin').is_file():

            # start fernet instance to convert stored username and password files
            pass_user_decoder = Fernet(crypto_key)

            # open both user and pass bin files
            with open('Runtime/user.bin', 'rb') as user_file, open('Runtime/pass.bin', 'rb') as pass_file:
                # decode and insert user name
                decode_user = pass_user_decoder.decrypt(user_file.read()).decode('utf-8')
                # decode and insert password
                decode_pass = pass_user_decoder.decrypt(pass_file.read()).decode('utf-8')

            # if username or password equals nothing send error
            if decode_user == '' or decode_pass == '':
                missing_info = messagebox.askyesno(parent=upload_ss_status, title='Missing credentials',
                                                   message='Missing user name and password for beyondhd.co\n\nWould '
                                                           'you like to add these now?')
                # if user selects yes
                if missing_info:
                    # open login window
                    bhd_co_login_window()
                    # update login variables
                    pass_user_decoder = Fernet(crypto_key)
                    with open('Runtime/user.bin', 'rb') as user_file, open('Runtime/pass.bin', 'rb') as pass_file:
                        decode_user = pass_user_decoder.decrypt(user_file.read()).decode('utf-8')
                        decode_pass = pass_user_decoder.decrypt(pass_file.read()).decode('utf-8')
                else:  # if user selects no
                    manipulate_ss_upload_window('Missing username and/or password. Cannot continue...')
                    return  # exit function
        else:  # if user or path bins do not exist
            missing_info = messagebox.askyesno(parent=upload_ss_status, title='Missing credentials',
                                               message='Missing user name and password for beyondhd.co\n\nWould you '
                                                       'like to add these now?')
            # if user selects yes
            if missing_info:
                # open login window
                bhd_co_login_window()
                # update login variables
                pass_user_decoder = Fernet(crypto_key)
                with open('Runtime/user.bin', 'rb') as user_file, open('Runtime/pass.bin', 'rb') as pass_file:
                    decode_user = pass_user_decoder.decrypt(user_file.read()).decode('utf-8')
                    decode_pass = pass_user_decoder.decrypt(pass_file.read()).decode('utf-8')
            else:  # if user selects no
                manipulate_ss_upload_window('Missing username and/or password. Cannot continue...')
                return  # exit function

        # create empty list
        list_of_pngs = []

        # use regex to get only the filename
        for loaded_images in image_listbox.get(0, END):
            img = re.search(r"[\d{1,3}]\)\s(.+)", loaded_images)
            list_of_pngs.append(str(pathlib.Path(img.group(1))))

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # login to beyondhd image host
        # start requests session
        session = requests.session()

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # get raw text of web page
        manipulate_ss_upload_window("Getting auth token from beyondhd.co")
        try:
            auth_raw = session.get("https://beyondhd.co/login", timeout=10).text
        except requests.exceptions.ConnectionError:
            manipulate_ss_upload_window("No internet connection")
            return  # exit the function

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # if web page didn't return a response
        if not auth_raw:
            manipulate_ss_upload_window("Could not access beyondhd.co")
            return  # exit the function

        # split auth token out of raw web page for later use
        auth_code = auth_raw.split('PF.obj.config.auth_token = ')[1].split(';')[0].replace('"', '')
        manipulate_ss_upload_window("Auth token found")
        if not auth_code:
            manipulate_ss_upload_window("Could not find auth token")
            return  # exit the function

        # login payload
        login_payload = {'login-subject': decode_user, 'password': decode_pass, 'auth_token': auth_code}

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # login post
        manipulate_ss_upload_window(f"Logging in to beyondhd.co as {login_payload['login-subject']}")
        try:
            login_post = session.post("https://beyondhd.co/login", data=login_payload, timeout=10)
        except requests.exceptions.ConnectionError:
            manipulate_ss_upload_window("No internet connection")
            return  # exit the function

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # find user info from login post
        confirm_login = re.search(r"CHV.obj.logged_user =(.+);", login_post.text, re.MULTILINE)
        manipulate_ss_upload_window(f"Successfully logged in as {decode_user}")

        # if post confirm_login is none
        if not confirm_login:
            manipulate_ss_upload_window("Incorrect username or password")
            return  # exit the function

        # generate album name
        # use regex to find the movie name
        movie_name = re.finditer(r'\d{4}(?!p)', pathlib.Path(encode_file_path.get()).stem, re.IGNORECASE)
        movie_name_extraction = []  # create empty list
        for match in movie_name:  # get the "span" from the movie name
            movie_name_extraction.append(match.span())
        # extract the full movie name (removing anything that is not needed from the filename)
        try:
            full_movie_name = pathlib.Path(encode_file_path.get()).stem[0:int(
                movie_name_extraction[-1][-1])].replace('.', ' ').strip()
            generated_album_name = f"{encode_file_resolution.get()} | {full_movie_name}"
        # if for some reason there is an index error just generate a generic album name based off of the encoded input
        except IndexError:
            generated_album_name = str(pathlib.Path(pathlib.Path(encode_file_path.get()).name).with_suffix(''))

        # create album payload
        album_payload = {'auth_token': auth_code, 'action': 'create-album', 'type': 'album',
                         'album[name]': generated_album_name, 'album[description]': main_root_title,
                         'album[password]': '', 'album[new]': 'true'}

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # create album post
        manipulate_ss_upload_window(f"Creating album:\n{generated_album_name}")
        try:
            album_post = session.post("https://beyondhd.co/json", data=album_payload, timeout=10)
        except requests.exceptions.ConnectionError:
            manipulate_ss_upload_window("No internet connection")
            return  # exit the function
        manipulate_ss_upload_window(f"{generated_album_name} album was created")

        # check for success message
        if not album_post.json()['success']['message'] == "Content added to album":
            manipulate_ss_upload_window(album_post.json()['success']['message'])
            return  # exit the function

        # get album_id for later use
        posted_album_id = album_post.json()['album']['id_encoded']

        # upload files to new album with the album id
        upload_files_payload = {'type': 'file', 'action': 'upload', 'auth_token': auth_code, 'nsfw': 0,
                                'album_id': posted_album_id}

        # create empty list to convert png to bytes
        bytes_converter_png_list = []

        # convert list of png files to bytes and append them to the above list
        for png_file in list_of_pngs:
            with open(str(png_file), 'rb') as f:
                bytes_converter_png_list.append({'source': (str(pathlib.Path(png_file).name), f.read())})

        # get length of list
        images_len = len(bytes_converter_png_list)

        # set empty string to update
        description_info = ''

        # clear screenshot info window
        manipulate_ss_upload_window('')

        # upload image 1 at a time
        for (png_num, current_image) in enumerate(bytes_converter_png_list, start=1):
            if not upload_error.get():
                upload_ss_info.config(state=NORMAL)
                upload_ss_info.insert(END, f'Uploading image {png_num}/{images_len}\n')
                upload_ss_info.see(END)
                upload_ss_info.config(state=DISABLED)
                # upload files
                try:
                    upload_file_post = session.post("https://beyondhd.co/json", files=current_image,
                                                    data=upload_files_payload)
                except requests.exceptions.ConnectionError:  # if there is a connection error show an error
                    manipulate_ss_upload_window('Upload connection error')
                    upload_error.set(True)  # set error to True
                    return  # exit the function

                # if upload file returns an 'ok' status
                if upload_file_post.ok:
                    # add uploaded image and returned url to description info string
                    description_info += f"[url={upload_file_post.json()['image']['url_viewer']}]" \
                                        f"[img]{upload_file_post.json()['image']['medium']['url']}[/img][/url]\n"

                    # upload status was a success
                    if upload_file_post.json()['success']['message'] != 'image uploaded':
                        upload_error.set(True)  # set error to True

                else:
                    upload_error.set(True)  # set error to True
                    manipulate_ss_upload_window(f"Error code from beyondhd.co {str(upload_file_post.status_code)}")
                    return  # exit the function

        # if images are uploaded/returned, change tabs to 'URLs' and insert the image description string
        if not upload_error.get():
            # clear screenshot box
            screenshot_scrolledtext.delete("1.0", END)
            # add description string to screenshot box
            screenshot_scrolledtext.insert(END, description_info)
            tabs.select(url_tab)  # swap tab
            # add success message to upload status window
            manipulate_ss_upload_window(f'Upload is successful!\n\nImages are upload to album:\n'
                                        f'{generated_album_name}\n\nClick OK to continue')

    # function to exit the screenshot upload window
    def upload_ss_exit_func():
        upload_error.set(True)  # exit function at next chance
        upload_ss_status.destroy()  # close window
        advanced_root_deiconify()  # re-open root window

    # upload status window
    upload_ss_status = Toplevel()
    upload_ss_status.configure(background="#363636")
    upload_ss_status.title('Upload Status')
    upload_ss_status.geometry(f'{460}x{240}+{str(int(root.geometry().split("+")[1]) + 138)}+'
                              f'{str(int(root.geometry().split("+")[2]) + 230)}')
    upload_ss_status.resizable(False, False)
    upload_ss_status.grab_set()  # force this window on top
    upload_ss_status.wm_protocol('WM_DELETE_WINDOW', upload_ss_exit_func)
    root.wm_withdraw()  # hide root
    upload_ss_status.grid_rowconfigure(0, weight=1)
    upload_ss_status.grid_columnconfigure(0, weight=1)

    # encoder name frame
    upload_ss_frame = Frame(upload_ss_status, highlightbackground="white", highlightthickness=2,
                            bg="#363636", highlightcolor='white')
    upload_ss_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        upload_ss_frame.grid_columnconfigure(e_n_f, weight=1)
        upload_ss_frame.grid_rowconfigure(e_n_f, weight=1)

    # create scrolled window
    upload_ss_info = scrolledtextwidget.ScrolledText(upload_ss_frame, height=9, bg='#565656', state=DISABLED,
                                                     fg='white', bd=4, wrap=WORD)
    upload_ss_info.grid(row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W)

    # create 'OK' button
    ss_okay_btn = HoverButton(upload_ss_frame, text="OK", command=upload_ss_exit_func,
                              foreground="white", background="#23272A", borderwidth="3",
                              activeforeground="#3498db", width=8, activebackground="#23272A")
    ss_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=E)

    # ensure error is set to False
    upload_error.set(False)

    # start upload in another thread
    threading.Thread(target=upload_to_beyond_hd_co).start()


# upload button
upload_ss_button = HoverButton(image_btn_frame, text="Upload IMGs", state=DISABLED,
                               command=upload_to_beyond_hd_co_window,
                               foreground="white", background="#23272A", borderwidth="3",
                               activeforeground="#3498db", activebackground="#23272A", width=12)
upload_ss_button.grid(row=1, column=1, rowspan=2, padx=5, pady=(7, 7), sticky=S + E)

# screen shot url tab
url_tab = Frame(tabs, background='#434547')
tabs.add(url_tab, text=' URLs ')
url_tab.grid_rowconfigure(0, weight=1)
url_tab.grid_columnconfigure(0, weight=20)
url_tab.grid_columnconfigure(1, weight=20)
url_tab.grid_columnconfigure(2, weight=20)
url_tab.grid_columnconfigure(3, weight=1)

# screenshot textbox
screenshot_scrolledtext = scrolledtextwidget.ScrolledText(url_tab, height=6, bg='#565656', fg='white', bd=4)
screenshot_scrolledtext.grid(row=0, column=0, columnspan=3, pady=(6, 6), padx=4, sticky=E + W)

# clear screenshot box
reset_screenshot_box = HoverButton(url_tab, text="X", activebackground="#23272A",
                                   command=lambda: screenshot_scrolledtext.delete('1.0', END), foreground="white",
                                   background="#23272A", borderwidth="3", activeforeground="#3498db", width=4)
reset_screenshot_box.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + E + W)


def popup_auto_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
    screen_shot_right_click_menu.tk_popup(e.x_root, e.y_root)  # This gets the position of 'e'


# pop up menu to enable/disable manual edits in release notes
screen_shot_right_click_menu = Menu(release_notes_scrolled, tearoff=False, font=(set_font, set_font_size + 1),
                                    background="#23272A", foreground="white",
                                    activebackground="grey")  # Right click menu


# right click menu cut
def text_cut():
    if screenshot_scrolledtext.selection_get():
        # Grab selected text from text box
        selected_text_cut = screenshot_scrolledtext.selection_get()
        # Delete Selected Text from text box
        screenshot_scrolledtext.delete("sel.first", "sel.last")
        # Clear the clipboard then append
        screenshot_scrolledtext.clipboard_clear()
        screenshot_scrolledtext.clipboard_append(selected_text_cut)


screen_shot_right_click_menu.add_command(label='Cut', command=text_cut)


# right click menu copy
def text_copy():
    if screenshot_scrolledtext.selection_get():
        # Grab selected text from text box
        selected_text_copy = screenshot_scrolledtext.selection_get()
        # Clear the clipboard then append
        screenshot_scrolledtext.clipboard_clear()
        screenshot_scrolledtext.clipboard_append(selected_text_copy)


screen_shot_right_click_menu.add_command(label='Copy', command=text_copy)


# right click menu paste
def text_paste():
    screenshot_scrolledtext.delete("1.0", END)
    screenshot_scrolledtext.insert(END, screenshot_scrolledtext.clipboard_get())


screen_shot_right_click_menu.add_command(label='Paste', command=text_paste)


# right click menu clear
def text_delete():
    screenshot_scrolledtext.delete("1.0", END)


screen_shot_right_click_menu.add_command(label='Clear', command=text_delete)

screenshot_scrolledtext.bind('<Button-3>', popup_auto_e_b_menu)  # Uses mouse button 3 (right click) to open


# check/return screenshots
def parse_screen_shots():
    # if screenshot textbox is not empty
    if screenshot_scrolledtext.compare("end-1c", "!=", "1.0"):
        new_screenshots = screenshot_scrolledtext.get(1.0, END).split('[/url]')
        fresh_list = [str(i).strip() for i in new_screenshots]
        if '' in fresh_list:
            fresh_list.remove('')

        if int(len(fresh_list)) % 2 == 0:
            sorted_screenshots = ''
            iterate_list = iter(fresh_list)
            for x in iterate_list:
                sorted_screenshots += x + '[/url]'
                sorted_screenshots += "  "
                sorted_screenshots += str(next(iterate_list)) + '[/url]'
                sorted_screenshots += "\n"
                sorted_screenshots += "\n"
            return sorted_screenshots
        else:
            return False


# manual workflow frame
manual_workflow = LabelFrame(root, text=' Manual Workflow ', labelanchor="nw")
manual_workflow.grid(column=0, row=4, columnspan=2, padx=5, pady=(5, 3), sticky=W)
manual_workflow.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
manual_workflow.grid_rowconfigure(0, weight=1)
manual_workflow.grid_columnconfigure(0, weight=1)
manual_workflow.grid_columnconfigure(1, weight=1)
manual_workflow.grid_columnconfigure(2, weight=1)


# generate nfo
def open_nfo_viewer():
    global nfo_pad, nfo_pad_text_box, nfo

    # nfo pad parser
    nfo_pad_parser = ConfigParser()
    nfo_pad_parser.read(config_file)

    if not pathlib.Path(source_file_path.get()).is_file():
        messagebox.showerror(parent=root, title='Error!', message='Source file is missing!')
        return
    if not pathlib.Path(encode_file_path.get()).is_file():
        messagebox.showerror(parent=root, title='Error!', message='Encode file is missing!')
        return
    parse_screenshots = parse_screen_shots()
    if not parse_screenshots:
        messagebox.showerror(parent=root, title='Error!', message='Missing or incorrectly formatted screenshots\n\n'
                                                                  'Screen shots need to be in multiples of 2')
        return

    # nfo formatter
    def run_nfo_formatter():
        # noinspection SpellCheckingInspection
        nfo_b64 = """
        W2NvbG9yPSNmNWM3MGFdUkVMRUFTRSBJTkZPWy9jb2xvcl0KClNvdXJjZSAgICAgICAgICAgICAgICAgIDoge2JsdXJheV9zb3VyY2V9IChUaG
        Fua3MhKQpDaGFwdGVycyAgICAgICAgICAgICAgICA6IHtjaGFwdGVyX3R5cGV9CkZpbGUgU2l6ZSAgICAgICAgICAgICAgIDoge2VuY29kZV9ma
        WxlX3NpemV9CkR1cmF0aW9uICAgICAgICAgICAgICAgIDoge2VuY29kZV9maWxlX2R1cmF0aW9ufQpWaWRlbyAgICAgICAgICAgICAgICAgICA6
        IHtjb250YWluZXJfZm9ybWF0fSB7dl9jb2RlY30gVmlkZW8gLyB7dl9iaXRyYXRlfSBrYnBzIC8ge3ZfZnBzfSAvIHt2X2Zvcm1hdF9wcm9maWx
        lfQpSZXNvbHV0aW9uICAgICAgICAgICAgICA6IHt2X3dpZHRofSB4IHt2X2hlaWdodH0gKHt2X2FzcGVjdF9yYXRpb30pCkF1ZGlvICAgICAgIC
        AgICAgICAgICAgIDoge2FfbG5nfSAvIHthX2NvbW1lcmNpYWx9IEF1ZGlvIC8ge2FfY2hubF9zfSAvIHthX2ZyZXF9IC8ge2FfYml0cmF0ZX0ga
        2JwcyB7b3B0aW9uYWxfc3ViX3N0cmluZ30KRW5jb2RlciAgICAgICAgICAgICAgICAgOiBbY29sb3I9I2Y1YzcwYV17ZW5jb2RlZF9ieX1bL2Nv
        bG9yXQoKW2NvbG9yPSNmNWM3MGFdUkVMRUFTRSBOT1RFU1svY29sb3JdCgp7bmZvX3JlbGVhc2Vfbm90ZXN9CgpbY29sb3I9I2Y1YzcwYV1TQ1J
        FRU5TSE9UU1svY29sb3JdCltjZW50ZXJdCltjb2xvcj0jZjVjNzBhXVNPVVJDRVsvY29sb3JdPDw8PDw8PDw8PDw8PDw8PDwtLS0tLS0tLS0tLS
        0tLS0tLS0tW2NvbG9yPSNmNWM3MGFdVlNbL2NvbG9yXS0tLS0tLS0tLS0tLS0tLS0tLS0+Pj4+Pj4+Pj4+Pj4+Pj4+Pltjb2xvcj0jZjVjNzBhX
        UVOQ09ERVsvY29sb3JdCntuZm9fc2NyZWVuX3Nob3RzfQpbL2NlbnRlcl0KW2NvbG9yPSNmNWM3MGFdR1JFRVRaWy9jb2xvcl0KCkFsbCB0aG9z
        ZSB3aG8gc3VwcG9ydCBvdXIgZ3JvdXAsIG91ciBlbmNvZGVycywgYW5kIG91ciBjb21tdW5pdHkuIAoKW2NvbG9yPSNmNWM3MGFdR1JPVVAgTk9
        URVNbL2NvbG9yXQoKRW5qb3khCgpXZSBhcmUgY3VycmVudGx5IGxvb2tpbmcgZm9yIG5vdGhpbmcgaW4gcGFydGljdWxhci4gSWYgeW91IGZlZW
        wgeW91IGhhdmUgc29tZXRoaW5nIHRvIG9mZmVyLCBjb250YWN0IHVzIQoKW2NlbnRlcl1baW1nXWh0dHBzOi8vYmV5b25kaGQuY28vaW1hZ2VzL
        zIwMjEvMDMvMzAvNjJiY2E4ZDU4N2I3MTczMTIxMDA4ODg3ZWJlMDVhNDIucG5nWy9pbWddWy9jZW50ZXJdCgo=
        """

        decoded_nfo = base64.b64decode(nfo_b64).decode("utf-8")

        # parse encoded file
        media_info_encode = MediaInfo.parse(pathlib.Path(encode_file_path.get()))
        encode_general_track = media_info_encode.general_tracks[0]
        encode_chapter = media_info_encode.menu_tracks[0].to_data()
        encode_video_track = media_info_encode.video_tracks[0]
        encode_audio_track = media_info_encode.audio_tracks[0]

        # bluray source
        bluray_source = pathlib.Path(source_file_path.get()).stem

        # chapter information
        try:
            # check for numbered chapters
            chapters_start_numbered = re.search(r"chapter\s*(\d+)", str(list(encode_chapter.values())),
                                                re.IGNORECASE).group(1)
            chapters_end_numbered = re.search(r"chapter\s*(\d+)", str(list(reversed(encode_chapter.values()))),
                                              re.IGNORECASE).group(1)
            chapter_type = f'Numbered ({chapters_start_numbered.lstrip("0")}-{chapters_end_numbered.lstrip("0")})'
        except AttributeError:
            # check for tagged chapters
            if re.search(r"\d+:\d+:\d+\.\d+", list(encode_chapter.values())[-1]):
                nfo_pad.destroy()
                messagebox.showerror(parent=root, title='Error',
                                     message="Chapters appear to be 'Tagged'.\n\nBHDStudio encodes only support "
                                             "'Numbered' and 'Named' chapters. You will need to re-create the "
                                             "chapters via MeGui/StaxRip included chapter creator or download them "
                                             "from the ChapterDB.\n\nYou can then re-mux the encoded file via "
                                             "Mp4-Mux-Tool.")
                return  # exit the function
            # if chapters are not numbered or tagged
            else:
                chapter_type = 'Named'

        # file size
        encode_file_size = encode_general_track.other_file_size[0]

        # duration
        encode_file_duration = encode_video_track.other_duration[0]

        # video container format
        container_format = encode_general_track.commercial_name

        # video codec
        v_codec = encode_video_track.commercial_name

        # video bitrate
        v_bitrate = round((float(encode_video_track.stream_size) / 1000) /
                          ((float(encode_video_track.duration) / 60000) * 0.0075) / 1000)

        # video fps
        v_fps = f'{encode_video_track.frame_rate} fps'

        # video format profile
        v_format_profile = ''
        if encode_video_track.format_profile == 'High@L4.1':
            v_format_profile = 'High Profile 4.1'
        elif encode_video_track.format_profile == 'Main 10@L5.1@Main':
            hdr_type = str(encode_video_track.hdr_format_compatibility)
            if 'HDR10+' in hdr_type:
                hdr_string = ' / HDR10+'
            elif 'HDR10' in hdr_type:
                hdr_string = ' / HDR10'
            else:
                hdr_string = ''
            v_format_profile = f'Main 10 @ Level 5.1 @ Main / 4:2:0{hdr_string}'

        # video width
        v_width = encode_video_track.width

        # video height
        v_height = encode_video_track.height

        # video aspect ratio
        v_aspect_ratio = encode_video_track.other_display_aspect_ratio[0]

        # audio language
        a_lng = ''
        check_audio_language = encode_audio_track.other_language
        if check_audio_language:
            a_lng = encode_audio_track.other_language[0]
        if not check_audio_language:
            a_lng = 'English'

        # audio commercial name
        a_commercial = encode_audio_track.commercial_name

        # audio channels
        if encode_audio_track.channel_s == 1:
            a_chnl_s = '1.0'
        elif encode_audio_track.channel_s == 2:
            a_chnl_s = '2.0'
        elif encode_audio_track.channel_s == 6:
            a_chnl_s = '5.1'
        else:
            a_chnl_s = encode_audio_track.channel_s

        # audio frequency
        a_freq = encode_audio_track.other_sampling_rate[0]

        # audio bitrate
        a_bitrate = str(encode_audio_track.other_bit_rate[0]).replace('kb/s', '').strip()

        # optional sub string
        optional_sub_string = ''
        if forced_subtitles_burned_var.get() == 'on':
            optional_sub_string = '\nSubtitles               : English (Forced)'

        # encoder name
        encoded_by = ''
        encoder_sig = nfo_pad_parser['encoder_name']['name'].strip()
        if encoder_sig == '':
            encoded_by = 'Anonymous'
        elif encoder_sig != '':
            encoded_by = nfo_pad_parser['encoder_name']['name'].strip()

        # release notes
        nfo_release_notes = release_notes_scrolled.get("1.0", END).strip()

        # screen shots
        nfo_screen_shots = parse_screenshots

        formatted_nfo = decoded_nfo.format(bluray_source=bluray_source, chapter_type=chapter_type,
                                           encode_file_size=encode_file_size, encode_file_duration=encode_file_duration,
                                           container_format=container_format, v_codec=v_codec, v_bitrate=v_bitrate,
                                           v_fps=v_fps, v_format_profile=v_format_profile, v_width=v_width,
                                           v_height=v_height, v_aspect_ratio=v_aspect_ratio, a_lng=a_lng,
                                           a_commercial=a_commercial, a_chnl_s=a_chnl_s, a_freq=a_freq,
                                           a_bitrate=a_bitrate, optional_sub_string=optional_sub_string,
                                           encoded_by=encoded_by, nfo_release_notes=nfo_release_notes,
                                           nfo_screen_shots=nfo_screen_shots)
        return formatted_nfo

    try:  # if window is already opened
        if nfo_pad.winfo_exists():
            nfo = run_nfo_formatter()
            nfo_pad_text_box.delete("1.0", END)
            nfo_pad_text_box.insert(END, nfo)
            return
    except NameError:  # if window is not opened
        pass

    def nfo_pad_exit_function():
        # nfo pad exit parser
        nfo_pad_exit_parser = ConfigParser()
        nfo_pad_exit_parser.read(config_file)

        # save nfo pad position if different
        if nfo_pad.wm_state() == 'normal':
            if nfo_pad_exit_parser['save_window_locations']['nfo_pad'] != nfo_pad.geometry():
                if int(nfo_pad.geometry().split('x')[0]) >= nfo_pad_window_width or \
                        int(nfo_pad.geometry().split('x')[1].split('+')[0]) >= nfo_pad_window_height:
                    nfo_pad_exit_parser.set('save_window_locations', 'nfo_pad', nfo_pad.geometry())
                    with open(config_file, 'w') as nfo_configfile:
                        nfo_pad_exit_parser.write(nfo_configfile)

        # update nfo var
        nfo_info_var.set(nfo_pad_text_box.get("1.0", "end-1c"))

        if not automatic_workflow_boolean.get():
            nfo_pad.destroy()  # destroy nfo window
            open_all_toplevels()  # open all top levels that was open
            advanced_root_deiconify()  # re-open root
        if automatic_workflow_boolean.get():
            nfo_pad.destroy()  # destroy nfo window

    nfo_pad = Toplevel()
    nfo_pad.title('BHDStudioUploadTool - NFO Pad')
    nfo_pad_window_height = 600
    nfo_pad_window_width = 1000
    nfo_pad.config(bg="#363636")
    if nfo_pad_parser['save_window_locations']['nfo_pad'] == '':
        nfo_screen_width = nfo_pad.winfo_screenwidth()
        nfo_screen_height = nfo_pad.winfo_screenheight()
        nfo_x_coordinate = int((nfo_screen_width / 2) - (nfo_pad_window_width / 2))
        nfo_y_coordinate = int((nfo_screen_height / 2) - (nfo_pad_window_height / 2))
        nfo_pad.geometry(f"{nfo_pad_window_width}x{nfo_pad_window_height}+{nfo_x_coordinate}+{nfo_y_coordinate}")
    elif nfo_pad_parser['save_window_locations']['nfo_pad'] != '':
        nfo_pad.geometry(nfo_pad_parser['save_window_locations']['nfo_pad'])
    nfo_pad.protocol('WM_DELETE_WINDOW', lambda: [automatic_workflow_boolean.set(False), nfo_pad_exit_function()])

    nfo_pad.grid_columnconfigure(0, weight=1)
    nfo_pad.grid_columnconfigure(1, weight=1)
    nfo_pad.grid_rowconfigure(0, weight=1000)
    nfo_pad.grid_rowconfigure(1, weight=1)
    nfo_pad.grid_rowconfigure(2, weight=1)

    # Set variable for open file name
    global open_status_name
    open_status_name = False

    global selected
    selected = False

    # Create New File Function
    def new_file():
        # Delete previous text
        nfo_pad_text_box.delete("1.0", END)
        # Update status bars
        nfo_pad.title('New File - TextPad!')
        status_bar.config(text="New File")

        global open_status_name
        open_status_name = False

    # Open Files
    def open_file():
        # Delete previous text
        nfo_pad_text_box.delete("1.0", END)

        # define parser
        nfo_dir_parser = ConfigParser()
        nfo_dir_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(nfo_dir_parser['last_used_folder']['path']).is_dir():
            nfo_initial_dir = pathlib.Path(nfo_dir_parser['last_used_folder']['path'])
        else:
            nfo_initial_dir = '/'

        # Grab Filename
        text_file = filedialog.askopenfilename(parent=nfo_pad, initialdir=nfo_initial_dir, title="Open File",
                                               filetypes=[("Text Files, NFO Files", ".txt .nfo")])

        # Check to see if there is a file name
        if text_file:
            # Make filename global so we can access it later
            global open_status_name
            open_status_name = text_file

        # Update Status bars
        name = text_file
        status_bar.config(text=f'{name}')
        nfo_pad.title(f'{name} - NFO Pad!')

        # Open the file
        text_file = open(text_file, 'r')
        stuff = text_file.read()
        # Add file to textbox
        nfo_pad_text_box.insert(END, stuff)
        # Close the opened file
        text_file.close()

    # save as file
    def nfo_pad_save():
        # define parser
        nfo_save_parser = ConfigParser()
        nfo_save_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(nfo_save_parser['last_used_folder']['path']).is_dir():
            nfo_save_initial_dir = pathlib.Path(nfo_save_parser['last_used_folder']['path'])
        else:
            nfo_save_initial_dir = '/'

        # get save output
        text_file = filedialog.asksaveasfilename(parent=nfo_pad, defaultextension=".nfo",
                                                 initialdir=nfo_save_initial_dir,
                                                 title="Save File", filetypes=[("NFO File", "*.nfo")])
        if text_file:
            # update status bars
            name = text_file
            status_bar.config(text=f'Saved: {name}')
            nfo_pad.title(f'{name} - NFO Pad')

            # save the file
            text_file = open(text_file, 'w')
            text_file.write(nfo_pad_text_box.get("1.0", "end-1c"))

            # Close the file
            text_file.close()
            nfo_pad_exit_function()

    # Cut Text
    def cut_text(e):
        global selected
        # Check to see if keyboard shortcut used
        if e:
            selected = nfo_pad.clipboard_get()
        else:
            if nfo_pad_text_box.selection_get():
                # Grab selected text from text box
                selected = nfo_pad_text_box.selection_get()
                # Delete Selected Text from text box
                nfo_pad_text_box.delete("sel.first", "sel.last")
                # Clear the clipboard then append
                nfo_pad.clipboard_clear()
                nfo_pad.clipboard_append(selected)

    # Copy Text
    def copy_text(e):
        global selected
        # check to see if we used keyboard shortcuts
        if e:
            selected = nfo_pad.clipboard_get()

        if nfo_pad_text_box.selection_get():
            # Grab selected text from text box
            selected = nfo_pad_text_box.selection_get()
            # Clear the clipboard then append
            nfo_pad.clipboard_clear()
            nfo_pad.clipboard_append(selected)

    # Paste Text
    def paste_text(e):
        global selected
        # Check to see if keyboard shortcut used
        if e:
            selected = nfo_pad.clipboard_get()
        else:
            if selected:
                position = nfo_pad_text_box.index(INSERT)
                nfo_pad_text_box.insert(position, str(selected))

    # change bg color
    def bg_color():
        my_color = colorchooser.askcolor(parent=nfo_pad)[1]
        if my_color:
            nfo_pad_text_box.config(bg=my_color)

            # save scheme to config
            bg_parser = ConfigParser()
            bg_parser.read(config_file)
            bg_parser.set('nfo_pad_color_settings', 'background', my_color)
            with open(config_file, 'w') as bg_config:
                bg_parser.write(bg_config)

    # change all text color
    def all_text_color():
        my_color = colorchooser.askcolor(parent=nfo_pad)[1]
        if my_color:
            nfo_pad_text_box.config(fg=my_color)

            # save scheme to config
            txt_parser = ConfigParser()
            txt_parser.read(config_file)
            txt_parser.set('nfo_pad_color_settings', 'text', my_color)
            with open(config_file, 'w') as bg_config:
                txt_parser.write(bg_config)

    # select all text
    def select_all(e):
        # Add sel tag to select all text
        nfo_pad_text_box.tag_add('sel', '1.0', 'end')

    # clear all text
    def clear_all():
        nfo_pad_text_box.delete(1.0, END)

    # fixed font chooser
    fixed_font_chooser_opened = BooleanVar()

    # reset nfo pad color scheme
    def reset_colors():
        # define parser and clear
        nfo_reset_parser = ConfigParser()
        nfo_reset_parser.read(config_file)
        nfo_reset_parser.set('nfo_pad_color_settings', 'background', '')
        nfo_reset_parser.set('nfo_pad_color_settings', 'text', '')
        with open(config_file, 'w') as nfo_cf_reset:
            nfo_reset_parser.write(nfo_cf_reset)

        # set default colors
        nfo_pad_text_box.config(bg='#c0c0c0', fg='black')

    def fixed_font_chooser(*e):
        # check if window is already opened
        if fixed_font_chooser_opened.get():
            return  # if opened exit the function
        else:  # if not opened set to opened
            fixed_font_chooser_opened.set(True)

        # font parser
        font_parser = ConfigParser()
        font_parser.read(config_file)

        font_chooser_win = Toplevel()
        font_chooser_win.title('BHDStudio Upload Tool - Font')
        font_chooser_win.configure(background="#363636")
        font_chooser_win.geometry(f'{700}x{320}+{str(int(nfo_pad.geometry().split("+")[1]) + 108)}+'
                                  f'{str(int(nfo_pad.geometry().split("+")[2]) + 80)}')
        font_chooser_win.grab_set()  # grab set

        font_chooser_win.rowconfigure(0, weight=1)
        font_chooser_win.rowconfigure(1, weight=60)
        font_chooser_win.rowconfigure(2, weight=1)
        font_chooser_win.rowconfigure(3, weight=1)
        font_chooser_win.columnconfigure(0, weight=1)
        font_chooser_win.columnconfigure(1, weight=1)

        # start font instance
        font_instance = font.Font()
        available_fonts = font.families()

        # create a list of fixed fonts only
        mono_spaced_fonts = []
        for fonts in available_fonts:
            get_fixed_fonts = font.Font(family=fonts)
            if get_fixed_fonts.metrics("fixed"):
                mono_spaced_fonts.append(fonts)

        # some needed font variables
        default_font_size = font_instance.actual().get("size")  # get default font size
        define_font_type = font.nametofont("TkFixedFont")  # get default font value into Font object
        default_font_name = define_font_type.actual().get("family")  # get font name
        # default_style = font_instance.cget("weight")  # get weight as a variable

        # get index of default mono font name
        if font_parser['nfo_pad_font_settings']['font'].strip() != '':
            get_font_index = mono_spaced_fonts.index(font_parser['nfo_pad_font_settings']['font'].strip())
        else:
            get_font_index = mono_spaced_fonts.index(default_font_name)

        # fonts frame
        fonts_frame = LabelFrame(font_chooser_win, text=' Fonts ', labelanchor="nw", fg="#3498db", bg="#363636", bd=3,
                                 font=(set_font, set_font_size + 1, 'bold'))
        fonts_frame.grid(column=0, row=0, rowspan=3, pady=5, padx=5, sticky=W + E + N + S)
        fonts_frame.grid_columnconfigure(0, weight=1)
        for f_f in range(3):
            fonts_frame.grid_rowconfigure(f_f, weight=1)

        # fonts listbox
        fonts_right_scrollbar = Scrollbar(fonts_frame, orient=VERTICAL)  # scrollbar
        fonts_listbox = Listbox(fonts_frame, selectbackground="#c0c0c0", background="#c0c0c0",
                                selectforeground="#3498db", exportselection=False,
                                yscrollcommand=fonts_right_scrollbar.set, selectmode=SINGLE, bd=2, activestyle="none",
                                width=20, height=12)
        fonts_listbox.grid(row=0, column=0, rowspan=3, sticky=N + E + S + W)
        fonts_right_scrollbar.config(command=fonts_listbox.yview)
        fonts_right_scrollbar.grid(row=0, column=1, rowspan=3, sticky=N + W + S)

        # add fixed fonts to list box
        for fixed_fonts in mono_spaced_fonts:
            fonts_listbox.insert(END, fixed_fonts)

        # select current default font
        fonts_listbox.selection_set(get_font_index)

        # fonts frame
        style_frame = LabelFrame(font_chooser_win, text=' Style ', labelanchor="nw", fg="#3498db", bg="#363636", bd=3,
                                 font=(set_font, set_font_size + 1, 'bold'))
        style_frame.grid(column=1, row=0, pady=5, padx=5, sticky=E + W + N)
        style_frame.grid_columnconfigure(0, weight=1)
        style_frame.grid_rowconfigure(0, weight=1)

        # style combo box
        style_combo_box = ttk.Combobox(style_frame,
                                       values=['Normal', 'Bold', 'Italic', 'Roman', 'Underline', 'Overstrike'],
                                       state="readonly")
        style_combo_box.grid(column=0, row=0, padx=2, pady=2, sticky=E + W)

        # set weight
        if font_parser['nfo_pad_font_settings']['style'].strip() != '':
            style_combo_box.set(font_parser['nfo_pad_font_settings']['style'].strip())
        else:
            style_combo_box.set('Normal')

        # set size list
        values_list = []
        for x in range(8, 74, 2):
            values_list.append(x)

        # fonts frame
        size_frame = LabelFrame(font_chooser_win, text=' Size ', labelanchor="nw", fg="#3498db", bg="#363636", bd=3,
                                font=(set_font, set_font_size + 1, 'bold'))
        size_frame.grid(column=1, row=1, pady=5, padx=5, sticky=E + W + N)
        size_frame.grid_columnconfigure(0, weight=1)
        size_frame.grid_rowconfigure(0, weight=1)

        # size combo box
        size_combo_box = ttk.Combobox(size_frame, values=values_list)
        size_combo_box.grid(column=0, row=0, padx=2, pady=2, sticky=E + W)

        # set size
        if font_parser['nfo_pad_font_settings']['size'].strip() != '':
            size_combo_box.set(nfo_pad_parser['nfo_pad_font_settings']['size'].strip())
        else:
            size_combo_box.set(default_font_size)

        # sample label
        sample_label = Label(font_chooser_win, text="Aa", background="#363636", foreground="white")
        sample_label.grid(column=1, row=2, pady=5, padx=5, sticky=E + W + N + S)

        # constant loop to update the sample label
        def sample_label_loop():
            sample_label.config(font=(mono_spaced_fonts[fonts_listbox.curselection()[0]], size_combo_box.get(),
                                      str(style_combo_box.get()).lower()))
            font_chooser_win.after(30, sample_label_loop)

        # start sample label loop
        sample_label_loop()

        # font chooser button frame
        font_button_frame = LabelFrame(font_chooser_win, bg="#363636", bd=0)
        font_button_frame.grid(column=0, row=3, columnspan=2, padx=5, pady=(5, 3), sticky=E + W)
        font_button_frame.grid_rowconfigure(0, weight=1)
        font_button_frame.grid_columnconfigure(0, weight=1)
        font_button_frame.grid_columnconfigure(1, weight=60)
        font_button_frame.grid_columnconfigure(2, weight=1)

        # reset command
        def reset_font_to_default():
            # define parser
            nfo_reset_parser = ConfigParser()
            nfo_reset_parser.read(config_file)

            # define settings
            nfo_reset_parser.set('nfo_pad_font_settings', 'font', '')
            nfo_reset_parser.set('nfo_pad_font_settings', 'style', '')
            nfo_reset_parser.set('nfo_pad_font_settings', 'size', '')
            with open(config_file, 'w') as font_configfile_reset:
                nfo_reset_parser.write(font_configfile_reset)

            # apply settings to nfo pad
            nfo_pad_text_box.config(font=(set_fixed_font, set_font_size + 1))

            # reset all the selections in the font chooser window
            fonts_listbox.selection_clear(0, END)  # clear selection
            fonts_listbox.selection_set(mono_spaced_fonts.index(default_font_name))  # set default value
            style_combo_box.set('Normal')  # set default value
            size_combo_box.set(default_font_size)  # set default value

        # once function is exited set starting boolean to false
        fixed_font_chooser_opened.set(False)

        # reset button
        font_reset_button = HoverButton(font_button_frame, text="Reset", command=reset_font_to_default,
                                        foreground="white", background="#23272A", borderwidth="3", width=8,
                                        activeforeground="#3498db", activebackground="#23272A")
        font_reset_button.grid(row=0, column=0, columnspan=1, padx=3, pady=5, sticky=W)

        # cancel button
        font_cancel_button = HoverButton(font_button_frame, text="Close", command=font_chooser_win.destroy,
                                         foreground="white", background="#23272A", borderwidth="3", width=8,
                                         activeforeground="#3498db", activebackground="#23272A")
        font_cancel_button.grid(row=0, column=1, columnspan=1, padx=3, pady=5, sticky=E)

        # change the font for the nfo pad
        def apply_command():
            # define parser
            nfo_apply_parser = ConfigParser()
            nfo_apply_parser.read(config_file)

            # define settings
            nfo_apply_parser.set('nfo_pad_font_settings', 'font', mono_spaced_fonts[fonts_listbox.curselection()[0]])
            nfo_apply_parser.set('nfo_pad_font_settings', 'size', str(size_combo_box.get()))
            nfo_apply_parser.set('nfo_pad_font_settings', 'style', str(style_combo_box.get()))
            with open(config_file, 'w') as font_configfile_apply:
                nfo_apply_parser.write(font_configfile_apply)

            # apply settings to nfo pad
            nfo_pad_text_box.config(font=(mono_spaced_fonts[fonts_listbox.curselection()[0]], size_combo_box.get(),
                                          str(style_combo_box.get()).lower()))

        # apply button
        font_apply_button = HoverButton(font_button_frame, text="Apply", command=apply_command,
                                        foreground="white", background="#23272A", borderwidth="3", width=8,
                                        activeforeground="#3498db", activebackground="#23272A")
        font_apply_button.grid(row=0, column=2, columnspan=1, padx=3, pady=5, sticky=E)

    # create main frame
    nfo_frame = Frame(nfo_pad)
    nfo_frame.grid(column=0, columnspan=2, row=0, pady=(5, 0), padx=5, sticky=N + S + E + W)
    nfo_frame.grid_columnconfigure(0, weight=1)
    nfo_frame.grid_rowconfigure(0, weight=1)

    # scroll bars
    right_scrollbar = Scrollbar(nfo_frame, orient=VERTICAL)  # scrollbars
    bottom_scrollbar = Scrollbar(nfo_frame, orient=HORIZONTAL)

    # create text box
    nfo_pad_text_box = Text(nfo_frame, undo=True, yscrollcommand=right_scrollbar.set, wrap="none",
                            xscrollcommand=bottom_scrollbar.set, background='#c0c0c0',
                            font=(set_fixed_font, set_font_size + 1))
    nfo_pad_text_box.grid(column=0, row=0, sticky=N + S + E + W)

    if nfo_pad_parser['nfo_pad_color_settings']['background'] != '':
        nfo_pad_text_box.config(bg=nfo_pad_parser['nfo_pad_color_settings']['background'])
    if nfo_pad_parser['nfo_pad_color_settings']['text'] != '':
        nfo_pad_text_box.config(fg=nfo_pad_parser['nfo_pad_color_settings']['text'])

    # add scrollbars to the textbox
    right_scrollbar.config(command=nfo_pad_text_box.yview)
    right_scrollbar.grid(row=0, column=1, sticky=N + W + S)
    bottom_scrollbar.config(command=nfo_pad_text_box.xview)
    bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

    # define starting font
    if nfo_pad_parser['nfo_pad_font_settings']['font'].strip() != '' and \
            nfo_pad_parser['nfo_pad_font_settings']['style'].strip() != '' and \
            nfo_pad_parser['nfo_pad_font_settings']['size'].strip() != '':
        nfo_pad_text_box.config(font=(nfo_pad_parser['nfo_pad_font_settings']['font'].strip(),
                                      int(nfo_pad_parser['nfo_pad_font_settings']['size'].strip()),
                                      nfo_pad_parser['nfo_pad_font_settings']['style'].strip().lower()))

    # Create Menu
    nfo_main_menu = Menu(nfo_pad)
    nfo_pad.config(menu=nfo_main_menu)

    # Add File Menu
    nfo_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="File", menu=nfo_menu)
    nfo_menu.add_command(label="New", command=new_file)
    nfo_menu.add_command(label="Open", command=open_file)
    nfo_menu.add_command(label="Save", command=nfo_pad_save)
    nfo_menu.add_command(label="Save Internally", command=nfo_pad_exit_function)
    nfo_menu.add_separator()
    nfo_menu.add_command(label="Exit", command=lambda: [automatic_workflow_boolean.set(False), nfo_pad_exit_function()])

    # Add Edit Menu
    edit_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+x)")
    edit_menu.add_command(label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+c)")
    edit_menu.add_command(label="Paste             ", command=lambda: paste_text(False), accelerator="(Ctrl+v)")
    edit_menu.add_separator()
    edit_menu.add_command(label="Undo", command=nfo_pad_text_box.edit_undo, accelerator="(Ctrl+z)")
    edit_menu.add_command(label="Redo", command=nfo_pad_text_box.edit_redo, accelerator="(Ctrl+y)")
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=lambda: select_all(True), accelerator="(Ctrl+a)")
    edit_menu.add_command(label="Clear", command=clear_all)

    # add options menu
    options_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(label="Font Settings", command=fixed_font_chooser, accelerator="(Ctrl+o)")

    # Add Color Menu
    color_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Colors", menu=color_menu)
    color_menu.add_command(label="Text Color", command=all_text_color)
    color_menu.add_command(label="Background", command=bg_color)
    color_menu.add_separator()
    color_menu.add_command(label="Reset", command=reset_colors)

    # Add Status Bar To Bottom Of App
    status_bar = Label(nfo_pad, text='Ready', anchor=E, bg="#565656", fg="white", relief=SUNKEN)
    status_bar.grid(column=0, columnspan=2, row=2, pady=1, padx=1, sticky=E + W)

    # edit bindings
    nfo_pad.bind('<Control-Key-x>', cut_text)
    nfo_pad.bind('<Control-Key-c>', copy_text)
    nfo_pad.bind('<Control-Key-v>', paste_text)
    nfo_pad.bind('<Control-Key-o>', fixed_font_chooser)
    # select binding
    nfo_pad.bind('<Control-A>', select_all)
    nfo_pad.bind('<Control-a>', select_all)

    # format nfo via function
    nfo = run_nfo_formatter()

    # if information was not returned correctly
    if not nfo:
        return  # exit this function

    # delete any text (shouldn't be any)
    nfo_pad_text_box.delete("1.0", END)

    # insert new nfo
    nfo_pad_text_box.insert(END, nfo)

    # if program is in automatic workflow mode
    if automatic_workflow_boolean.get():
        workflow_frame = Frame(nfo_pad, bg="#363636")
        workflow_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=0, sticky=N + S + E + W)
        workflow_frame.grid_columnconfigure(0, weight=1)
        workflow_frame.grid_columnconfigure(1, weight=1)
        workflow_frame.grid_rowconfigure(0, weight=1)

        continue_button = HoverButton(workflow_frame, text="Continue", activebackground="#23272A",
                                      command=lambda: [automatic_workflow_boolean.set(True), nfo_pad_exit_function()],
                                      foreground="white", background="#23272A", borderwidth="3",
                                      activeforeground="#3498db", width=10)
        continue_button.grid(row=0, column=1, columnspan=1, padx=7, pady=(3, 0), sticky=N + S + E)

        cancel_workflow_button = HoverButton(workflow_frame, text="Cancel", width=10, foreground="white",
                                             command=lambda: [automatic_workflow_boolean.set(False),
                                                              nfo_pad_exit_function()], activebackground="#23272A",
                                             borderwidth="3", activeforeground="#3498db", background="#23272A")
        cancel_workflow_button.grid(row=0, column=0, columnspan=1, padx=7, pady=(3, 0), sticky=N + S + W)
        status_bar.config(text="(Saving is optional)   Cancel / Closing NFO Pad will stop the automatic workflow  |  "
                               "Click continue to proceed...")
        nfo_pad.wait_window()


generate_nfo_button = HoverButton(manual_workflow, text="Generate NFO", command=open_nfo_viewer, foreground="white",
                                  background="#23272A", borderwidth="3", activeforeground="#3498db",
                                  activebackground="#23272A", width=15)
generate_nfo_button.grid(row=0, column=1, columnspan=1, padx=5, pady=1, sticky=E + W)


# torrent creation ----------------------------------------------------------------------------------------------------
def torrent_function_window():
    # main torrent parser
    torrent_config = ConfigParser()
    torrent_config.read(config_file)

    # torrent window exit function
    def torrent_window_exit_function():
        # exit torrent parser
        torrent_parser = ConfigParser()
        torrent_parser.read(config_file)

        # save announce url if it's correct
        if '/announce' in torrent_tracker_url_entry_box.get().strip():
            torrent_parser.set('torrent_settings', 'tracker_url', torrent_tracker_url_entry_box.get().strip())
            with open(config_file, 'w') as torrent_configfile:
                torrent_parser.write(torrent_configfile)

        # save torrent window position/geometry
        if torrent_window.wm_state() == 'normal':
            if torrent_parser['save_window_locations']['torrent_window'] != torrent_window.geometry():
                if int(torrent_window.geometry().split('x')[0]) >= tor_window_width or \
                        int(torrent_window.geometry().split('x')[1].split('+')[0]) >= tor_window_height:
                    torrent_parser.set('save_window_locations', 'torrent_window', torrent_window.geometry())
                    with open(config_file, 'w') as torrent_configfile:
                        torrent_parser.write(torrent_configfile)

        if not automatic_workflow_boolean.get():
            torrent_window.destroy()  # destroy torrent window
            open_all_toplevels()  # open all top levels that was open
            advanced_root_deiconify()  # re-open root
        if automatic_workflow_boolean.get():
            torrent_window.destroy()  # destroy torrent window

    hide_all_toplevels()  # hide all top levels
    root.withdraw()  # hide root

    # create new toplevel window
    torrent_window = Toplevel()
    torrent_window.configure(background="#363636")  # Set color of torrent_window background
    torrent_window.title('BHDStudio Torrent Creator')
    tor_window_height = 330  # win height
    tor_window_width = 520  # win width
    if torrent_config['save_window_locations']['torrent_window'] == '':
        # open near the center of root
        torrent_window.geometry(f'{tor_window_width}x{tor_window_height}+'
                                f'{str(int(root.geometry().split("+")[1]) + 100)}+'
                                f'{str(int(root.geometry().split("+")[2]) + 210)}')
    elif torrent_config['save_window_locations']['torrent_window'] != '':
        torrent_window.geometry(torrent_config['save_window_locations']['torrent_window'])
    torrent_window.protocol('WM_DELETE_WINDOW', lambda: [automatic_workflow_boolean.set(False),
                                                         torrent_window_exit_function()])

    # row and column configure
    for t_w in range(10):
        torrent_window.grid_columnconfigure(t_w, weight=1)
    for t_w in range(10):
        torrent_window.grid_rowconfigure(t_w, weight=1)

    # torrent path frame
    torrent_path_frame = LabelFrame(torrent_window, text=' Path ', labelanchor="nw")
    torrent_path_frame.grid(column=0, row=0, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S)
    torrent_path_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_path_frame.grid_rowconfigure(0, weight=1)
    for t_f in range(10):
        torrent_path_frame.grid_columnconfigure(t_f, weight=1)

    # re-define torrent output if the user wants
    def torrent_save_output():
        torrent_file_input = filedialog.asksaveasfilename(parent=root, title='Save Torrent',
                                                          initialdir=pathlib.Path(torrent_file_path.get()).parent,
                                                          initialfile=pathlib.Path(torrent_file_path.get()).name,
                                                          filetypes=[("Torrent Files", "*.torrent")])
        if torrent_file_input:
            torrent_entry_box.config(state=NORMAL)
            torrent_entry_box.delete(0, END)
            torrent_entry_box.insert(END, pathlib.Path(torrent_file_input).with_suffix('.torrent'))
            torrent_file_path.set(pathlib.Path(torrent_file_input).with_suffix('.torrent'))
            torrent_entry_box.config(state=DISABLED)
            return True
        if not torrent_file_input:
            return False

    # torrent set path button
    torrent_button = HoverButton(torrent_path_frame, text="Set", command=torrent_save_output, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db",
                                 activebackground="#23272A")
    torrent_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 5), sticky=N + S + E + W)

    # torrent path entry box
    torrent_entry_box = Entry(torrent_path_frame, borderwidth=4, bg="#565656", fg='white',
                              disabledforeground='white', disabledbackground="#565656")
    torrent_entry_box.grid(row=0, column=1, columnspan=9, padx=5, pady=(5, 5), sticky=N + S + E + W)
    torrent_entry_box.insert(END, pathlib.Path(torrent_file_path.get()))
    torrent_entry_box.config(state=DISABLED)

    # torrent piece frame
    torrent_piece_frame = LabelFrame(torrent_window, text=' Settings ', labelanchor="nw")
    torrent_piece_frame.grid(column=0, row=1, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S)
    torrent_piece_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_piece_frame.grid_columnconfigure(0, weight=1)
    torrent_piece_frame.grid_columnconfigure(1, weight=200)
    torrent_piece_frame.grid_columnconfigure(2, weight=2000)
    torrent_piece_frame.grid_columnconfigure(3, weight=200000)
    torrent_piece_frame.grid_rowconfigure(0, weight=1)
    torrent_piece_frame.grid_rowconfigure(1, weight=1)

    # calculate piece size for 'piece_size_info_label2'
    def set_piece_size(*args):
        # get size of file with os.stat()
        file = float(os.stat(pathlib.Path(encode_file_path.get())).st_size)
        # if torrent is auto use torf.Torrent() to generate piece size
        if torrent_piece.get() == 'Auto':
            calculate_pieces = math.ceil(file / float(Torrent.calculate_piece_size(file)))
        # if any other setting manually calculate it
        else:
            calculate_pieces = math.ceil(float(os.stat(pathlib.Path(encode_file_path.get())).st_size) / float(
                torrent_piece_choices[torrent_piece.get()]))

        # update label with piece size
        piece_size_label2.config(text=str(calculate_pieces))

    # piece size info label
    piece_size_info_label = Label(torrent_piece_frame, text='Piece Size:', bd=0, relief=SUNKEN, background='#363636',
                                  fg="#3498db", font=(set_font, set_font_size + 1))
    piece_size_info_label.grid(column=0, row=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W)

    # piece size menu
    torrent_piece_choices = {
        "Auto": None,
        "16 KiB": 16384,
        "32 KiB": 32768,
        "64 KiB": 65536,
        "128 KiB": 131072,
        "256 KiB": 262144,
        "512 KiB": 524288,
        "1 MiB": 1048576,
        "2 MiB": 2097152,
        "4 MiB": 4194304,
        "8 MiB": 8388608,
        "16 MiB": 16777216,
        "32 MiB": 33554432}
    torrent_piece = StringVar()
    torrent_piece.set("Auto")
    torrent_piece_menu = OptionMenu(torrent_piece_frame, torrent_piece, *torrent_piece_choices.keys(),
                                    command=set_piece_size)
    torrent_piece_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=7,
                              activebackground="grey")
    torrent_piece_menu.grid(row=0, column=1, columnspan=1, pady=(7, 5), padx=(10, 5), sticky=W)
    torrent_piece_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')

    # piece size label
    piece_size_label = Label(torrent_piece_frame, text='Total Pieces:', bd=0, relief=SUNKEN, background='#363636',
                             fg="#3498db", font=(set_font, set_font_size + 1))
    piece_size_label.grid(column=2, row=0, columnspan=1, pady=(5, 0), padx=(20, 0), sticky=W)

    # piece size label 2
    piece_size_label2 = Label(torrent_piece_frame, text='', bd=0, relief=SUNKEN, background='#363636',
                              fg="white", font=(set_font, set_font_size))
    piece_size_label2.grid(column=3, row=0, columnspan=1, pady=(7, 0), padx=(5, 5), sticky=W)

    # set piece size information
    set_piece_size()

    # torrent entry frame
    torrent_entry_frame = LabelFrame(torrent_window, text=' Fields ', labelanchor="nw")
    torrent_entry_frame.grid(column=0, row=2, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S)
    torrent_entry_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_entry_frame.grid_columnconfigure(0, weight=1)
    torrent_entry_frame.grid_columnconfigure(1, weight=200)
    torrent_entry_frame.grid_columnconfigure(2, weight=2000)
    torrent_entry_frame.grid_columnconfigure(3, weight=200000)
    torrent_entry_frame.grid_rowconfigure(0, weight=1)
    torrent_entry_frame.grid_rowconfigure(1, weight=1)

    # tracker url label
    torrent_tracker_label = Label(torrent_entry_frame, text='Tracker URL:', bd=0, relief=SUNKEN, background='#363636',
                                  fg="#3498db", font=(set_font, set_font_size))
    torrent_tracker_label.grid(row=0, column=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W)

    # tracker url entry box
    torrent_tracker_url_entry_box = Entry(torrent_entry_frame, borderwidth=4, bg="#565656", fg='white',
                                          disabledforeground='white', disabledbackground="#565656", show='*')
    torrent_tracker_url_entry_box.grid(row=0, column=1, columnspan=7, padx=(2, 5), pady=(5, 0), sticky=N + S + E + W)
    torrent_tracker_url_entry_box.bind('<Enter>', lambda event: torrent_tracker_url_entry_box.config(show=''))
    torrent_tracker_url_entry_box.bind('<Leave>', lambda event: torrent_tracker_url_entry_box.config(show='*'))

    # if tracker url from config.ini is not empty, set it
    if config['torrent_settings']['tracker_url'] != '':
        torrent_tracker_url_entry_box.insert(END, config['torrent_settings']['tracker_url'])

    # torrent source label
    torrent_source_label = Label(torrent_entry_frame, text='Source:', bd=0, relief=SUNKEN, background='#363636',
                                 fg="#3498db", font=(set_font, set_font_size))
    torrent_source_label.grid(row=1, column=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W)

    # torrent source entry box
    torrent_source_entry_box = Entry(torrent_entry_frame, borderwidth=4, bg="#565656", fg='white',
                                     disabledforeground='white', disabledbackground="#565656")
    torrent_source_entry_box.grid(row=1, column=1, columnspan=5, padx=(2, 5), pady=5, sticky=N + S + E + W)

    # insert string 'BHD' into source
    torrent_source_entry_box.insert(END, 'BHD')

    # create torrent
    def create_torrent():
        if pathlib.Path(torrent_file_path.get()).is_file():
            # ask user if they would like to use the existing torrent file
            use_existing_file = messagebox.askyesno(parent=root, title='Use Existing File?',
                                                    message=f'"{pathlib.Path(torrent_file_path.get()).name}"\n\n'
                                                            f'File already exists.\n\nWould you like to use '
                                                            f'existing file?')
            # if user presses yes
            if use_existing_file:
                torrent_window_exit_function()
                return

            # if user press no
            if not use_existing_file:
                # ask user if they would like to overwrite
                check_overwrite = messagebox.askyesno(parent=root, title='Overwrite File?',
                                                      message='Would you like to overwrite file?')
                if not check_overwrite:  # if user does not want to overwrite file
                    save_new_file = torrent_save_output()  # call the torrent_save_output() function
                    if not save_new_file:  # if user press cancel in the torrent_save_output() window
                        return  # exit this function

        error = False  # set temporary error variable
        try:
            build_torrent = Torrent(path=pathlib.Path(encode_file_path.get()),
                                    trackers=str(torrent_tracker_url_entry_box.get()).strip(),
                                    private=True, source=torrent_source_entry_box.get().strip(),
                                    piece_size=torrent_piece_choices[torrent_piece.get()])
        except torf.URLError:  # if tracker url is invalid
            messagebox.showerror(parent=torrent_window, title='Error', message='Invalid Tracker URL')
            error = True  # set error to true
        except torf.PathError:  # if path to encoded file is invalid
            messagebox.showerror(parent=torrent_window, title='Error', message='Path to encoded file is invalid')
            error = True  # set error to true
        except torf.PieceSizeError:  # if piece size is incorrect
            messagebox.showerror(parent=torrent_window, title='Error', message='Piece size is incorrect')
            error = True  # set error to true

        if error:  # if error is true
            return  # exit the function

        # call back method to read/abort progress
        def torrent_progress(torrent, filepath, pieces_done, pieces_total):
            try:
                app_progress_bar['value'] = int(f'{pieces_done / pieces_total * 100:3.0f}')
                custom_style.configure('text.Horizontal.TProgressbar', text=f'{pieces_done / pieces_total * 100:3.0f}')
            except TclError:  # if window is closed return 0
                return 0  # returning 0 ends process

        # if callback torrent_progress returns anything other than None, exit the function
        if not build_torrent.generate(callback=torrent_progress):
            return  # exit function

        # once hash is completed build torrent file, overwrite automatically
        build_torrent.write(pathlib.Path(torrent_file_path.get()), overwrite=True)

        # if *.torrent exists then exit the window
        if pathlib.Path(torrent_file_path.get()).is_file():
            torrent_window_exit_function()

    # progress bar
    app_progress_bar = ttk.Progressbar(torrent_window, orient=HORIZONTAL, mode='determinate',
                                       style="text.Horizontal.TProgressbar")
    app_progress_bar.grid(row=3, column=0, columnspan=10, sticky=W + E, pady=5, padx=5)

    # set text to progress bar every time window opens to ''
    custom_style.configure('text.Horizontal.TProgressbar', text='')

    # create torrent button
    create_torrent_button = HoverButton(torrent_window, text="Create", activebackground="#23272A",
                                        command=lambda: threading.Thread(target=create_torrent).start(),
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=12)
    create_torrent_button.grid(row=4, column=9, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # cancel torrent button
    cancel_torrent_button = HoverButton(torrent_window, text="Cancel", activebackground="#23272A",
                                        command=lambda: [automatic_workflow_boolean.set(False),
                                                         torrent_window_exit_function()],
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=12)
    cancel_torrent_button.grid(row=4, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N)

    # if program is in automatic workflow mode
    if automatic_workflow_boolean.get():
        torrent_window.wait_window()


# open torrent window button
open_torrent_window_button = HoverButton(manual_workflow, text="Create Torrent", command=torrent_function_window,
                                         foreground="white", background="#23272A", borderwidth="3", width=15,
                                         activeforeground="#3498db", activebackground="#23272A", state=DISABLED)
open_torrent_window_button.grid(row=0, column=0, columnspan=1, padx=(10, 5), pady=1, sticky=E + W)

# view loaded script button
view_loaded_script = HoverButton(root, text="View Script", state=DISABLED,
                                 command=lambda: os.startfile(pathlib.Path(input_script_path.get())),
                                 foreground="white", background="#23272A", borderwidth="3",
                                 activeforeground="#3498db", width=10, activebackground="#23272A")
view_loaded_script.grid(row=4, column=2, columnspan=1, padx=(20, 5), pady=(23, 3), sticky=E + W)

# automatic workflow frame
automatic_workflow = LabelFrame(root, text=' Automatic Workflow ', labelanchor="nw")
automatic_workflow.grid(column=3, row=4, columnspan=1, padx=5, pady=(5, 3), sticky=E)
automatic_workflow.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, set_font_size + 1, 'bold'))
automatic_workflow.grid_rowconfigure(0, weight=1)
automatic_workflow.grid_columnconfigure(0, weight=1)


# uploader window
def open_uploader_window(job_mode):
    # uploader window config parser
    uploader_window_config_parser = ConfigParser()
    uploader_window_config_parser.read(config_file)

    # if key is not found in the config.ini file
    if uploader_window_config_parser['bhd_upload_api']['key'] == '':
        api_checkpoint = messagebox.askyesno(parent=root, title='Missing API Key',
                                             message='You are missing your BHD API Key\n\nWould you like to add '
                                                     'this key now?\n\nNote: You can do this manually in '
                                                     '"Options > Api Key"')
        # if user presses yes
        if api_checkpoint:
            # open a new custom window to obtain and save the key to config.ini
            custom_input_prompt(root, 'BHD Upload Key:', 'bhd_upload_api', 'key', 'hide')
            # define temp parser
            api_temp_parser = ConfigParser()
            api_temp_parser.read(config_file)
            # if bhd key is still nothing, set workflow to False, re-open root and top levels, then exit this function
            if api_temp_parser['bhd_upload_api']['key'] == '':
                automatic_workflow_boolean.set(0)
                advanced_root_deiconify()
                open_all_toplevels()
                return
        # if user presses no, set workflow to False, re-open root and top levels, then exit this function
        if not api_checkpoint:
            automatic_workflow_boolean.set(0)
            advanced_root_deiconify()
            open_all_toplevels()
            return

    # check job type, if auto or manual, clear some variables
    if job_mode == 'auto' or job_mode == 'manual':
        movie_search_var.set('')
        tmdb_id_var.set('')
        imdb_id_var.set('')
        release_date_var.set('')
        rating_var.set('')

    # if job type is custom_advanced, reset the entire GUI for a clean and empty uploader window
    elif job_mode == 'custom_advanced':
        reset_gui()

    # update id variables
    try:
        tmdb_id_var.set(source_file_information['tmdb_id'])
        imdb_id_var.set(source_file_information['imdb_id'])
    except KeyError:
        pass

    # uploader window exit function
    def upload_window_exit_function():
        # uploader exit parser
        uploader_exit_parser = ConfigParser()
        uploader_exit_parser.read(config_file)

        # save window position/geometry
        if upload_window.wm_state() == 'normal':
            if uploader_exit_parser['save_window_locations']['uploader'] != upload_window.geometry():
                if int(upload_window.geometry().split('x')[0]) >= upload_window_width or \
                        int(upload_window.geometry().split('x')[1].split('+')[0]) >= upload_window_height:
                    uploader_exit_parser.set('save_window_locations', 'uploader', upload_window.geometry())
                    with open(config_file, 'w') as uploader_exit_config_file:
                        uploader_exit_parser.write(uploader_exit_config_file)

        # close window, re-open root, re-open all top level windows if they exist
        upload_window.destroy()
        advanced_root_deiconify()
        open_all_toplevels()

    # hide all top levels and main GUI
    hide_all_toplevels()
    root.withdraw()

    # upload window
    upload_window = Toplevel()
    upload_window.title('BHDStudio - Uploader')
    upload_window.iconphoto(True, PhotoImage(data=base_64_icon))
    upload_window.configure(background="#363636")
    upload_window_height = 660
    upload_window_width = 720
    if uploader_window_config_parser['save_window_locations']['uploader'] == '':
        uploader_screen_width = upload_window.winfo_screenwidth()
        uploader_screen_height = upload_window.winfo_screenheight()
        uploader_x_coordinate = int((uploader_screen_width / 2) - (upload_window_width / 2))
        uploader_y_coordinate = int((uploader_screen_height / 2) - (upload_window_height / 2))
        upload_window.geometry(f"{upload_window_width}x{upload_window_height}+"
                               f"{uploader_x_coordinate}+{uploader_y_coordinate}")
    elif uploader_window_config_parser['save_window_locations']['uploader'] != '':
        upload_window.geometry(uploader_window_config_parser['save_window_locations']['uploader'])
    upload_window.protocol('WM_DELETE_WINDOW', upload_window_exit_function)

    # row and column configures
    for u_w_c in range(4):
        upload_window.grid_columnconfigure(u_w_c, weight=1)
    for u_w_r in range(7):
        upload_window.grid_rowconfigure(u_w_r, weight=1)

    # upload torrent options frame
    torrent_options_frame = LabelFrame(upload_window, text=' Torrent Input ', labelanchor="nw")
    torrent_options_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    torrent_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_options_frame.grid_rowconfigure(0, weight=1)
    torrent_options_frame.grid_columnconfigure(0, weight=1)
    torrent_options_frame.grid_columnconfigure(1, weight=20)

    # torrent drag and drop function for torrent file
    def torrent_drop_function(event):
        torrent_file_input = [x for x in root.splitlist(event.data)][0]
        # ensure dropped file is a *.torrent file
        if pathlib.Path(torrent_file_input).suffix == '.torrent':
            torrent_file_path.set(str(pathlib.Path(torrent_file_input)))
        else:
            messagebox.showinfo(parent=upload_window, title='Info', message='Only .torrent files can be opened')

    # bind frame to drop torrent file
    torrent_options_frame.drop_target_register(DND_FILES)
    torrent_options_frame.dnd_bind('<<Drop>>', torrent_drop_function)

    # manual torrent file selection
    def open_torrent_file():
        # define parser
        torrent_input_parser = ConfigParser()
        torrent_input_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(torrent_input_parser['last_used_folder']['path']).is_dir():
            torrent_save_dir = pathlib.Path(torrent_input_parser['last_used_folder']['path'])
        else:
            torrent_save_dir = '/'

        # get torrent input
        torrent_input = filedialog.askopenfilename(parent=upload_window, title='Select Torrent',
                                                   initialdir=torrent_save_dir,
                                                   filetypes=[("Torrent Files", "*.torrent")])
        if torrent_input:
            torrent_file_path.set(str(pathlib.Path(torrent_input)))

    torrent_input_button = HoverButton(torrent_options_frame, text="Open", command=open_torrent_file,
                                       foreground="white", background="#23272A", borderwidth="3",
                                       activeforeground="#3498db", activebackground="#23272A")
    torrent_input_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W)

    torrent_input_entry_box = Entry(torrent_options_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                                    disabledforeground='white', disabledbackground="#565656",
                                    textvariable=torrent_file_path)
    torrent_input_entry_box.grid(row=0, column=1, columnspan=3, padx=5, pady=(5, 0), sticky=E + W)

    title_options_frame = LabelFrame(upload_window, text=' Title ', labelanchor="nw")
    title_options_frame.grid(column=0, row=3, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    title_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    title_options_frame.grid_rowconfigure(0, weight=1)
    title_options_frame.grid_columnconfigure(0, weight=1)

    title_input_entry_box = Entry(title_options_frame, borderwidth=4, bg="#565656", fg='white',
                                  disabledforeground='white', disabledbackground="#565656")
    title_input_entry_box.grid(row=0, column=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)

    # automatically insert corrected bhdstudio name into the title box
    if encode_file_path.get() != '':
        title_input_entry_box.insert(END, str(pathlib.Path(pathlib.Path(encode_file_path.get()).name).with_suffix(''))
                                     .replace('.', ' ').replace('DD 1 0', 'DD1.0').replace('DD 2 0', 'DD2.0')
                                     .replace('DD 5 1', 'DD5.1'))

    upload_options_frame = LabelFrame(upload_window, text=' Options ', labelanchor="nw")
    upload_options_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    upload_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    upload_options_frame.grid_rowconfigure(0, weight=1)
    upload_options_frame.grid_rowconfigure(1, weight=1)
    for u_o_f in range(6):
        upload_options_frame.grid_columnconfigure(u_o_f, weight=300)

    type_label = Label(upload_options_frame, text='Type', bd=0, relief=SUNKEN, background='#363636',
                       fg="#3498db", font=(set_font, set_font_size + 1))
    type_label.grid(column=0, row=0, columnspan=1, pady=(5, 0), padx=(5, 10), sticky=E)

    # resolution menu
    type_choices = {"720p": "720p", "1080p": "1080p", "2160p": "2160p"}
    type_var = StringVar()
    type_var_menu = OptionMenu(upload_options_frame, type_var, *type_choices.keys(), command=None)
    type_var_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=12,
                         activebackground="grey")
    type_var_menu.grid(row=0, column=1, columnspan=1, pady=(7, 5), padx=(0, 5), sticky=W)
    type_var_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')
    if encode_file_path.get().strip() != '' and pathlib.Path(encode_file_path.get().strip()).is_file():
        type_var.set(encode_file_resolution.get().strip())

    # Blu-ray selection menu (only Blu-ray for BHD)
    upload_source_label = Label(upload_options_frame, text='Source', bd=0, relief=SUNKEN, background='#363636',
                                fg="#3498db", font=(set_font, set_font_size + 1))
    upload_source_label.grid(column=2, row=0, columnspan=1, pady=(5, 0), padx=(5, 5), sticky=E)

    source_choices = {"Blu-Ray": "Blu-ray"}
    source_var = StringVar()
    source_var_menu = OptionMenu(upload_options_frame, source_var, *source_choices.keys(), command=None)
    source_var_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=12,
                           activebackground="grey")
    source_var_menu.grid(row=0, column=3, columnspan=1, pady=(7, 5), padx=(2, 5), sticky=W)
    source_var_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')
    source_var.set('Blu-Ray')  # set var to Blu-Ray

    # select edition menu
    edition_label = Label(upload_options_frame, text='Edition\n(Optional)', bd=0, relief=SUNKEN, background='#363636',
                          fg="#3498db", font=(set_font, set_font_size + 1))
    edition_label.grid(column=4, row=0, columnspan=1, pady=(5, 0), padx=5, sticky=E)

    edition_choices = {
        "N/A": "",
        "Collector's Edition": "Collector",
        "Director's Cut": "Director",
        "Extended Cut": "Extended",
        "Limited Edition": "Limited",
        "Special Edition": "Special",
        "Theatrical Cut": "Theatrical",
        "Uncut": "Uncut",
        "Unrated": "Unrated"}
    edition_var = StringVar()
    edition_var.set("N/A")
    edition_var_menu = OptionMenu(upload_options_frame, edition_var, *edition_choices.keys(), command=None)
    edition_var_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=12,
                            activebackground="grey")
    edition_var_menu.grid(row=0, column=5, columnspan=1, pady=(7, 5), padx=(0, 5), sticky=E)
    edition_var_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')

    # function to automatically grab edition based off of file name
    def check_edition_function():
        if encode_file_path.get().strip() != '' and pathlib.Path(encode_file_path.get()).is_file():
            edition_check = re.search('collector.*edition|director.*cut|extended.*cut|limited.*edition|s'
                                      'pecial.*edition|theatrical.*cut|uncut|unrated',
                                      pathlib.Path(encode_file_path.get()).stem, re.IGNORECASE)
            if edition_check:
                if 'collector' in str(edition_check.group()).lower():
                    edition_var.set("Collector's Edition")
                elif 'director' in str(edition_check.group()).lower():
                    edition_var.set("Director's Cut")
                elif 'extended' in str(edition_check.group()).lower():
                    edition_var.set("Extended Cut")
                elif 'limited' in str(edition_check.group()).lower():
                    edition_var.set("Limited Edition")
                elif 'special' in str(edition_check.group()).lower():
                    edition_var.set("Special Edition")
                elif 'theatrical' in str(edition_check.group()).lower():
                    edition_var.set("Theatrical Cut")
                elif 'uncut' in str(edition_check.group()).lower():
                    edition_var.set("Uncut")
                elif 'unrated' in str(edition_check.group()).lower():
                    edition_var.set("Unrated")

    check_edition_function()  # run function to check edition upon opening the window automatically

    # custom edition label and entry box
    edition_label = Label(upload_options_frame, text='Edition\n(Custom)', bd=0, relief=SUNKEN, background='#363636',
                          fg="#3498db", font=(set_font, set_font_size + 1))
    edition_label.grid(column=0, row=1, columnspan=1, pady=(5, 0), padx=5, sticky=E)

    edition_entry_box = Entry(upload_options_frame, borderwidth=4, bg="#565656", fg='white',
                              disabledforeground='white', disabledbackground="#565656")
    edition_entry_box.grid(row=1, column=1, columnspan=5, padx=5, pady=(5, 0), sticky=E + W)

    # a constant function to check if user types in the custom edition box, this set's edition to N/A and accepts text
    def reset_disable_set_edition():
        if edition_entry_box.get().strip() != '':
            edition_var.set("N/A")
            edition_var_menu.config(state=DISABLED)
        else:
            edition_var_menu.config(state=NORMAL)
            check_edition_function()
        upload_window.after(50, reset_disable_set_edition)

    reset_disable_set_edition()  # launch loop to check edition

    # IMDB and TMDB frame
    imdb_tmdb_frame = LabelFrame(upload_window, text=' IMDB / TMDB ', labelanchor="nw")
    imdb_tmdb_frame.grid(column=0, row=2, columnspan=8, padx=5, pady=(5, 3), sticky=E + W)
    imdb_tmdb_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    imdb_tmdb_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_frame.grid_rowconfigure(1, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(0, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(1, weight=300)
    imdb_tmdb_frame.grid_columnconfigure(7, weight=1)

    # search frame inside the IMDB and TMDB frame
    imdb_tmdb_search_frame = LabelFrame(imdb_tmdb_frame, text=' Search ', labelanchor="n")
    imdb_tmdb_search_frame.grid(column=0, row=0, columnspan=8, padx=5, pady=(5, 3), sticky=E + W)
    imdb_tmdb_search_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 9, 'bold'))
    imdb_tmdb_search_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_search_frame.grid_columnconfigure(0, weight=1)

    # search entry box
    search_entry_box = Entry(imdb_tmdb_search_frame, borderwidth=4, bg="#565656", fg='white',
                             disabledforeground='white', disabledbackground="#565656", textvariable=movie_search_var)
    search_entry_box.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 0), sticky=E + W)

    # if encode file is loaded, parse the name of the file to get autoload it into the search box for the user
    if pathlib.Path(encode_file_path.get()).stem != '':
        search_entry_box.delete(0, END)  # clear the search box
        # use regex to find the movie name
        movie_name = re.finditer(r'\d{4}(?!p)', pathlib.Path(encode_file_path.get()).stem, re.IGNORECASE)
        movie_name_extraction = []  # create empty list
        for match in movie_name:  # get the "span" from the movie name
            movie_name_extraction.append(match.span())
        # extract the full movie name (removing anything that is not needed from the filename)
        full_movie_name = pathlib.Path(encode_file_path.get()).stem[0:int(
            movie_name_extraction[-1][-1])].replace('.', ' ').strip()
        search_entry_box.insert(END, full_movie_name)  # insert this full movie name into the search box

    # # function to search tmdb for information
    def call_search_command(*enter_args):
        if search_entry_box.get().strip() != '':
            upload_window.wm_withdraw()
            search_movie_global_function(search_entry_box.get().strip())
            upload_window.wm_deiconify()

    # search button and bind to use command from "Enter" key
    search_entry_box.bind("<Return>", call_search_command)
    search_button = HoverButton(imdb_tmdb_search_frame, text="Search", activebackground="#23272A",
                                command=call_search_command,
                                foreground="white", background="#23272A",
                                borderwidth="3", activeforeground="#3498db", width=12)
    search_button.grid(row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # imdb label
    imdb_label = Label(imdb_tmdb_frame, text='IMDB ID\n(Required)', background='#363636',
                       fg="#3498db", font=(set_font, set_font_size + 1))
    imdb_label.grid(column=0, row=1, columnspan=1, pady=(5, 0), padx=5, sticky=W)

    # imdb entry box
    imdb_entry_box = Entry(imdb_tmdb_frame, borderwidth=4, bg="#565656", fg='white',
                           disabledforeground='white', disabledbackground="#565656", textvariable=imdb_id_var)
    imdb_entry_box.grid(row=1, column=1, columnspan=6, padx=5, pady=(5, 0), sticky=E + W)

    # decode imdb img for use with the buttons
    decode_resize_imdb_image = Image.open(BytesIO(base64.b64decode(imdb_icon))).resize((35, 35))
    imdb_img = ImageTk.PhotoImage(decode_resize_imdb_image)

    # upload window imdb button with decoded image
    imdb_button = Button(imdb_tmdb_frame, image=imdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                         activebackground="#363636", command=open_imdb_link)
    imdb_button.grid(row=1, column=7, columnspan=1, padx=5, pady=(5, 0), sticky=W)
    imdb_button.photo = imdb_img

    # tmdb label
    tmdb_label = Label(imdb_tmdb_frame, text='TMDB ID\n(Required)', background='#363636',
                       fg="#3498db", font=(set_font, set_font_size + 1))
    tmdb_label.grid(column=0, row=2, columnspan=1, pady=(5, 0), padx=5, sticky=W)

    # tmdb upload window entry box
    tmdb_entry_box = Entry(imdb_tmdb_frame, borderwidth=4, bg="#565656", fg='white',
                           disabledforeground='white', disabledbackground="#565656", textvariable=tmdb_id_var)
    tmdb_entry_box.grid(row=2, column=1, columnspan=6, padx=5, pady=(5, 0), sticky=E + W)

    # decode tmdb img for use with the buttons
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(tmdb_icon))).resize((35, 35))
    tmdb_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # tmdb clickable icon button in upload window with decoded image
    tmdb_button = Button(imdb_tmdb_frame, image=tmdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                         activebackground="#363636", command=open_tmdb_link)
    tmdb_button.grid(row=2, column=7, columnspan=1, padx=5, pady=(5, 0), sticky=W)
    tmdb_button.photo = tmdb_img

    # info frame
    info_frame = LabelFrame(upload_window, text=' Info ', labelanchor="nw")
    info_frame.grid(column=0, row=4, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    info_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    info_frame.grid_rowconfigure(0, weight=1)
    info_frame.grid_columnconfigure(0, weight=1)
    info_frame.grid_columnconfigure(1, weight=100)
    info_frame.grid_columnconfigure(2, weight=1)
    info_frame.grid_columnconfigure(3, weight=100)

    # function when media info video file is dropped/opened, it's given a variable when called
    def update_media_info_function(m_i_input):
        # if input is *.txt
        if pathlib.Path(m_i_input).suffix == '.txt':
            # open file and set variable
            with open(pathlib.Path(m_i_input), mode='rt', encoding="utf-8") as m_i_file:
                encode_media_info.set(m_i_file.read())
        # if input is *.mp4
        elif pathlib.Path(m_i_input).suffix == '.mp4':
            # parse file with mediainfo to txt and set variable
            m_i_dropped = MediaInfo.parse(pathlib.Path(m_i_input), full=False, output="")  # parse mediainfo
            encode_media_info.set(m_i_dropped)
        media_info_entry.config(state=NORMAL)  # enable entry box
        media_info_entry.delete(0, END)  # clear entry box
        media_info_entry.insert(END, 'MediaInfo loaded from file')  # insert string
        media_info_entry.config(state=DISABLED)  # disable entry box

    # function for dropped/open nfo input from txt/nfo file
    def update_nfo_desc_function(nfo_desc_input):
        # open nfo file and set it as variable
        with open(pathlib.Path(nfo_desc_input), mode='rt', encoding="utf-8") as nfo_file_open:
            nfo_info_var.set(nfo_file_open.read())
        nfo_desc_entry.config(state=NORMAL)  # enable entry box
        nfo_desc_entry.delete(0, END)  # clear entry box
        nfo_desc_entry.insert(END, 'NFO loaded from file')  # insert string
        nfo_desc_entry.config(state=DISABLED)  # disable entry box

    # torrent drag and drop function for media info and torrent files
    def media_info_nfo_drop_function(event):
        m_i_nfo_drop = [x for x in root.splitlist(event.data)][0]  # dropped path to file
        # if file is *.mp4, call update media info func
        if pathlib.Path(m_i_nfo_drop).suffix == '.mp4':
            update_media_info_function(m_i_nfo_drop)
        # if file is *.nfo or *.txt, call update nfo func
        elif pathlib.Path(m_i_nfo_drop).suffix == '.nfo' or pathlib.Path(m_i_nfo_drop).suffix == '.txt':
            update_nfo_desc_function(m_i_nfo_drop)

    # bind frame to drop media info and torrent files
    info_frame.drop_target_register(DND_FILES)
    info_frame.dnd_bind('<<Drop>>', media_info_nfo_drop_function)

    # manual media info dialog, this accepts txt and .mp4
    def open_media_info_text():
        # define parser
        mediainfo_input_parser = ConfigParser()
        mediainfo_input_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(mediainfo_input_parser['last_used_folder']['path']).is_dir():
            mi_save_dir = pathlib.Path(mediainfo_input_parser['last_used_folder']['path'])
        else:
            mi_save_dir = '/'

        # get media info input
        m_i_t = filedialog.askopenfilename(parent=upload_window, title='Select Mediainfo File', initialdir=mi_save_dir,
                                           filetypes=[("Text, MP4", "*.txt *.mp4")])
        if m_i_t:  # if selection is made, run the media info function
            update_media_info_function(m_i_t)

    # media info button
    media_info_button = HoverButton(info_frame, text="MediaInfo", command=open_media_info_text, foreground="white",
                                    background="#23272A", borderwidth="3", activeforeground="#3498db", width=15,
                                    activebackground="#23272A")
    media_info_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N)

    # media info entry box
    media_info_entry = Entry(info_frame, borderwidth=4, bg="#565656", fg='white',
                             disabledforeground='white', disabledbackground="#565656", state=DISABLED)
    media_info_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=(5, 0), sticky=E + W)
    # if automatic work flow is set and encode media info is not blank, assume it's been automatically loaded
    if automatic_workflow_boolean and encode_media_info.get() != '':
        media_info_entry.config(state=NORMAL)  # enable entry box
        media_info_entry.delete(0, END)  # clear entry box
        media_info_entry.insert(END, 'MediaInfo Loaded Internally')  # insert string
        media_info_entry.config(state=DISABLED)  # disable entry box

    # manual nfo open dialog, this accepts *.txt and *.nfo files
    def open_nfo_info_text_nfo():
        # define parser
        open_nfo_parser = ConfigParser()
        open_nfo_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(open_nfo_parser['last_used_folder']['path']).is_dir():
            nfo_initial_save_dir = pathlib.Path(open_nfo_parser['last_used_folder']['path'])
        else:
            nfo_initial_save_dir = '/'

        # nfo/description open prompt
        nfo_desc = filedialog.askopenfilename(parent=upload_window, title='Select NFO', initialdir=nfo_initial_save_dir,
                                              filetypes=[("NFO, Text", "*.txt *.nfo")])
        if nfo_desc:  # if selection is made, run the nfo function
            update_nfo_desc_function(nfo_desc)

    # nfo load button
    nfo_desc_button = HoverButton(info_frame, text="NFO / Description", command=open_nfo_info_text_nfo,
                                  foreground="white", background="#23272A", borderwidth="3",
                                  activeforeground="#3498db", width=15, activebackground="#23272A")
    nfo_desc_button.grid(row=0, column=2, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # nfo entry
    nfo_desc_entry = Entry(info_frame, borderwidth=4, bg="#565656", fg='white',
                           disabledforeground='white', disabledbackground="#565656", state=DISABLED)
    nfo_desc_entry.grid(row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=E + W)
    # if automatic work flow is set and nfo info is not blank, assume it's been automatically loaded
    if automatic_workflow_boolean and nfo_info_var.get() != '':
        nfo_desc_entry.config(state=NORMAL)
        nfo_desc_entry.insert(END, 'NFO Loaded Internally')
        nfo_desc_entry.config(state=DISABLED)

    # misc options frame
    misc_options_frame = LabelFrame(upload_window, text=' Upload Options ', labelanchor="nw")
    misc_options_frame.grid(column=0, row=5, columnspan=3, padx=5, pady=(5, 3), sticky=E + W)
    misc_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, set_font_size + 1, 'bold'))
    misc_options_frame.grid_rowconfigure(0, weight=1)
    for m_o_f in range(3):
        misc_options_frame.grid_columnconfigure(m_o_f, weight=1)

    # live checkbox, set to on, this is a permanent choice
    def update_checkbutton_info():
        chk_button_parser = ConfigParser()
        chk_button_parser.read(config_file)
        if live_boolean.get():
            save_checkbutton = 1
        elif not live_boolean.get():
            save_checkbutton = 0
        chk_button_parser.set('live_release', 'value', str(save_checkbutton))
        with open(config_file, 'w') as c_b_config:
            chk_button_parser.write(c_b_config)

    live_checkbox = Checkbutton(misc_options_frame, text='Send to Drafts', variable=live_boolean, state=DISABLED,
                                onvalue=0, offvalue=1, command=update_checkbutton_info)
    live_checkbox.grid(row=0, column=0, padx=5, pady=(5, 3), sticky=E + W)
    live_checkbox.configure(background="#363636", foreground="white", activebackground="#363636",
                            activeforeground="white", selectcolor="#363636",
                            font=(set_font, set_font_size + 1))
    live_boolean.set(0)

    # parser to check for password and remember settings if enabled
    live_temp_parser = ConfigParser()
    live_temp_parser.read(config_file)
    # if sticky gives users the password to live release
    if live_temp_parser['live_release']['password'] == "StickySaidSo":
        live_checkbox.config(state=NORMAL)  # enable check button
        try:  # try to set check button based off of config
            live_boolean.set(int(live_temp_parser['live_release']['value']))
        except ValueError:  # if check button is blank or value error
            live_boolean.set(0)  # set it to the default 0

    anonymous_checkbox = Checkbutton(misc_options_frame, text='Anonymous', variable=anonymous_boolean, onvalue=1,
                                     offvalue=0)
    anonymous_checkbox.grid(row=0, column=1, padx=5, pady=(5, 3), sticky=W)
    anonymous_checkbox.configure(background="#363636", foreground="white", activebackground="#363636",
                                 activeforeground="white", selectcolor="#363636",
                                 font=(set_font, set_font_size + 1))
    anonymous_boolean.set(0)

    # upload to beyond hd api function
    def upload_to_api():
        # set config parser
        api_parser = ConfigParser()
        api_parser.read(config_file)

        # upload status window
        upload_status_window = Toplevel()
        upload_status_window.configure(background="#363636")
        upload_status_window.geometry(f'{460}x{200}+{str(int(upload_window.geometry().split("+")[1]) + 156)}+'
                                      f'{str(int(upload_window.geometry().split("+")[2]) + 230)}')
        upload_status_window.resizable(False, False)
        upload_status_window.grab_set()
        upload_status_window.wm_overrideredirect(True)
        upload_window.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
        upload_status_window.grid_rowconfigure(0, weight=1)
        upload_status_window.grid_columnconfigure(0, weight=1)

        # encoder name frame
        upload_output_frame = Frame(upload_status_window, highlightbackground="white", highlightthickness=2,
                                    bg="#363636", highlightcolor='white')
        upload_output_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        for e_n_f in range(3):
            upload_output_frame.grid_columnconfigure(e_n_f, weight=1)
            upload_output_frame.grid_rowconfigure(e_n_f, weight=1)

        # create window
        upload_status_info = scrolledtextwidget.ScrolledText(upload_output_frame, height=7, bg='#565656',
                                                             fg='white', bd=4, wrap=WORD)
        upload_status_info.grid(row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W)
        upload_status_info.insert(END, 'Uploading, please wait...')
        upload_status_info.config(state=DISABLED)

        # function to save new name to config.ini
        def encoder_okay_func():
            upload_window.wm_attributes('-alpha', 1.0)  # restore transparency
            upload_status_window.destroy()  # close window

        # create 'OK' button
        uploader_okay_btn = HoverButton(upload_output_frame, text="OK", command=encoder_okay_func,
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=8, activebackground="#23272A")
        uploader_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=E)

        # if live boolean is True
        if live_boolean.get():
            live_release = 1
        # if live boolean is False
        elif not live_boolean.get():
            live_release = 0

        # if anon boolean is True
        if anonymous_boolean.get():
            anonymous_release = 1
        # if anon boolean is False
        elif not anonymous_boolean.get():
            anonymous_release = 0

        # api link
        api_link = f"https://beyond-hd.me/api/upload/{api_parser['bhd_upload_api']['key']}"

        # define upload params for BHD
        upload_payload_params = {"name": title_input_entry_box.get().strip(),
                                 "category_id": 1, "type": type_choices[type_var.get()],
                                 "source": source_choices[source_var.get()], "internal": 1,
                                 "imdb_id": imdb_id_var.get(), "tmdb_id": tmdb_id_var.get(),
                                 "description": nfo_info_var.get(), "nfo": nfo_info_var.get(),
                                 "live": live_release, "anon": anonymous_release,
                                 "stream": "optimized", "promo": 2}

        # if any preset edition selections are selected add the params and value
        if edition_var.get() != 'N/A':
            upload_payload_params.update({"edition": edition_choices[edition_var.get()]})

        # if a custom edition is typed add the params and value
        if edition_entry_box.get().strip() != '':
            upload_payload_params.update({"custom_edition": edition_entry_box.get().strip()})

        # upload function in a different thread
        def run_upload_in_different_thread():
            try:  # try to upload
                upload_job = requests.post(api_link, upload_payload_params,
                                           files={'file': open(pathlib.Path(torrent_file_path.get()), 'rb'),
                                                  "mediainfo": encode_media_info.get()})
            except requests.exceptions.ConnectionError:  # if there is a connection error show function
                encoder_okay_func()  # this runs the okay button function to close the window and restore transparency
                messagebox.showerror(parent=upload_window, title='Error', message='There is a connection error, check '
                                                                                  'your internet connection')
                return  # exit the function

            upload_status_info.config(state=NORMAL)  # enable scrolled text box
            upload_status_info.delete("1.0", END)  # delete all contents of the box
            if upload_job.status_code == 200:  # if upload returns a status code '200', assume success
                if upload_job.json()['status_code'] == 1 and 'saved' in upload_job.json()['status_message'] \
                        and upload_job.json()['success']:
                    upload_status_info.insert(END, 'Upload is successful!\n\nUpload has been successfully '
                                                   'saved as a draft on site')
                else:
                    upload_status_info.insert(END, f"There was an error:\n\n{upload_job.json()['status_message']}")
            elif upload_job.status_code == 404:  # if upload returns a status code '400', site error
                upload_status_info.insert(END, f"Upload failed! This is likely a problem with the site\n\n"
                                               f"{upload_job.json()['status_message']}")
            elif upload_job.status_code == 500:  # if upload returns a status code '400', critical site error
                upload_status_info.insert(END, "Error!\n\nThe site isn't returning the upload status.\n"
                                               "This is a critical error from the site.\n"
                                               f"Status code:{str(upload_job.status_code)}")
            else:  # if it returns any other status code, raise a pythonic error to be shown and print unknown error
                upload_status_info.insert(END, 'Unknown error!')
                upload_job.raise_for_status()
            upload_status_info.config(state=DISABLED)  # disable scrolled textbox

        # start upload in a thread
        threading.Thread(target=run_upload_in_different_thread).start()

    # enabled upload img
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(bhd_upload_icon))).resize((120, 45))
    upload_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # disabled upload img
    decode_resize_tmdb_image2 = Image.open(BytesIO(base64.b64decode(bhd_upload_icon_disabled))).resize((120, 45))
    upload_img_disabled = ImageTk.PhotoImage(decode_resize_tmdb_image2)

    upload_button = HoverButton(upload_window, text="Upload", image=upload_img_disabled,
                                background="#363636", borderwidth=0, activebackground="#363636",
                                cursor='question_arrow')
    upload_button.grid(row=5, column=3, padx=(5, 10), pady=(5, 10), sticky=E + S)
    upload_button.image = upload_img_disabled

    # function to define and display missing inputs
    def show_missing_input():
        missing_list = []  # create empty missing list
        if torrent_file_path.get() == '':
            missing_list.append('Torrent Input')
        if title_input_entry_box.get().strip() == '':
            missing_list.append('Title')
        if type_var.get() == '':
            missing_list.append('Type')
        if source_var.get() == '':
            missing_list.append('Source')
        if imdb_id_var.get().strip() == '':
            missing_list.append('IMDB ID')
        if tmdb_id_var.get().strip() == '':
            missing_list.append('TMDB ID')
        if encode_media_info.get() == '':
            missing_list.append('MediaInfo')
        if nfo_info_var.get() == '':
            missing_list.append('NFO/Description')

        # open messagebox with all the missing inputs
        messagebox.showinfo(parent=upload_window, title='Missing Input',
                            message=f"Missing inputs:\n\n{', '.join(missing_list)}")

    # function to check for missing variables and enable/change button and button commands
    def enable_disable_upload_button():
        # if everything is needed in the window, enable upload button
        if torrent_file_path.get() != '' and title_input_entry_box.get().strip() != '' and type_var.get() != '' and \
                source_var.get() != '' and imdb_id_var.get().strip() != '' and tmdb_id_var.get().strip() != '' and \
                encode_media_info.get() != '' and nfo_info_var.get() != '':
            upload_button.config(image=upload_img)
            upload_button.image = upload_img
            upload_button.config(command=upload_to_api, cursor='hand2')
        else:  # if 1 item is missing, disable upload button and enable show missing input function
            upload_button.config(image=upload_img_disabled)
            upload_button.image = upload_img_disabled
            upload_button.config(command=show_missing_input, cursor='question_arrow')
        upload_window.after(50, enable_disable_upload_button)  # loop to check this constantly

    # start loop
    enable_disable_upload_button()


# open torrent window button
open_uploader_button = HoverButton(manual_workflow, text="Uploader", state=DISABLED,
                                   command=lambda: [automatic_workflow_boolean.set(False),
                                                    open_uploader_window('manual')],
                                   foreground="white", background="#23272A", borderwidth="3", width=15,
                                   activeforeground="#3498db", activebackground="#23272A")
open_uploader_button.grid(row=0, column=2, columnspan=1, padx=(5, 10), pady=1, sticky=E + W)


# automatic work flow button
def auto_workflow():
    # check screens
    check_screens = parse_screen_shots()
    if not check_screens:  # if returned false, show error message and exit this function
        messagebox.showerror(parent=root, title='Error!', message='Missing or incorrectly formatted screenshots\n\n'
                                                                  'Screen shots need to be in multiples of 2')
        return
    torrent_function_window()  # if passed run torrent function
    if not automatic_workflow_boolean.get():  # if returned false, exit this function back to main GUI
        return
    open_nfo_viewer()  # if passed run nfo viewer function
    if not automatic_workflow_boolean.get():  # if returned false, exit this function back to main GUI
        return
    open_uploader_window('auto')  # if it passes all the automatic requirements, open upload window in 'auto' mode


# parse and upload button
parse_and_upload = HoverButton(automatic_workflow, text="Parse & Upload", state=DISABLED,
                               command=lambda: [automatic_workflow_boolean.set(True), auto_workflow()],
                               foreground="white", background="#23272A", borderwidth="3",
                               activeforeground="#3498db", width=1, activebackground="#23272A")
parse_and_upload.grid(row=0, column=0, columnspan=1, padx=10, pady=1, sticky=E + W)


# Hide/Open all top level window function -----------------------------------------------------------------------------
def hide_all_toplevels():
    for widget in root.winfo_children():
        if isinstance(widget, Toplevel):
            widget.withdraw()


def open_all_toplevels():
    for widget in root.winfo_children():
        if isinstance(widget, Toplevel):
            widget.deiconify()


# ----------------------------------------------------------------------------- Hide/Open all top level window function

# function to check state of root, then deiconify it accordingly ------------------------------------------------------
def advanced_root_deiconify():
    if root.winfo_viewable():
        root.deiconify()
    elif not root.winfo_viewable():
        root.iconify()
        root.deiconify()


# ------------------------------------------------------ function to check state of root, then deiconify it accordingly

# reset gui -----------------------------------------------------------------------------------------------------------
def reset_gui():
    delete_source_entry()
    delete_encode_entry()
    image_listbox.config(state=NORMAL)
    image_listbox.delete(0, END)
    image_listbox.config(state=DISABLED)
    screenshot_scrolledtext.delete("1.0", END)
    tabs.select(image_tab)
    clear_all_variables()


# ----------------------------------------------------------------------------------------------------------- reset gui

# reset settings ------------------------------------------------------------------------------------------------------
def reset_all_settings():
    reset_settings = messagebox.askyesno(title='Prompt', message='Are you sure you want to reset all settings?')

    # if user presses yes
    if reset_settings:
        pathlib.Path(config_file).unlink(missing_ok=True)
        pathlib.Path('Runtime/user.bin').unlink(missing_ok=True)
        pathlib.Path('Runtime/pass.bin').unlink(missing_ok=True)
        messagebox.showinfo(title='Prompt', message='Settings are reset, program will restart automatically')

        # close root window
        root.destroy()

        # re-open the program
        subprocess.run(pathlib.Path().cwd() / "BHDStudioUploadTool.exe")  # use subprocess.run to restart


# ------------------------------------------------------------------------------------------------------ reset settings

# menu Items and Sub-Bars ---------------------------------------------------------------------------------------------
my_menu_bar = Menu(root, tearoff=0)
root.config(menu=my_menu_bar)

file_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='File', menu=file_menu)

file_menu.add_command(label='Open Source File', command=manual_source_input, accelerator="[Ctrl+O]")
root.bind("<Control-s>", lambda event: manual_source_input())
file_menu.add_command(label='Open Encode File', command=manual_encode_input, accelerator="[Ctrl+E]")
root.bind("<Control-e>", lambda event: manual_encode_input())
file_menu.add_separator()
file_menu.add_command(label='Open StaxRip Temp', command=staxrip_manual_open, accelerator="[Ctrl+S]")
root.bind("<Control-s>", lambda event: staxrip_manual_open())
file_menu.add_separator()
file_menu.add_command(label='Reset GUI', command=reset_gui, accelerator="[Ctrl+R]")
root.bind("<Control-r>", lambda event: reset_gui())
file_menu.add_command(label='Exit', command=root_exit_function, accelerator="[Alt+F4]")


# custom input box that accepts parent window, label, config option, and config key
def custom_input_prompt(parent_window, label_input, config_option, config_key, hide_show):
    # hide all top levels if they are opened
    hide_all_toplevels()
    # set parser
    custom_input_parser = ConfigParser()
    custom_input_parser.read(config_file)

    # encoder name window
    custom_input_window = Toplevel()
    custom_input_window.title('')
    custom_input_window.configure(background="#363636")
    custom_input_window.geometry(f'{260}x{140}+{str(int(parent_window.geometry().split("+")[1]) + 220)}+'
                                 f'{str(int(parent_window.geometry().split("+")[2]) + 230)}')
    custom_input_window.resizable(False, False)
    custom_input_window.grab_set()
    custom_input_window.protocol('WM_DELETE_WINDOW', lambda: custom_okay_func())
    parent_window.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
    custom_input_window.grid_rowconfigure(0, weight=1)
    custom_input_window.grid_columnconfigure(0, weight=1)

    # encoder name frame
    custom_input_frame = Frame(custom_input_window, highlightbackground="white", highlightthickness=2, bg="#363636",
                               highlightcolor='white')
    custom_input_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        custom_input_frame.grid_columnconfigure(e_n_f, weight=1)
        custom_input_frame.grid_rowconfigure(e_n_f, weight=1)

    # create label
    image_name_label3 = Label(custom_input_frame, text=label_input, background='#363636', fg="#3498db",
                              font=(set_font, set_font_size, "bold"))
    image_name_label3.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

    # create entry box
    custom_entry_box = Entry(custom_input_frame, borderwidth=4, bg="#565656", fg='white')
    custom_entry_box.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky=E + W)
    custom_entry_box.insert(END, custom_input_parser[config_option][config_key])
    # if api key is called
    if hide_show == 'hide':
        custom_entry_box.config(show='*')
        custom_entry_box.bind('<Enter>', lambda event: custom_entry_box.config(show=''))
        custom_entry_box.bind('<Leave>', lambda event: custom_entry_box.config(show='*'))

    # function to save new name to config.ini
    def custom_okay_func():
        if custom_input_parser[config_option][config_key] != custom_entry_box.get().strip():
            custom_input_parser.set(config_option, config_key, custom_entry_box.get().strip())
            with open(config_file, 'w') as encoder_name_config_file:
                custom_input_parser.write(encoder_name_config_file)
        parent_window.wm_attributes('-alpha', 1.0)  # restore transparency
        custom_input_window.destroy()  # close window

    # create 'OK' button
    custom_okay_btn = HoverButton(custom_input_frame, text="OK", command=custom_okay_func, foreground="white",
                                  background="#23272A", borderwidth="3", activeforeground="#3498db", width=8,
                                  activebackground="#23272A")
    custom_okay_btn.grid(row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    # create 'Cancel' button
    custom_cancel_btn = HoverButton(custom_input_frame, text="Cancel", activeforeground="#3498db", width=8,
                                    command=lambda: [custom_input_window.destroy(),
                                                     root.wm_attributes('-alpha', 1.0)],
                                    foreground="white", background="#23272A", borderwidth="3",
                                    activebackground="#23272A")
    custom_cancel_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    custom_input_window.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist


# define default torrent path window
def torrent_path_window_function(*t_args):
    # hide all top levels if they are opened
    hide_all_toplevels()
    # define parser
    torrent_window_path_parser = ConfigParser()
    torrent_window_path_parser.read(config_file)

    # function to exit torrent path window
    def torrent_path_okay_func():
        root.wm_attributes('-alpha', 1.0)  # restore transparency
        torrent_path_window.destroy()  # close window

    # torrent path window
    torrent_path_window = Toplevel()
    torrent_path_window.title('')
    torrent_path_window.configure(background="#363636")
    torrent_path_window.geometry(f'{460}x{160}+{str(int(root.geometry().split("+")[1]) + 156)}+'
                                 f'{str(int(root.geometry().split("+")[2]) + 230)}')
    torrent_path_window.resizable(False, False)
    torrent_path_window.grab_set()
    torrent_path_window.protocol('WM_DELETE_WINDOW', torrent_path_okay_func)
    root.wm_attributes('-alpha', 0.92)  # set parent window to be slightly transparent
    torrent_path_window.grid_rowconfigure(0, weight=1)
    torrent_path_window.grid_columnconfigure(0, weight=1)

    # encoder name frame
    torrent_path_frame = Frame(torrent_path_window, highlightbackground="white", highlightthickness=2, bg="#363636",
                               highlightcolor='white')
    torrent_path_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)

    # grid and row config
    for e_n_f in range(4):
        torrent_path_frame.grid_columnconfigure(e_n_f, weight=1)
        torrent_path_frame.grid_rowconfigure(e_n_f, weight=1)
    torrent_path_frame.grid_columnconfigure(1, weight=100)
    torrent_path_frame.grid_rowconfigure(2, weight=50)

    # create label
    torrent_label = Label(torrent_path_frame, text="Torrent Output Path", background='#363636', fg="#3498db",
                          font=(set_font, set_font_size, "bold"))
    torrent_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 8))

    # set torrent default path function
    def save_default_torrent_path():
        # save directory dialog box
        torrent_path_dialogue = filedialog.askdirectory(parent=torrent_path_window, title="Set Default Path")
        # if directory is defined
        if torrent_path_dialogue:
            # define parser/settings then write to config file
            torrent_path_update_parser = ConfigParser()
            torrent_path_update_parser.read(config_file)
            torrent_path_update_parser.set('torrent_settings', 'default_path', str(pathlib.Path(torrent_path_dialogue)))
            with open(config_file, 'w') as t_p_configfile:
                torrent_path_update_parser.write(t_p_configfile)
            # update entry box
            torrent_path_entry_box.config(state=NORMAL)
            torrent_path_entry_box.delete(0, END)
            torrent_path_entry_box.insert(END, str(pathlib.Path(torrent_path_dialogue)))
            torrent_path_entry_box.config(state=DISABLED)
            # update torrent_file_path string var
            if torrent_file_path.get() != '':
                torrent_file_path.set(str(pathlib.Path(torrent_path_update_parser['torrent_settings']['default_path'])
                                          / pathlib.Path(pathlib.Path(torrent_file_path.get()).stem
                                                         ).with_suffix('.torrent')))

    # create torrent path button
    torrent_path_btn = HoverButton(torrent_path_frame, text="Path", command=save_default_torrent_path,
                                   background="#23272A", borderwidth="3", activeforeground="#3498db", width=8,
                                   activebackground="#23272A", foreground="white")
    torrent_path_btn.grid(row=1, column=0, columnspan=1, padx=(5, 2), pady=5, sticky=W)

    # create entry box
    torrent_path_entry_box = Entry(torrent_path_frame, borderwidth=4, bg="#565656", fg='white',
                                   disabledbackground="#565656", disabledforeground="light grey")
    torrent_path_entry_box.grid(row=1, column=1, columnspan=2, padx=0, pady=5, sticky=E + W)
    torrent_path_entry_box.insert(END, torrent_window_path_parser['torrent_settings']['default_path'])
    torrent_path_entry_box.config(state=DISABLED)

    # reset path function
    def reset_torrent_path_function():
        # confirm reset
        confirm_reset = messagebox.askyesno(parent=torrent_path_window, title='Confirm',
                                            message='Are you sure you want to reset path back to default?\n'
                                                    '(Encode file input path)')
        # if user presses yes
        if confirm_reset:
            # define parser/settings then write to config file
            reset_path_parser = ConfigParser()
            reset_path_parser.read(config_file)
            reset_path_parser.set('torrent_settings', 'default_path', '')
            with open(config_file, 'w') as t_r_configfile:
                reset_path_parser.write(t_r_configfile)
            # update entry box
            torrent_path_entry_box.config(state=NORMAL)
            torrent_path_entry_box.delete(0, END)
            torrent_path_entry_box.config(state=DISABLED)
            # update torrent_file_path string var if encode_file_path is loaded
            if encode_file_path.get() != '':
                torrent_file_path.set(str(pathlib.Path(encode_file_path.get()).with_suffix('.torrent')))

    # create torrent reset path button
    torrent_path_reset_btn = HoverButton(torrent_path_frame, text="X", command=reset_torrent_path_function,
                                         background="#23272A", borderwidth="3", activeforeground="#3498db", width=3,
                                         activebackground="#23272A", foreground="white")
    torrent_path_reset_btn.grid(row=1, column=3, columnspan=1, padx=(2, 5), pady=5, sticky=E)

    # create 'OK' button
    torrent_path_okay_btn = HoverButton(torrent_path_frame, text="OK", command=torrent_path_okay_func,
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=8, activebackground="#23272A")
    torrent_path_okay_btn.grid(row=2, column=2, columnspan=2, padx=7, pady=(5, 3), sticky=E + S)

    torrent_path_window.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist


# beyondhd.co login credentials
def bhd_co_login_window():
    # hide all top levels if they are opened
    hide_all_toplevels()

    # function to save new name to config.ini
    def save_exit_function():
        # get user and pass to encrypt and save
        user_pass_encoder = Fernet(crypto_key)
        encode_user = user_pass_encoder.encrypt(str(user_entry_box.get()).strip().encode())
        encode_password = user_pass_encoder.encrypt(str(pass_entry_box.get()).strip().encode())

        # write encrypted data to config
        with open('Runtime/user.bin', 'wb') as user_bin, open('Runtime/pass.bin', 'wb') as pass_bin:
            # write info to user and password bins
            user_bin.write(encode_user)
            pass_bin.write(encode_password)

        # restore transparency
        root.wm_attributes('-alpha', 1.0)
        # close window
        bhd_login_win.destroy()

    # encoder name window
    bhd_login_win = Toplevel()
    bhd_login_win.title('')
    bhd_login_win.configure(background="#363636")
    bhd_login_win.geometry(f'{300}x{210}+{str(int(root.geometry().split("+")[1]) + 220)}+'
                           f'{str(int(root.geometry().split("+")[2]) + 230)}')
    bhd_login_win.resizable(False, False)
    bhd_login_win.grab_set()
    bhd_login_win.protocol('WM_DELETE_WINDOW', save_exit_function)
    root.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
    bhd_login_win.grid_rowconfigure(0, weight=1)
    bhd_login_win.grid_columnconfigure(0, weight=1)

    # encoder name frame
    bhd_login_frame = Frame(bhd_login_win, highlightbackground="white", highlightthickness=2, bg="#363636",
                            highlightcolor='white')
    bhd_login_frame.grid(column=0, row=0, columnspan=5, sticky=N + S + E + W)
    for e_n_f in range(5):
        bhd_login_frame.grid_columnconfigure(e_n_f, weight=1)
        bhd_login_frame.grid_rowconfigure(e_n_f, weight=1)

    # create label
    user_label = Label(bhd_login_frame, text='Username', background='#363636', fg="#3498db",
                       font=(set_font, set_font_size, "bold"))
    user_label.grid(row=0, column=0, columnspan=5, sticky=W + N, padx=5, pady=(2, 0))

    # create username entry box
    user_entry_box = Entry(bhd_login_frame, borderwidth=4, bg="#565656", fg='white')
    user_entry_box.grid(row=1, column=0, columnspan=5, padx=10, pady=(0, 5), sticky=E + W)

    # create label
    pass_label = Label(bhd_login_frame, text='Password', background='#363636', fg="#3498db",
                       font=(set_font, set_font_size, "bold"))
    pass_label.grid(row=2, column=0, columnspan=5, sticky=W + N, padx=5, pady=(2, 0))

    # create password entry box
    pass_entry_box = Entry(bhd_login_frame, borderwidth=4, bg="#565656", fg='white', show='*')
    pass_entry_box.grid(row=3, column=0, columnspan=5, padx=10, pady=(0, 5), sticky=E + W)
    pass_entry_box.bind('<Enter>', lambda event: pass_entry_box.config(show=''))
    pass_entry_box.bind('<Leave>', lambda event: pass_entry_box.config(show='*'))

    # custom_entry_box.insert(END, custom_input_parser[config_option][config_key])

    # function to check login credentials
    def check_bhd_login():
        # login to beyondhd image host to confirm username and password
        # start requests session
        session = requests.session()

        # get raw text of web page
        try:
            auth_raw = session.get("https://beyondhd.co/login", timeout=10).text
        except requests.exceptions.ConnectionError:
            messagebox.showerror(parent=bhd_login_win, title='Error', message='No internet connection')
            session.close()  # end session
            return  # exit the function

        # if web page didn't return a response
        if not auth_raw:
            messagebox.showerror(parent=bhd_login_win, title='Error', message="Could not access beyondhd.co")
            session.close()  # end session
            return  # exit the function

        # split auth token out of raw web page for later use
        auth_code = auth_raw.split('PF.obj.config.auth_token = ')[1].split(';')[0].replace('"', '')
        if not auth_code:
            messagebox.showerror(parent=bhd_login_win, title='Error', message="Could not find auth token")
            session.close()  # end session
            return  # exit the function

        # login payload
        login_payload = {'login-subject': str(user_entry_box.get()).strip(),
                         'password': str(pass_entry_box.get()).strip(), 'auth_token': auth_code}

        # login post
        try:
            login_post = session.post("https://beyondhd.co/login", data=login_payload, timeout=10)
        except requests.exceptions.ConnectionError:
            session.close()  # end session
            return  # exit the function

        # find user info from login post
        confirm_login = re.search(r"CHV.obj.logged_user =(.+);", login_post.text, re.MULTILINE)
        if confirm_login:
            messagebox.showinfo(parent=bhd_login_win, title='Success', message="Successfully logged in")
            session.close()  # end session

        # if post confirm_login is none
        if not confirm_login:
            messagebox.showerror(parent=bhd_login_win, title='Error', message="Incorrect username and/or password")
            session.close()  # end session
            return  # exit the function

    # create 'Login' button
    login_okay_btn = HoverButton(bhd_login_frame, text="Check Login", command=check_bhd_login, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db", width=10,
                                 activebackground="#23272A")
    login_okay_btn.grid(row=4, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    # create 'Save' button
    custom_cancel_btn = HoverButton(bhd_login_frame, text="Save", activeforeground="#3498db", width=10,
                                    command=save_exit_function, foreground="white", background="#23272A",
                                    borderwidth="3", activebackground="#23272A")
    custom_cancel_btn.grid(row=4, column=4, columnspan=1, padx=7, pady=5, sticky=S + E)

    # decode user and password
    if pathlib.Path('Runtime/user.bin').is_file() and pathlib.Path('Runtime/pass.bin').is_file():
        # start fernet instance
        pass_user_decoder = Fernet(crypto_key)
        # open both user and pass bin files
        with open('Runtime/user.bin', 'rb') as user_file, open('Runtime/pass.bin', 'rb') as pass_file:
            # decode and insert user name
            decode_user = pass_user_decoder.decrypt(user_file.read())
            user_entry_box.delete(0, END)
            user_entry_box.insert(END, decode_user.decode('utf-8'))
            # decode and insert password
            decode_pass = pass_user_decoder.decrypt(pass_file.read())
            pass_entry_box.delete(0, END)
            pass_entry_box.insert(END, decode_pass.decode('utf-8'))

    bhd_login_win.wait_window()  # wait for window to be closed

    open_all_toplevels()  # re-open all top levels if they exist


screen_shot_window_opened = False


# function to set screenshot count
def screen_shot_count_spinbox(*e_hotkey):
    global screen_shot_window_opened
    # check if window is opened
    if screen_shot_window_opened:
        return  # exit the function
    else:
        screen_shot_window_opened = True

    # hide all top levels if they are opened
    hide_all_toplevels()

    # set parser
    ss_count_parser = ConfigParser()
    ss_count_parser.read(config_file)

    # encoder name window
    ss_count_win = Toplevel()
    ss_count_win.title('SS Count')
    ss_count_win.configure(background="#363636")
    ss_count_win.geometry(f'{280}x{140}+{str(int(root.geometry().split("+")[1]) + 220)}+'
                          f'{str(int(root.geometry().split("+")[2]) + 230)}')
    ss_count_win.resizable(False, False)
    ss_count_win.grab_set()
    ss_count_win.protocol('WM_DELETE_WINDOW', lambda: [ss_count_win.destroy(), root.wm_attributes('-alpha', 1.0)])
    root.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
    ss_count_win.grid_rowconfigure(0, weight=1)
    ss_count_win.grid_columnconfigure(0, weight=1)

    # screenshot count frame
    ss_count_frame = Frame(ss_count_win, highlightbackground="white", highlightthickness=2, bg="#363636",
                           highlightcolor='white')
    ss_count_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        ss_count_frame.grid_columnconfigure(e_n_f, weight=1)
        ss_count_frame.grid_rowconfigure(e_n_f, weight=1)

    # add right click menu to quickly set screenshot count
    def spinbox_right_click_options():
        def popup_spinbox_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
            spinbox_sel_menu.tk_popup(e.x_root, e.y_root)  # This gets the position of 'e'

        spinbox_sel_menu = Menu(ss_spinbox, tearoff=False, font=(set_font, set_font_size + 1), background="#23272A",
                                foreground="white", activebackground="#23272A", activeforeground="#3498db")
        spinbox_sel_menu.add_command(label='20', command=lambda: ss_count.set("20"))
        spinbox_sel_menu.add_command(label='30', command=lambda: ss_count.set("30"))
        spinbox_sel_menu.add_command(label='40', command=lambda: ss_count.set("40"))
        spinbox_sel_menu.add_command(label='50', command=lambda: ss_count.set("50"))
        spinbox_sel_menu.add_command(label='60', command=lambda: ss_count.set("60"))
        spinbox_sel_menu.add_command(label='70', command=lambda: ss_count.set("70"))
        spinbox_sel_menu.add_command(label='80', command=lambda: ss_count.set("80"))
        spinbox_sel_menu.add_command(label='90', command=lambda: ss_count.set("90"))
        spinbox_sel_menu.add_command(label='100', command=lambda: ss_count.set("100"))
        ss_spinbox.bind('<Button-3>', popup_spinbox_e_b_menu)  # Uses mouse button 3 (right click) to open
        # custom hover tip
        CustomTooltipLabel(anchor_widget=ss_spinbox, hover_delay=200, background="#363636", foreground="#3498db",
                           font=(set_fixed_font, 9, 'bold'), text='Right click to quickly select amount')

    # create label
    ss_count_lbl = Label(ss_count_frame, text='Select desired amount of comparisons', background='#363636',
                         fg="#3498db", font=(set_font, set_font_size, "bold"))
    ss_count_lbl.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

    # create spinbox
    ss_count = StringVar()
    ss_spinbox = Spinbox(ss_count_frame, from_=20, to=100, increment=1, justify=CENTER, wrap=True,
                         textvariable=ss_count, state='readonly', background="#23272A", foreground="white",
                         highlightthickness=1, buttonbackground="black", readonlybackground="#23272A")
    ss_spinbox.grid(row=1, column=0, columnspan=3, padx=10, pady=3, sticky=N + S + E + W)
    spinbox_right_click_options()

    # set default value for the spinbox
    if ss_count_parser['screenshot_settings']['semi_auto_count'] != '':
        ss_count.set(ss_count_parser['screenshot_settings']['semi_auto_count'])
    else:
        ss_count.set('20')

    # define returned var
    temp_var = ''

    # function to save new name to config.ini
    def custom_okay_func():
        nonlocal temp_var

        # create parser instance
        ss_parser = ConfigParser()
        ss_parser.read(config_file)

        # define temp var
        temp_var = ss_count.get()

        # save setting and exit the window
        if ss_parser['screenshot_settings']['semi_auto_count'] != ss_count.get():
            ss_parser.set('screenshot_settings', 'semi_auto_count', ss_count.get())
            with open(config_file, 'w') as ss_config_file:
                ss_parser.write(ss_config_file)
        root.wm_attributes('-alpha', 1.0)  # restore transparency
        ss_count_win.destroy()  # close window

    # create 'OK' button
    ss_okay_btn = HoverButton(ss_count_frame, text="OK", command=custom_okay_func, foreground="white",
                              background="#23272A", borderwidth="3", activeforeground="#3498db", width=8,
                              activebackground="#23272A")
    ss_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    # create 'Cancel' button
    ss_cancel_btn = HoverButton(ss_count_frame, text="Cancel", activeforeground="#3498db", width=8,
                                command=lambda: [ss_count_win.destroy(), root.wm_attributes('-alpha', 1.0)],
                                foreground="white", background="#23272A", borderwidth="3", activebackground="#23272A")
    ss_cancel_btn.grid(row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    ss_count_win.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist
    screen_shot_window_opened = False  # set variable back to false

    # return temp_var
    return temp_var


options_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='Options', menu=options_menu)
options_menu.add_command(label='Encoder Name', accelerator="[Ctrl+E]",
                         command=lambda: [custom_input_prompt(root, 'Encoder Name:', 'encoder_name', 'name', 'show')])
root.bind('<Control-e>', lambda event: custom_input_prompt(root, 'Encoder Name:', 'encoder_name', 'name', 'show'))
options_menu.add_command(label='API Key', accelerator="[Ctrl+A]",
                         command=lambda: [custom_input_prompt(root, 'BHD Upload Key:', 'bhd_upload_api', 'key',
                                                              'hide')])
root.bind('<Control-a>', lambda event: custom_input_prompt(root, 'BHD Upload Key:', 'bhd_upload_api', 'key', 'hide'))
options_menu.add_command(label='Torrent Output Path', command=torrent_path_window_function, accelerator="[Ctrl+T]")
root.bind("<Control-t>", torrent_path_window_function)
options_menu.add_command(label='BeyondHD.co', command=bhd_co_login_window, accelerator="[Ctrl+I]")
root.bind("<Control-i>", bhd_co_login_window)
options_menu.add_separator()
options_menu.add_command(label='Semi-Auto Screenshot Count', command=screen_shot_count_spinbox, accelerator="[Ctrl+C]")
root.bind("<Control-c>", screen_shot_count_spinbox)
options_menu.add_separator()

# auto update options menu
auto_update_var = StringVar()
auto_update_var.set(config['check_for_updates']['value'])
if auto_update_var.get() == 'True':
    auto_update_var.set('True')
elif auto_update_var.get() == 'False':
    auto_update_var.set(config['check_for_updates']['value'])


# function to save to config
def auto_update_func():
    # parser
    a_u_parser = ConfigParser()
    a_u_parser.read(config_file)
    # write
    a_u_parser.set('check_for_updates', 'value', auto_update_var.get())
    with open(config_file, 'w') as au_configfile:
        a_u_parser.write(au_configfile)


auto_update_func()
options_submenu2 = Menu(root, tearoff=0, activebackground='dim grey')
options_menu.add_cascade(label='Auto Update', menu=options_submenu2)
options_submenu2.add_radiobutton(label='On', variable=auto_update_var, value='True', command=auto_update_func)
options_submenu2.add_radiobutton(label='Off', variable=auto_update_var, value='False', command=auto_update_func)
options_menu.add_separator()

options_menu.add_command(label='Reset All Settings', command=reset_all_settings)

tools_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='Tools', menu=tools_menu)
tools_menu.add_command(label='Manual Uploader', accelerator="[Ctrl+U]",
                       command=lambda: open_uploader_window('custom_advanced'))
root.bind("<Control-u>", lambda event: open_uploader_window('custom_advanced'))

help_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Documentation                 [F1]",  # Open GitHub wiki
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool/wiki'))
root.bind("<F1>", lambda event: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool/wiki'))  # hotkey
help_menu.add_command(label="Project Page",  # Open GitHub project page
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool'))
help_menu.add_command(label="Report Error / Feature Request",  # Open GitHub tracker link
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool'
                                                      '/issues/new/choose'))
help_menu.add_command(label="Download Latest Release",  # Open GitHub release link
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool/releases'))
help_menu.add_separator()
help_menu.add_command(label="Info", command=lambda: openaboutwindow(main_root_title))  # Opens about window


# function to enable/disable main GUI buttons
def generate_button_checker():
    if source_file_path.get() != '' and encode_file_path.get() != '':  # if source/encode is not empty strings
        open_torrent_window_button.config(state=NORMAL)
        auto_screens_multi_btn.config(state=NORMAL)
        view_loaded_script.config(state=NORMAL)
        check_screens = parse_screen_shots()
        # if check screens was not False
        if check_screens:
            generate_nfo_button.config(state=NORMAL)
            parse_and_upload.config(state=NORMAL)
            # if nfo is not blank and torrent file is exists
            if nfo_info_var.get() != '' and pathlib.Path(torrent_file_path.get()).is_file():
                open_uploader_button.config(state=NORMAL)
    else:  # if source/encode is empty strings
        generate_nfo_button.config(state=DISABLED)
        open_torrent_window_button.config(state=DISABLED)
        parse_and_upload.config(state=DISABLED)
        open_uploader_button.config(state=DISABLED)
        auto_screens_multi_btn.config(state=DISABLED)
        view_loaded_script.config(state=DISABLED)
    root.after(50, generate_button_checker)  # loop to constantly check


# start button checker loop
generate_button_checker()


# check for updates
def check_for_latest_program_updates():
    def error_message_open_browser():
        auto_error = messagebox.askyesno(parent=root, title='Error',
                                         message='There was an error automatically getting the download, would you '
                                                 'like to manually update? ')
        # if user selects yes
        if auto_error:
            webbrowser.open(release_link)  # open link to the latest release page
            update_window.destroy()  # close update window

    # update parser
    check_for_update_parser = ConfigParser()
    check_for_update_parser.read(config_file)

    # if check for updates is disabled
    if check_for_update_parser['check_for_updates']['value'] == "False":
        return  # exit function

    release_link = 'https://github.com/jlw4049/BHDStudio-Upload-Tool/releases'

    # parse release page without GitHub api
    try:
        parse_release_page = requests.get(release_link, timeout=10)
    except requests.exceptions.ConnectionError:
        error_message_open_browser()
        return  # exit function

    # split program json string up to get the latest release version
    search_for_version = re.search(r'class="Link--primary">(.*?)</a></h1>', parse_release_page.text, re.MULTILINE)
    if search_for_version:
        parsed_version = search_for_version.group(1)
    elif not search_for_version:
        error_message_open_browser()
        return  # exit function

    # if extracted version is equal to current version exit this function
    if parsed_version == main_root_title:
        return  # program is up-to-date, exit the function

    # if extracted version is the same as skipped version exit this function
    if check_for_update_parser['check_for_updates']['ignore_version'] == parsed_version:
        return  # newest version is set to be skipped

    # search for update link
    find_update_link = re.search(r'"(.*?\.zip)"', parse_release_page.text, re.MULTILINE)
    if find_update_link:
        update_download_link = find_update_link.group(1)
    elif not find_update_link:
        error_message_open_browser()
        return  # exit the function

    # search for latest patch notes
    get_release_notes = re.search(r'<div data-pjax="true" data-test-selector="body-content" data-view-component="true" '
                                  r'class="markdown-body(?s:.*?)<div data-view-component="true" class="Box-footer">',
                                  parse_release_page.text, re.MULTILINE)
    if get_release_notes:
        convert_release_notes = re.search(r"<.*>(.*)<.*>", get_release_notes.group(), re.MULTILINE)
    elif not get_release_notes:
        convert_release_notes = "Could not parse release notes"

    # updater window
    update_window = Toplevel()
    update_window.title('Update')
    update_window.configure(background="#363636")
    update_window.geometry(f'{800}x{540}+{root.geometry().split("+")[1]}+{root.geometry().split("+")[2]}')
    for e_w in range(4):
        update_window.grid_columnconfigure(e_w, weight=1)
    update_window.grid_rowconfigure(0, weight=1)
    update_window.grid_rowconfigure(1, weight=1)
    update_window.grid_rowconfigure(2, weight=1)
    update_window.grab_set()

    # basic update label to show parsed version
    update_label = Label(update_window, text=parsed_version, bd=0, relief=SUNKEN,
                         background='#363636', foreground="#3498db", font=(set_font, set_font_size + 4, 'bold'))
    update_label.grid(column=0, row=0, columnspan=4, pady=3, padx=3, sticky=W + E)

    # scrolled update window
    update_scrolled = scrolledtextwidget.ScrolledText(update_window, bg="#565656", fg="white", bd=4, wrap=WORD)
    update_scrolled.grid(row=1, column=0, columnspan=4, pady=5, padx=5, sticky=E + W + N + S)
    update_scrolled.tag_configure('bold_color', background="#565656", foreground="#3498db", font=12, justify=CENTER)
    update_scrolled.tag_configure('version_color', background="#565656", foreground="white",
                                  font=(set_fixed_font, set_font_size), justify=LEFT)
    update_scrolled.insert(END, f"Current version: {main_root_title}\nVersion found: {parsed_version}\n\n",
                           "version_color")
    update_scrolled.insert(END, "Patch Notes\n", 'bold_color')
    update_scrolled.tag_configure('highlight_color', background="#40444b", foreground="white", font=(set_fixed_font,
                                                                                                     set_font_size))
    html_to_string = BeautifulSoup(get_release_notes.group(), features="lxml")
    update_scrolled.insert(END, html_to_string.get_text(), 'highlight_color')
    update_scrolled.config(state=DISABLED)

    # update button frame
    update_frame = Frame(update_window, bg="#363636", bd=0)
    update_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    update_frame.grid_rowconfigure(0, weight=1)
    update_frame.grid_columnconfigure(0, weight=1)
    update_frame.grid_columnconfigure(1, weight=50)
    update_frame.grid_columnconfigure(2, weight=50)
    update_frame.grid_columnconfigure(3, weight=1)

    # close updater button
    close_updater_btn = HoverButton(update_frame, text='Close', command=update_window.destroy,
                                    foreground='white', background='#23272A', borderwidth='3',
                                    activeforeground="#3498db", activebackground="#23272A", width=14)
    close_updater_btn.grid(row=0, column=0, columnspan=1, padx=10, pady=(5, 4), sticky=S + W)

    # ignore update function
    def ignore_update_function():
        # parser
        i_a_u_parser = ConfigParser()
        i_a_u_parser.read(config_file)
        # write
        i_a_u_parser.set('check_for_updates', 'value', 'False')
        with open(config_file, 'w') as au_configfile:
            i_a_u_parser.write(au_configfile)
        # close update window
        update_window.destroy()

    # ignore updates button
    ignore_updates = HoverButton(update_frame, text='Ignore Updates', command=ignore_update_function,
                                 foreground='white', background='#23272A', borderwidth='3',
                                 activeforeground="#3498db", activebackground="#23272A", width=14)
    ignore_updates.grid(row=0, column=1, columnspan=1, padx=10, pady=(5, 4), sticky=S + W)

    # ignore update function
    def skip_version_function():
        # parser
        skip_version_parser = ConfigParser()
        skip_version_parser.read(config_file)

        # write the version to skip
        if skip_version_parser['check_for_updates']['ignore_version'] != parsed_version:
            skip_version_parser.set('check_for_updates', 'ignore_version', parsed_version)
            with open(config_file, 'w') as version_config:
                skip_version_parser.write(version_config)

        # close update window
        update_window.destroy()

    # skip version button
    skip_version = HoverButton(update_frame, text='Skip Version', command=skip_version_function,
                               foreground='white', background='#23272A', borderwidth='3',
                               activeforeground="#3498db", activebackground="#23272A", width=14)
    skip_version.grid(row=0, column=2, columnspan=1, padx=10, pady=(5, 4), sticky=S + E)

    # update button function
    def update_program():
        # get bhdstudio upload tool download
        try:
            request_download = requests.get(f"https://github.com{update_download_link}", timeout=10)
        except requests.exceptions.ConnectionError:
            messagebox.showerror(parent=update_window, title='Error', message='Automatic update failed')
            return  # exit function

        # if requests passes internet check but for some reason timeouts
        if not request_download:
            messagebox.showerror(parent=update_window, title='Error', message='Automatic update failed')
            return  # exit function

        # if download was successful
        if request_download.ok:
            # delete old exe if it exists (it shouldn't)
            pathlib.Path('OLD.exe').unlink(missing_ok=True)

            # rename current running exe
            pathlib.Path('BHDStudioUploadTool.exe').rename('OLD.exe')

            # use zipfile module to unzip latest update
            with zipfile.ZipFile(BytesIO(request_download.content)) as dl_zipfile:
                dl_zipfile.extractall()

            # check to ensure new exe is moved
            if pathlib.Path("BHDStudioUploadTool.exe").is_file():
                # prompt update message box
                messagebox.showinfo(parent=update_window, title='Update Status',
                                    message='Update complete, program will now restart and automatically clean '
                                            'update files')

                # use subprocess to open the new download
                subprocess.Popen(pathlib.Path(pathlib.Path.cwd() / "BHDStudioUploadTool.exe"),
                                 creationflags=subprocess.CREATE_NO_WINDOW)

                # close update window
                update_window.destroy()

                # close main gui
                root.destroy()

                # exit function to kill thread
                return
            else:
                # if program couldn't move new exe
                messagebox.showinfo(parent=update_window, title='Update Status',
                                    message='Could not move updated exe to main directory, please do this manually')

                # open main directory
                webbrowser.open(str(pathlib.Path.cwd()))

                # close update window
                update_window.destroy()

                # close main gui
                root.destroy()

                # exit function to kill thread
                return

        # if downloaded exe is not detected
        if not pathlib.Path("BHDStudioUploadTool.exe").is_file():
            # open message box failed message
            messagebox.showinfo(parent=update_window, title='Update Status',
                                message="Update failed! Opening link to manual update")
            webbrowser.open(f"https://github.com{update_download_link}")  # open browser for manual download
            return  # exit function

    # update button
    update_button = HoverButton(update_frame, text='Update', command=update_program, foreground='white',
                                background='#23272A', borderwidth='3', activeforeground="#3498db",
                                activebackground="#23272A", width=14)
    update_button.grid(row=0, column=3, columnspan=1, padx=10, pady=(5, 4), sticky=S + E)

    update_window.grab_set()  # Brings attention to this window until it's closed


# start check for updates function in a new thread
if app_type == 'bundled':
    check_update = threading.Thread(target=check_for_latest_program_updates).start()

# if program was opened with a dropped video file load it into the source function
if cli_command:
    source_input_function(cli_command)


# clean update files
def clean_update_files():
    if pathlib.Path("OLD.exe").is_file():
        try:
            pathlib.Path('OLD.exe').unlink(missing_ok=True)  # delete old exe
        except PermissionError:
            pass


if app_type == 'bundled':
    root.after(5000, clean_update_files)

# tkinter mainloop
root.mainloop()
