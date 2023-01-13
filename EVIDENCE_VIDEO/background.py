import gc
import json
from tkinter import messagebox
from tkinter import *
import tkinter as tk


gc.collect()


with open('/home/2cp/evidence_video/config.json', 'r', encoding='utf8') as config_file:
    config = json.load(config_file)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                                        FUNCTIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def landingpage():
    window.unbind('<Return>')
    # Changed Button to Canvas
    bg = canvas_language.create_image(0, 0, image=bg_image_startscreen, anchor=tk.NW)    


def close():
    gc.collect()
    window.destroy()





"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                                        MAIN
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
window = Tk()
window.title("LOGIN")
window.attributes("-fullscreen", True)
window.configure(background = config['tkinter']['background-color'])
window.wm_attributes("-topmost", 1)  # make sure window is on top to start
window.config(cursor="none")


# ------------------------ Canvas ---------------------------------
canvas_language = tk.Canvas(window, bg="black", width = 1920, height = 1080)
canvas_language.pack()

#------------------------ Bilder ------------------------
bg_image_startscreen = tk.PhotoImage(file = config['general']['img_path']['all'] +  'startscreen.png')
label_background_startsceen = tk.Label(window, image = bg_image_startscreen)

landingpage()

window.mainloop()
