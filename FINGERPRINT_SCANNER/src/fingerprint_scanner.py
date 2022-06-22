from adafruit_pn532.i2c import PN532_I2C
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A
import argparse
import busio
import board
import json
import RPi.GPIO as GPIO
from threading import Thread
from time import sleep, time
import tkinter as tk
from tkinter import W, E, messagebox, ttk
import vlc
import pyautogui


'''
=========================================================================================================
Argument parser
=========================================================================================================
'''
argparser = argparse.ArgumentParser(
    description='Fingerprint Scanner')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

city = argparser.parse_args().city


'''
=========================================================================================================
Load config
=========================================================================================================
'''
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

with open('texts.json', 'r') as texts_file:
    texts = json.load(texts_file)

'''
=========================================================================================================
Global language variable
=========================================================================================================
'''
language = 'deu'


'''
=========================================================================================================
PN532 init
=========================================================================================================
'''
read_block = 4
pn532 = PN532_I2C(busio.I2C(board.SCL, board.SDA), debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
sleep(0.5)  # this delay avoids some problems after wakeup
pn532.SAM_configuration()   # Configure PN532 to communicate with MiFare cards

cards_images = {
    "BE": "1-eva_julius.png",
    "ZK": "2-janine.png",
    "SB": "3-jessica_unknown.png",
    "TB": "4-luise.png",
    "DT": "5-jakob_unknown.png",
    "RF": "6-johannes_unknown.png",
    "KU": "7-jessica.png",
    "VM": "8-julius_unknown_johannes.png",
    "unk": "9-unknown.png"
}

'''
=========================================================================================================
GPIO init
=========================================================================================================
'''
GPIO.setmode(GPIO.BCM)

'''
=========================================================================================================
VLC init
=========================================================================================================
'''
Instance = vlc.Instance()
media = Instance.media_new(config['PATH']['video'] + 'scannerfilm_mit_sound.mp4')
player = Instance.media_player_new()
player.set_media(media)

'''
=========================================================================================================
Variable init
=========================================================================================================
'''
places = []
proof = []
person_one = []
person_two = []
toxicity = []


'''
=========================================================================================================
RFID classes (related to RFID scanner)
=========================================================================================================
'''
class Check_pin(Thread):
    # Check door status
    def __init__(self, door_pin):
        Thread.__init__(self)
        self.pin = door_pin
        GPIO.setup(config['PIN'][city]['door'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.status = bool(GPIO.input(config['PIN'][city]['door']))

    def checkloop(self):
        while True:
            self.reset_mouse()
            # sleep(1)
            #print(f"door: {GPIO.input(self.pin)}")
            if self.status != bool(GPIO.input(self.pin)):
                self.status = bool(GPIO.input(self.pin))
                if self.status:
                    print("door: locked")
                    scan_field()
                else:
                    print("door: unlocked")

    def is_door_closed(self):
        return bool(GPIO.input(self.pin))

    def reset_mouse(self):
        currentMouseX, currentMouseY = pyautogui.position()
        if currentMouseX < 1024:
            #print('POS is: {}, {} limitx'.format(currentMouseX, currentMouseY))
            pyautogui.moveTo(1024, currentMouseY)
'''
=========================================================================================================
RFID functions
=========================================================================================================
'''
def authenticate(uid, read_block):
    rc = 0
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rc = pn532.mifare_classic_authenticate_block(
        uid, read_block, MIFARE_CMD_AUTH_A, key)
    print(rc)
    return rc

def card_func(sample_var):
    sleep(1)
    global picture_popup

    try:
        picture_popup.destroy()
    except (AttributeError, NameError):
        picture_popup = None

    toplevel = tk.Toplevel()

    # offset_x = 200 #random.randint(0, 200)
    # offset_y = 400 #random.randint(0, 400)
    x = root.winfo_x()
    y = root.winfo_y()
    str_geo = "+%d+%d" % (x, y)
    print("img @ " + str_geo)
    toplevel.geometry(str_geo)

    toplevel.title("Scanning result")
    FA_Bild = tk.PhotoImage(file = config['PATH']['image'] + 'fingerprints/' + cards_images.get(sample_var, cards_images["unk"]))
    FA_Label = tk.Label(toplevel, image=FA_Bild)
    FA_Label.image = FA_Bild
    FA_Label.grid()

    #toplevel.attributes("-toolwindow",1)
    toplevel.resizable(0, 0)  # will remove the top badge of window
    toplevel.lift(root)
    picture_popup = toplevel

def foo():      # dummy function
    pass

def return_to_normal():
    global ButtonScan
    ButtonScan["command"] = scan_field

def scan_field():
    global warning_popup
    global ButtonScan
    global window

    try:
        warning_popup.destroy()
    except (AttributeError, NameError):
        warning_popup = None
    
    #print(f'button state {ButtonScan["state"]}')
    if not chk_door.is_door_closed():
        popupmsg(
            "Close door", "Bitte schließen Sie die scannertür \n Please close the scanner door") 
        return -1

    if ButtonScan["state"] == tk.DISABLED :
        return -1
    else:
        print(f'btn state: {ButtonScan["state"]}')

    ButtonScan["state"] = tk.DISABLED
    ButtonScan["command"] = foo
    window.update()

    print(f'btn is now: {ButtonScan["state"]}')
    
    start_time = time()
    count = 0
    # Show scanning window
    player.set_xwindow(videopanel.winfo_id())
    player.play()  # hit the player button

    # Found Solution
    success = False
    msg = ["Timeout!", "Beweismittel richtig einlegen \n Object not placed correctly"]
    read_data = "XX"

    uid = None
    while chk_door.is_door_closed():
        try:
            uid = pn532.read_passive_target(timeout=0.5)
        except RuntimeError:
            sleep(0.2)

        print('.', end="")
        # Try again if no card is available.
        if uid is None:
            count += 1
            if count > 10:
                print("Timeout! Failed to read")
                break
        else:
            print('Found card with UID:', [hex(i) for i in uid])
            break

    print("Out while")

    if uid:
        print('Card found')
        try:
            # if classic tag
            auth = authenticate(uid, read_block)
        except Exception:
            # if ntag
            auth = False

        try:
            # Switch between ntag and classic
            if auth:  # True for classic and False for ntags
                data = pn532.mifare_classic_read_block(read_block)
            else:
                data = pn532.ntag2xx_read_block(read_block)

            if data is not None:
                read_data = data.decode('utf-8')[:2]
            else:
                print("None block")
        except Exception as e:
            print(e)

        print('data is: {}'.format(read_data))
        if read_data != "XX":
            success = True
        else:
            msg = [
                "Fehler", "Beweismittel richtig einlegen - Object not placed correctly"]

    # wait video before showing results
    while chk_door.is_door_closed() and (time() - start_time) < 10:
        pass

    # end video
    print("--- %s seconds ---" % (time() - start_time))
    player.stop()
    
    # activate button again
    ButtonScan["state"] = tk.ACTIVE
    window.after(100, return_to_normal)

    # actions are taken later
    if success:
        card_func(read_data)
    else:
        popupmsg(*msg)

    window.update()
    return uid


'''
=========================================================================================================
Tkinter classes
=========================================================================================================
'''
class MyOptionMenu(tk.OptionMenu):
    # Dropdown anpassen
    def __init__(self, master, status, *options):
        self.var = tk.StringVar(master)
        self.var.set(status)
        super().__init__(master, self.var, *options)
        self.config(font=('calibri', (config['TKINTER']['font-size'])), bg='#E2E2E2', width=12)
        self['menu'].config(font=('calibri', (config['TKINTER']['font-size'])), bg=config['TKINTER']['background-color'])

'''
=========================================================================================================
Tkinter functions
=========================================================================================================
'''
def motion(event):
    # limit the mouse motion to just the GUI dimensions
    # Returns two integers, the x and y of the mouse cursor's current position.
    currentMouseX, currentMouseY = pyautogui.position()
    if currentMouseX < 1024:
        #print('POS is: {}, {} limitx'.format(currentMouseX, currentMouseY))
        pyautogui.moveTo(1024, currentMouseY)


def reset_mouse(event):
    currentMouseX, currentMouseY = pyautogui.position()
    pyautogui.moveTo(1025, currentMouseY)


def popupmsg(ttl, msg):
    global warning_popup

    try:
        warning_popup.destroy()
    except (AttributeError, NameError):
        warning_popup = None

    #popup.wm_title(ttl)
    # keeps popup above everything until closed.
    # popup.wm_attributes('-topmost', True)
    # this is outter background colour
    #popup.configure(background='#4a4a4a')
    top = tk.Toplevel(root)
    top.details_expanded = False
    top.title(ttl)
    w = 300
    h = 100
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = int((ws/2)) + 200
    y = int((hs/2) - (h/2))
    top.geometry("{}x{}+{}+{}".format(w, h, x, y))
    top.resizable(False, False)
    top.rowconfigure(0, weight=0)
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=1)
    tk.Label(top, image="::tk::icons::question").grid(row=0, column=0, pady=(7, 0), padx=(7, 7), sticky="e")
    tk.Label(top, text=msg).grid(row=0, column=1, columnspan=2, pady=(7, 7), sticky="w")
    ttk.Button(top, text="OK", command=top.destroy).grid(row=1, column=2, padx=(7, 7), sticky="e")
    top.lift(root)
    warning_popup = top


def check_de(event=0):
    if check_beweismittel() == 1 and check_person1() == 1 and check_person2() == 1 and check_toxisch() == 1:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + '/messages/deu/accepted.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    elif check_beweismittel() == 2 and check_person1() == 2 and check_person2() == 1 and check_toxisch() == 2:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + '/messages/deu/hint.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    else:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + '/messages/deu/declined.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild


def check_en(event=0):
    if check_proof() == 1 and check_en_person1() == 1 and check_en_person2() == 1 and check_toxic() == 1:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + '/messages/eng/accepted.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    elif check_proof() == 2 and check_en_person1() == 2 and check_en_person2() == 1 and check_toxic() == 2:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + '/messages/eng/hint.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    else:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + '/messages/eng/declined.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild


def check_beweismittel():
    if(beweismittel1.var).get() == "Becher" and\
        (beweismittel2.var).get() == "Zucker" and\
        (beweismittel3.var).get() == "Süßstoff" and\
        (beweismittel4.var).get() == "Tabletten" and\
        (beweismittel5.var).get() == "Reiseführer" and\
        (beweismittel6.var).get() == "Donut" and\
            (beweismittel7.var).get() == "Kuli":
        var_beweismittel = 1
    elif(beweismittel1.var).get() == "Becher" and\
        (beweismittel2.var).get() == "Zucker" and\
        (beweismittel3.var).get() == "Süßstoff" and\
        (beweismittel4.var).get() == "Tabletten" and\
        (beweismittel5.var).get() == "Donut" and\
        (beweismittel6.var).get() == "Reiseführer" and\
            (beweismittel7.var).get() == "Kuli":
        var_beweismittel = 2
    else:
        var_beweismittel = 0
    return var_beweismittel


def check_person1():
    if(person11.var).get() == "Eva" and\
        (person12.var).get() == "Janine" and\
        (person13.var).get() == "Jessica" and\
        (person14.var).get() == "Luise" and\
        (person15.var).get() == "Johannes" and\
        (person16.var).get() == "Jakob" and\
            (person17.var).get() == "Jessica":
        var_person1 = 1
    elif(person11.var).get() == "Eva" and\
        (person12.var).get() == "Janine" and\
        (person13.var).get() == "Jessica" and\
        (person14.var).get() == "Luise" and\
        (person15.var).get() == "Jakob" and\
        (person16.var).get() == "Johannes" and\
            (person17.var).get() == "Jessica":
        var_person1 = 2
    else:
        var_person1 = 0
    return var_person1


def check_person2():
    if(person21.var).get() == "Julius" and\
        (person22.var).get() == "- kein -" and\
        (person23.var).get() == "Unbekannt" and\
        (person24.var).get() == "- kein -" and\
        (person25.var).get() == "Unbekannt" and\
        (person26.var).get() == "Unbekannt" and\
            (person27.var).get() == "- kein -":
        var_person2 = 1
    else:
        var_person2 = 0
    return var_person2


def check_toxisch():
    if(toxisch1.var).get() == "Toxisch" and\
        (toxisch2.var).get() == "Nicht toxisch" and\
        (toxisch3.var).get() == "Nicht toxisch" and\
        (toxisch4.var).get() == "Nicht toxisch" and\
        (toxisch5.var).get() == "Keine Probe" and\
        (toxisch6.var).get() == "Nicht toxisch" and\
            (toxisch7.var).get() == "Keine Probe":
        var_toxisch = 1
    elif(toxisch1.var).get() == "Toxisch" and\
        (toxisch2.var).get() == "Nicht toxisch" and\
        (toxisch3.var).get() == "Nicht toxisch" and\
        (toxisch4.var).get() == "Nicht toxisch" and\
        (toxisch5.var).get() == "Nicht toxisch" and\
        (toxisch6.var).get() == "Keine Probe" and\
            (toxisch7.var).get() == "Keine Probe":
        var_toxisch = 2

    else:
        var_toxisch = 0
    return var_toxisch


def check_proof():
    if(proof1.var).get() == "Cup" and\
        (proof2.var).get() == "Sugar" and\
        (proof3.var).get() == "Sweetener" and\
        (proof4.var).get() == "Pills" and\
        (proof5.var).get() == "Guidebook" and\
        (proof6.var).get() == "Donut" and\
            (proof7.var).get() == "Pen":
        var_proof = 1
    elif(proof1.var).get() == "Cup" and\
        (proof2.var).get() == "Sugar" and\
        (proof3.var).get() == "Sweetener" and\
        (proof4.var).get() == "Pills" and\
        (proof5.var).get() == "Donut" and\
        (proof6.var).get() == "Guidebook" and\
            (proof7.var).get() == "Pen":
        var_proof = 2
    else:
        var_proof = 0
    return var_proof


def check_en_person1():
    if(en_person11.var).get() == "Eva" and\
        (en_person12.var).get() == "Janine" and\
        (en_person13.var).get() == "Jessica" and\
        (en_person14.var).get() == "Luise" and\
        (en_person15.var).get() == "Johannes" and\
        (en_person16.var).get() == "Jakob" and\
            (en_person17.var).get() == "Jessica":
        var_en_person1 = 1
    elif(en_person11.var).get() == "Eva" and\
        (en_person12.var).get() == "Janine" and\
        (en_person13.var).get() == "Jessica" and\
        (en_person14.var).get() == "Luise" and\
        (en_person15.var).get() == "Jakob" and\
        (en_person16.var).get() == "Johannes" and\
            (en_person17.var).get() == "Jessica":
        var_en_person1 = 2

    else:
        var_en_person1 = 0
    return var_en_person1


def check_en_person2():
    if(en_person21.var).get() == "Julius" and\
        (en_person22.var).get() == "- none -" and\
        (en_person23.var).get() == "Unknown" and\
        (en_person24.var).get() == "- none -" and\
        (en_person25.var).get() == "Unknown" and\
        (en_person26.var).get() == "Unknown" and\
            (en_person27.var).get() == "- none -":
        var_en_person2 = 1
    else:
        var_en_person2 = 0
    return var_en_person2


def check_toxic():
    if(toxic1.var).get() == "toxic" and\
        (toxic2.var).get() == "non toxic" and\
        (toxic3.var).get() == "non toxic" and\
        (toxic4.var).get() == "non toxic" and\
        (toxic5.var).get() == "no sample" and\
        (toxic6.var).get() == "non toxic" and\
            (toxic7.var).get() == "no sample":
        var_toxic = 1
    elif(toxic1.var).get() == "toxic" and\
        (toxic2.var).get() == "non toxic" and\
        (toxic3.var).get() == "non toxic" and\
        (toxic4.var).get() == "non toxic" and\
        (toxic5.var).get() == "non toxic" and\
        (toxic6.var).get() == "no sample" and\
            (toxic7.var).get() == "no sample":
        var_toxic = 2
    else:
        var_toxic = 0
    return var_toxic

# from here on there are new functions
def landingpage():
    window.unbind('<Return>')
    frame_language.grid(row=1, column=1)
    label_headline.grid(row=0, column=0, sticky=W+E, columnspan=3)
    button_deu.grid(row=0, column=0, sticky=W+E, padx=config['TKINTER']['tabpadx'], pady=20)
    button_eng.grid(row=1, column=0, sticky=W+E, padx=config['TKINTER']['tabpadx'], pady=20)


def select_eng():
    global language
    language = 'eng'
    evidence_collection()()


def select_deu():
    global language
    language = 'deu'
    evidence_collection()()


def evidence_collection():
    frame_language.grid_forget()
    label_headline.grid_forget()
    button_deu.grid_forget()
    button_eng.grid_forget()

    # bg_image_en = tk.PhotoImage(file = config['PATH']['image'] + city + '/background/eng/background.png')
    # label_background_eng.configure(image=bg_image_en)
    # label_background_eng.image=bg_image_en
    # label_background_eng.place(x=0, y=0)

    frame_login.grid(row=1, column=1)
    
    places.append(tk.Label(frame_login, text=texts['all'][language]['head_place'], bg=config['TKINTER']['background-color'], font="HELVETICA 22 bold"))
    for i in range(1, 8):
        places.append(tk.Label(frame_login, text=i, bg=config['TKINTER']['background-color'], font="HELVETICA 18 bold"))
    for i in range(0, len(places)):
        places[i].grid(row=i, sticky=W+E, padx=config['TKINTER']['tabpadx'])

    init_dropdown(proof, texts['all'][language]['head_object'], texts[city][language]['dropdown_objects'])
    for i in range(0, len(proof)):
        proof[i].grid(row=i, column=1, sticky=W+E, padx=config['TKINTER']['tabpadx'])

    init_dropdown(person_one, texts['all'][language]['head_person_1'], texts['all'][language]['dropdown_person_1'])
    for i in range(0, len(person_one)):
        person_one[i].grid(row=i, column=2, sticky=W+E, padx=config['TKINTER']['tabpadx'])

    init_dropdown(person_two, texts['all'][language]['head_person_2'], texts['all'][language]['dropdown_person_2'])
    for i in range(0, len(person_two)):
        person_two[i].grid(row=i, column=3, sticky=W+E, padx=config['TKINTER']['tabpadx'])

    init_dropdown(toxicity, texts['all'][language]['head_toxicity'], texts['all'][language]['dropdown_toxicity'])
    for i in range(0, len(toxicity)):
        toxicity[i].grid(row=i, column=4, sticky=W+E, padx=config['TKINTER']['tabpadx'])
    

    ButtonSendEn.grid(row=8, column=4, sticky=W, padx=config['TKINTER']['tabpadx'], pady=20)
    ButtonScan.grid(row=8, column=1, rowspan=2, stick=W+E, pady=20, padx=config['TKINTER']['tabpadx'])
    ButtonScan["state"] = tk.NORMAL   # Activate scanning ability


def init_dropdown(_list, text_head, text_dropdown):
    _list.append(tk.Label(frame_login, text=text_head, bg=config['TKINTER']['background-color'], font="HELVETICA 22 bold"))
    for i in range(1, 8):
        _list.append(MyOptionMenu(frame_login, texts['all'][language]['dropdown_std'], *text_dropdown))
    
'''
=========================================================================================================
"MAIN"
=========================================================================================================
'''
root = tk.Tk()
root.title("Fingerprint scanner")
scrW = root.winfo_screenwidth()
scrH = root.winfo_screenheight()
geo_str = str(scrW) + "x" + str(scrH)

# We will create two screens: one for the interface, one for laser scanner
# small screen root
# top2 = tk.Toplevel(root, bg='#000000')
# top2.geometry("+0+0")
# top2.attributes('-fullscreen', tk.TRUE)
# top2.wm_attributes("-topmost", 1)  # make sure window is on top to start

# big screen
window = root
root.option_add('*Dialog.msg.width', 34)
print("Geo str: " + geo_str)
window.geometry(geo_str)
window.title("Forensik Hamburg")
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(2, weight=1)
# window.wm_attributes("-topmost", 1)  # make sure window is on top to start
window.configure(background=config['TKINTER']['background-color'])
window.attributes('-fullscreen', True)

sleep(1)

# ------------------------ Frame ----------------------------------
frame_login = tk.Frame(window, bg=config['TKINTER']['background-color'], bd=0, height=700, width=1620)
frame_language = tk.Frame(window, bg=config['TKINTER']['background-color'], bd=200, height=700, width=700)


# ------------------------ Images ---------------------------------
bg_image_de = tk.PhotoImage(file = config['PATH']['image'] + city + '/background/deu/background.png')
#bg_image_en = tk.PhotoImage(file = config['PATH']['image'] + city + '/background/eng/background.png')
flag_deu = tk.PhotoImage(file = config['PATH']['image'] + 'deu.png')
flag_eng = tk.PhotoImage(file = config['PATH']['image'] + 'eng.png')

# ------------------------ Label ----------------------------------
label_headline = tk.Label(window, text="Sprache wählen | Please select your language", bg=config['TKINTER']['background-color'], font="HELVETICA 40 bold")
label_background_deu = tk.Label(window, image=bg_image_de)
#label_background_eng = tk.Label(window, image=bg_image_en)
label_background_eng = tk.Label(window, bg='#FFFFFF')
label_flag_deu = tk.Label(frame_language, image=flag_deu)
label_flag_eng = tk.Label(frame_language, image=flag_eng)
label_text_deu = tk.Label(frame_language, text="Deutsch", bg=config['TKINTER']['background-color'], font="HELVETICA 30 bold")
label_text_eng = tk.Label(frame_language, text="English", bg=config['TKINTER']['background-color'], font="HELVETICA 30 bold")


# ------------------------ Buttons ------------------------
ButtonScan = tk.Button(frame_login, text="SCAN", font="HELVETICA 18 bold", command=scan_field, bg='#BB3030', fg='#E0E0E0')
ButtonScan.config(activebackground='#FF5050')
ButtonScan["state"] = tk.DISABLED   # Disable scanning ability
ButtonSendGer = tk.Button(frame_login, text="Absenden", font="HELVETICA 18 bold", command=check_de, bg='#E2E2E2')
ButtonSendEn = tk.Button(frame_login, text="Submit", font="HELVETICA 18 bold", command=check_en, bg='#E2E2E2')
button_deu = tk.Button(frame_language, image=flag_deu, command=lambda: select_deu())
button_eng = tk.Button(frame_language, image=flag_eng, command=lambda: select_eng())




landingpage()

# Mainloop

#if __name__ == "__main__":
    # pyautogui.FAILSAFE = False
    # top2.config(cursor="none")

    # warning_popup = None
    # picture_popup = None

    # chk_door = Check_pin(config['PIN'][city]['door'])
    # c1 = Thread(target=chk_door.checkloop)
    # c1.start()

    # videopanel = tk.Frame(top2)
    # canvas = tk.Canvas(videopanel,  bg="black", bd=0, highlightthickness=0, relief='ridge').pack(fill=tk.BOTH, expand=1)
    # videopanel.pack(fill=tk.BOTH, expand=1)
window.mainloop()
