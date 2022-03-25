import argparse
import gc
import json
from tkinter import messagebox
from tkinter import *
from PIL import Image

gc.collect()

argparser = argparse.ArgumentParser(
    description='Carls Office')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / s]')

args = argparser.parse_args()

with open('config.json', 'r', encoding='utf8') as config_file:
    config = json.load(config_file)

city = args.city
language = 'deu'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                                        FUNCTIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def landingpage():
    window.unbind('<Return>')
    frame_language.grid(row=1, column=1)
    label_headline.grid(row=0, column=0, sticky= W+E, columnspan=3)    
    button_deu.grid(row=0, column=0, sticky=W+E, padx=config['tkinter']['tabpadx'], pady=20)
    button_eng.grid(row=1, column=0, sticky=W+E, padx=config['tkinter']['tabpadx'], pady=20)

def select_eng():
    global language
    language = 'eng'
    login_window()

def select_deu():
    global language
    language = 'deu'
    login_window()

def login_window():
    frame_language.grid_forget()
    label_headline.grid_forget()
    window.bind('<Return>', pw_check)
    
    frame_login.grid(row=1, column=1)
    
    label_name.configure(text=config['text']['login']['username'][language])
    label_password.configure(text=config['text']['login']['password'][language])
    label_name.grid(row=0, sticky=W)
    label_password.grid(row=1, sticky=W)
    
    label_username.grid(row=0, column=1, sticky=W)
    input_password.grid(row=1, column=1)
    input_password.focus_set()
    
    logo_police = PhotoImage(file = config['general']['img_path'][city] + "police.png")
    label_logo.configure(image=logo_police)
    label_logo.image=logo_police
    label_logo.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)

    button_login.configure(text=config['text']['button']['login'][language])
    button_login.grid(row=3, column=1, sticky=E, pady=30)
    button_pw_hint.configure(text=config['text']['button']['pw_hint'][language])
    button_pw_hint.grid(row=3, column=2, sticky=E, padx=10)

def pw_hint():
    global language
    messagebox.showinfo(config['text']['password_hint']['title'][language], config['text']['password_hint']['text'][language])

def pw_check(event=0):
    global language
    
    if input_password.get() == config['general']['password']:
        show_website()
    elif input_password.get() == config['general']['exit_password']:
        close()
    else:
        messagebox.showinfo(config['text']['password_wrong']['title'][language], config['text']['password_wrong']['text'][language])

def show_website():
    frame_login.grid_forget()
    website=PhotoImage(file = config['general']['img_path'][city] + "website_" + language + ".png")
    label_website.configure(image=website)
    label_website.image=website
    label_website.grid()


def dismiss(event):
    gc.collect()
    frame_login.grid_forget()
    label_website.grid_forget()
    label_username.grid_forget()
    button_login.grid_forget()
    button_pw_hint.grid_forget()
    input_password.delete(0, END)
    landingpage()

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
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(2, weight=1)
window.bind('<Escape>', dismiss)
window.bind('Super_L', dismiss)


#------------------------ Frame ------------------------
frame_login = Frame(window, bg='#FFFFFF', bd=200, height=600, width=500)
frame_language = Frame(window, bg=config['tkinter']['background-color'], bd=200, height=900, width=1600)

#------------------------ Bilder ------------------------
label_logo = Label(frame_login, bg='#FFFFFF')
label_headline=Label(window, text="Sprache wählen / Please select your language", bg=config['tkinter']['background-color'], font= "HELVETICA 40 bold")
label_name=Label(frame_login, bg='#FFFFFF', font= "HELVETICA 18 bold")
label_password = Label(frame_login, bg='#FFFFFF', font= "HELVETICA 18 bold")
label_username = Label(frame_login, text='Carl', bg='#FFFFFF', font= "HELVETICA 18 bold")
label_website = Label(window)

#------------------------ Eingabe ------------------------
flag_deu = PhotoImage(file = config['general']['img_path']['all'] + "deu.png")
flag_eng = PhotoImage(file = config['general']['img_path']['all'] + "eng.png")
button_deu = Button(frame_language, image=flag_deu, command=lambda: select_deu())
button_eng = Button(frame_language, image=flag_eng, command=lambda: select_eng())
button_login = Button(frame_login,font= "HELVETICA 14 bold", command=lambda: pw_check())
button_pw_hint = Button(frame_login, font= "HELVETICA 14 bold", command=pw_hint)

input_password = Entry(frame_login, text='Code', bg='#FFFFFF', show="*", font= "HELVETICA 18 bold")

landingpage()

window.mainloop()
