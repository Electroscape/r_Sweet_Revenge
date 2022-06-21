from adafruit_pn532.i2c import PN532_I2C
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A
import argparse
import busio
import board
import RPi.GPIO as GPIO
from threading import Thread
from time import sleep, time
import tkinter as tk
from tkinter import W, E, messagebox, ttk
import vlc
import pyautogui


'''
Argument parser
'''
argparser = argparse.ArgumentParser(
    description='Fingerprint Scanner')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

city = argparser.parse_args().city


'''
Load config
'''
with open('config.json', 'r') as config_file:
    config = json.load(config_file)



GPIO.setmode(GPIO.BCM)
door_lock_pin = 4

# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)

# Non-hardware reset/request with I2C
pn532 = PN532_I2C(i2c, debug=False)
read_block = 4

ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# this delay avoids some problems after wakeup
sleep(0.5)

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

bgDef = '#F2F2F2'             # Hintergrundfarbe
tabpadx = 50                  # Spaltenbreite der Einträge
fontSize = 22                 # Schriftgröße
textSTD = "- Auswahl -"       # Standardtext für Dropdown
textSTD_en = "- select -"

cards_images = {
    "BE": "img/fingerprints/1-eva_julius.png",
    "ZK": "img/fingerprints/2-janine.png",
    "SB": "img/fingerprints/3-jessica_unknown.png",
    "TB": "img/fingerprints/4-luise.png",
    "DT": "img/fingerprints/5-jakob_unknown.png",
    "RF": "img/fingerprints/6-johannes_unknown.png",
    "KU": "img/fingerprints/7-jessica.png",
    "VM": "img/fingerprints/8-julius_unknown_johannes.png",
    "unk": "img/fingerprints/9-unknown.png"
}

# Scanner video
Instance = vlc.Instance()
media = Instance.media_new('vid/scannerfilm_mit_sound.mp4')
player = Instance.media_player_new()
player.set_media(media)


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


def authenticate(uid, read_block):
    rc = 0
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rc = pn532.mifare_classic_authenticate_block(
        uid, read_block, MIFARE_CMD_AUTH_A, key)
    print(rc)
    return rc


class Check_pin(Thread):
    # Check door status
    def __init__(self, door_pin):
        Thread.__init__(self)
        self.pin = door_pin
        GPIO.setup(door_lock_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.status = bool(GPIO.input(door_lock_pin))

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


class MyOptionMenu(tk.OptionMenu):
    # Dropdown anpassen
    def __init__(self, master, status, *options):
        self.var = tk.StringVar(master)
        self.var.set(status)
        super().__init__(master, self.var, *options)
        self.config(font=('calibri', (fontSize)), bg='#E2E2E2', width=12)
        self['menu'].config(font=('calibri', (fontSize)), bg=bgDef)


root = tk.Tk()
root.title("Fingerprint scanner")
scrW = root.winfo_screenwidth()
scrH = root.winfo_screenheight()
geo_str = str(scrW) + "x" + str(scrH)

# We will create two screens: one for the interface, one for laser scanner
# small screen root
top2 = tk.Toplevel(root, bg='#000000')
top2.geometry("+0+0")
top2.attributes('-fullscreen', tk.TRUE)
top2.wm_attributes("-topmost", 1)  # make sure window is on top to start

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
window.configure(background=bgDef)
window.attributes('-fullscreen', True)

sleep(1)

img_path = "/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/"


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

# ------------------------ RFID ------------------------


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
    FA_Bild = tk.PhotoImage(file=cards_images.get(
        sample_var, cards_images["unk"]))
    FA_Label = tk.Label(toplevel, image=FA_Bild)
    FA_Label.image = FA_Bild
    FA_Label.grid()

    #toplevel.attributes("-toolwindow",1)
    toplevel.resizable(0, 0)  # will remove the top badge of window
    toplevel.lift(root)
    picture_popup = toplevel

# dummy function
def foo():
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


# ------------------------ Hintergrundbild ------------------------
bg_image_de = tk.PhotoImage(
    file="/home/2cp/FINGERPRINT_SCANNER/img/hh/background/deu/background.png")
bg_de = tk.Label(window, image=bg_image_de)
bg_image_en = tk.PhotoImage(
    file="/home/2cp/FINGERPRINT_SCANNER/img/hh/background/eng/background.png")
bg_en = tk.Label(window, image=bg_image_en)

# ------------------------ Frame ------------------------
loginframe = tk.Frame(window, bg=bgDef, bd=0, height=700, width=1620)

# ------------------------ Frame ------------------------
ButtonScan = tk.Button(loginframe, text="SCAN", font="HELVETICA 18 bold",
                       command=scan_field, bg='#BB3030', fg='#E0E0E0')
ButtonScan.config(activebackground='#FF5050')
# Disable scanning ability
ButtonScan["state"] = tk.DISABLED

# ----------------------------------------------------------------------------------------------------------------------
# ----- Dropdownmenü ---------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# --- deutsch ---

# Fundort
ort = tk.Label(loginframe, text="Fundort", bg=bgDef, font="HELVETICA 22 bold")
ort1 = tk.Label(loginframe, text="1", bg=bgDef, font="HELVETICA 18 bold")
ort2 = tk.Label(loginframe, text="2", bg=bgDef, font="HELVETICA 18 bold")
ort3 = tk.Label(loginframe, text="3", bg=bgDef, font="HELVETICA 18 bold")
ort4 = tk.Label(loginframe, text="4", bg=bgDef, font="HELVETICA 18 bold")
ort5 = tk.Label(loginframe, text="5", bg=bgDef, font="HELVETICA 18 bold")
ort6 = tk.Label(loginframe, text="6", bg=bgDef, font="HELVETICA 18 bold")
ort7 = tk.Label(loginframe, text="7", bg=bgDef, font="HELVETICA 18 bold")
# Objekt
beweismittel = tk.Label(loginframe, text="Objekt",
                        bg=bgDef, font="HELVETICA 22 bold")
beweismittel1 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
beweismittel2 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
beweismittel3 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
beweismittel4 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
beweismittel5 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
beweismittel6 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
beweismittel7 = MyOptionMenu(loginframe, textSTD, "Becher", "Kuli",
                             "Reiseführer", "Süßstoff", "Tabletten", "Donut", "Zucker")
# Person 1
personEins = tk.Label(loginframe, text="Fingerabdruck 1",
                      bg=bgDef, font="HELVETICA 22 bold")
person11 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person12 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person13 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person14 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person15 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person16 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person17 = MyOptionMenu(loginframe, textSTD, "- kein -", "Eva",
                        "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
# Person 2
personZwei = tk.Label(loginframe, text="Fingerabdruck 2",
                      bg=bgDef, font="HELVETICA 22 bold")
person21 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person22 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person23 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person24 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person25 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person26 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
person27 = MyOptionMenu(loginframe, "- kein -", "- kein -", "Unbekannt",
                        "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
# Toxisch/nicht toxisch
Toxisch = tk.Label(loginframe, text="Toxizität",
                   bg=bgDef, font="HELVETICA 22 bold")
toxisch1 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")
toxisch2 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")
toxisch3 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")
toxisch4 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")
toxisch5 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")
toxisch6 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")
toxisch7 = MyOptionMenu(loginframe, "- Auswählen -",
                        "Keine Probe", "Toxisch", "Nicht toxisch")

# --- englisch ---

# Fundort
place = tk.Label(loginframe, text="Place", bg=bgDef, font="HELVETICA 22 bold")
place1 = tk.Label(loginframe, text="1", bg=bgDef, font="HELVETICA 18 bold")
place2 = tk.Label(loginframe, text="2", bg=bgDef, font="HELVETICA 18 bold")
place3 = tk.Label(loginframe, text="3", bg=bgDef, font="HELVETICA 18 bold")
place4 = tk.Label(loginframe, text="4", bg=bgDef, font="HELVETICA 18 bold")
place5 = tk.Label(loginframe, text="5", bg=bgDef, font="HELVETICA 18 bold")
place6 = tk.Label(loginframe, text="6", bg=bgDef, font="HELVETICA 18 bold")
place7 = tk.Label(loginframe, text="7", bg=bgDef, font="HELVETICA 18 bold")
# Objekt
proof = tk.Label(loginframe, text="Object", bg=bgDef, font="HELVETICA 22 bold")
proof1 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
proof2 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
proof3 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
proof4 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
proof5 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
proof6 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
proof7 = MyOptionMenu(loginframe, textSTD_en, "Cup", "Donut",
                      "Guidebook", "Pen", "Pills", "Sugar", "Sweetener")
# Person 1
personOne = tk.Label(loginframe, text="1st fingerprint",
                     bg=bgDef, font="HELVETICA 22 bold")
en_person11 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person12 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person13 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person14 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person15 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person16 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person17 = MyOptionMenu(loginframe, textSTD_en, "- none -", "Eva",
                           "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
# Person 2
personTwo = tk.Label(loginframe, text="2nd fingerprint",
                     bg=bgDef, font="HELVETICA 22 bold")
en_person21 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person22 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person23 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person24 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person25 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person26 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
en_person27 = MyOptionMenu(loginframe, "- none -", "- none -", "Unknown",
                           "Eva", "Jakob", "Janine", "Jessica", "Johannes", "Julius", "Luise")
# Toxic/not toxic
toxic = tk.Label(loginframe, text="Toxicity",
                 bg=bgDef, font="HELVETICA 22 bold")
toxic1 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")
toxic2 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")
toxic3 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")
toxic4 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")
toxic5 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")
toxic6 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")
toxic7 = MyOptionMenu(loginframe, "- choose -",
                      "no sample", "toxic", "non toxic")


# ------------------------ Sprachauswahl ------------------------
languageframe = tk.Frame(window, bg=bgDef, bd=200, height=700, width=700)

# Überschrift
labelHeadline = tk.Label(
    window, text="Sprache wählen | Please select your language", bg=bgDef, font="HELVETICA 40 bold")

# Deutsch
germanflag = tk.PhotoImage(file="/home/2cp/FINGERPRINT_SCANNER/img/deu.png")
labelGerFlag = tk.Label(languageframe, image=germanflag)
labelGerText = tk.Label(languageframe, text="Deutsch",
                        bg=bgDef, font="HELVETICA 30 bold")

# Englisch
englishflag = tk.PhotoImage(file="/home/2cp/FINGERPRINT_SCANNER/img/eng.png")
labelEnFlag = tk.Label(languageframe, image=englishflag)
labelEnText = tk.Label(languageframe, text="English",
                       bg=bgDef, font="HELVETICA 30 bold")

# ----------------------------------------------------------------------------------------------------------------------
# ----- Überprüfen der Angaben -----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


def check_de(event=0):
    if check_beweismittel() == 1 and check_person1() == 1 and check_person2() == 1 and check_toxisch() == 1:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(
            file="/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/deu/accepted.png")
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    elif check_beweismittel() == 2 and check_person1() == 2 and check_person2() == 1 and check_toxisch() == 2:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(
            file="/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/deu/hint.png")
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    else:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(
            file="/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/deu/declined.png")
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild


def check_en(event=0):
    if check_proof() == 1 and check_en_person1() == 1 and check_en_person2() == 1 and check_toxic() == 1:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(
            file="/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/eng/accepted.png")
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    elif check_proof() == 2 and check_en_person1() == 2 and check_en_person2() == 1 and check_toxic() == 2:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(
            file="/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/eng/hint.png")
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    else:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(
            file="/home/2cp/FINGERPRINT_SCANNER/img/hh/messages/eng/declined.png")
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


# ----------------------------------------------------------------------------------------------------------------------
# ----- Buttons zur Bestätigung der Auswahl ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
ButtonSendGer = tk.Button(loginframe, text="Absenden",
                          font="HELVETICA 18 bold", command=check_de, bg='#E2E2E2')
ButtonSendEn = tk.Button(loginframe, text="Submit",
                         font="HELVETICA 18 bold", command=check_en, bg='#E2E2E2')

# ----------------------------------------------------------------------------------------------------------------------
# ----- Hauptbildschirm ------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


def SelectGerman(event=0):
    languageframe.grid_forget()
    labelHeadline.grid_forget()
    loginframe.grid(row=1, column=1)
    bg_de.grid(row=1, column=1)
    ort.grid(row=0, sticky=W+E, padx=tabpadx)
    ort1.grid(row=1, sticky=W+E, padx=tabpadx)
    ort2.grid(row=2, sticky=W+E, padx=tabpadx)
    ort3.grid(row=3, sticky=W+E, padx=tabpadx)
    ort4.grid(row=4, sticky=W+E, padx=tabpadx)
    ort5.grid(row=5, sticky=W+E, padx=tabpadx)
    ort6.grid(row=6, sticky=W+E, padx=tabpadx)
    ort7.grid(row=7, sticky=W+E, padx=tabpadx)
    beweismittel.grid(row=0, column=1, sticky=W+E, padx=tabpadx)
    beweismittel1.grid(row=1, column=1, sticky=E+W, padx=tabpadx)
    beweismittel2.grid(row=2, column=1, sticky=E+W, padx=tabpadx)
    beweismittel3.grid(row=3, column=1, sticky=E+W, padx=tabpadx)
    beweismittel4.grid(row=4, column=1, sticky=E+W, padx=tabpadx)
    beweismittel5.grid(row=5, column=1, sticky=E+W, padx=tabpadx)
    beweismittel6.grid(row=6, column=1, sticky=E+W, padx=tabpadx)
    beweismittel7.grid(row=7, column=1, sticky=E+W, padx=tabpadx)
    personEins.grid(row=0, column=2, sticky=W+E, padx=tabpadx)
    person11.grid(row=1, column=2, sticky=W, padx=tabpadx)
    person12.grid(row=2, column=2, sticky=W, padx=tabpadx)
    person13.grid(row=3, column=2, sticky=W, padx=tabpadx)
    person14.grid(row=4, column=2, sticky=W, padx=tabpadx)
    person15.grid(row=5, column=2, sticky=W, padx=tabpadx)
    person16.grid(row=6, column=2, sticky=W, padx=tabpadx)
    person17.grid(row=7, column=2, sticky=W, padx=tabpadx)
    personZwei.grid(row=0, column=3, sticky=W+E, padx=tabpadx)
    person21.grid(row=1, column=3, sticky=W, padx=tabpadx)
    person22.grid(row=2, column=3, sticky=W, padx=tabpadx)
    person23.grid(row=3, column=3, sticky=W, padx=tabpadx)
    person24.grid(row=4, column=3, sticky=W, padx=tabpadx)
    person25.grid(row=5, column=3, sticky=W, padx=tabpadx)
    person26.grid(row=6, column=3, sticky=W, padx=tabpadx)
    person27.grid(row=7, column=3, sticky=W, padx=tabpadx)
    Toxisch.grid(row=0, column=4, sticky=W+E, padx=tabpadx)
    toxisch1.grid(row=1, column=4, sticky=W, padx=tabpadx)
    toxisch2.grid(row=2, column=4, sticky=W, padx=tabpadx)
    toxisch3.grid(row=3, column=4, sticky=W, padx=tabpadx)
    toxisch4.grid(row=4, column=4, sticky=W, padx=tabpadx)
    toxisch5.grid(row=5, column=4, sticky=W, padx=tabpadx)
    toxisch6.grid(row=6, column=4, sticky=W, padx=tabpadx)
    toxisch7.grid(row=7, column=4, sticky=W, padx=tabpadx)
    ButtonGer.grid_forget()
    ButtonEn.grid_forget()
    ButtonSendGer.grid(row=8, column=4, sticky=W, padx=tabpadx, pady=20)
    ButtonScan.grid(row=8, column=1, rowspan=2,
                    stick=W+E, pady=20, padx=tabpadx)
    # Activate scanning ability
    ButtonScan["state"] = tk.NORMAL


def SelectEnglish(event=0):
    languageframe.grid_forget()
    labelHeadline.grid_forget()
    loginframe.grid(row=1, column=1)
    bg_en.grid(row=1, column=1)
    place.grid(row=0, sticky=W+E, padx=tabpadx)
    place1.grid(row=1, sticky=W+E, padx=tabpadx)
    place2.grid(row=2, sticky=W+E, padx=tabpadx)
    place3.grid(row=3, sticky=W+E, padx=tabpadx)
    place4.grid(row=4, sticky=W+E, padx=tabpadx)
    place5.grid(row=5, sticky=W+E, padx=tabpadx)
    place6.grid(row=6, sticky=W+E, padx=tabpadx)
    place7.grid(row=7, sticky=W+E, padx=tabpadx)
    proof.grid(row=0, column=1, sticky=W+E, padx=tabpadx)
    proof1.grid(row=1, column=1, sticky=W, padx=tabpadx)
    proof2.grid(row=2, column=1, sticky=W, padx=tabpadx)
    proof3.grid(row=3, column=1, sticky=W, padx=tabpadx)
    proof4.grid(row=4, column=1, sticky=W, padx=tabpadx)
    proof5.grid(row=5, column=1, sticky=W, padx=tabpadx)
    proof6.grid(row=6, column=1, sticky=W, padx=tabpadx)
    proof7.grid(row=7, column=1, sticky=W, padx=tabpadx)
    personOne.grid(row=0, column=2, sticky=W+E, padx=tabpadx)
    en_person11.grid(row=1, column=2, sticky=E+W, padx=tabpadx)
    en_person12.grid(row=2, column=2, sticky=E+W, padx=tabpadx)
    en_person13.grid(row=3, column=2, sticky=E+W, padx=tabpadx)
    en_person14.grid(row=4, column=2, sticky=E+W, padx=tabpadx)
    en_person15.grid(row=5, column=2, sticky=E+W, padx=tabpadx)
    en_person16.grid(row=6, column=2, sticky=E+W, padx=tabpadx)
    en_person17.grid(row=7, column=2, sticky=E+W, padx=tabpadx)
    personTwo.grid(row=0, column=3, sticky=W+E, padx=tabpadx)
    en_person21.grid(row=1, column=3, sticky=E+W, padx=tabpadx)
    en_person22.grid(row=2, column=3, sticky=E+W, padx=tabpadx)
    en_person23.grid(row=3, column=3, sticky=E+W, padx=tabpadx)
    en_person24.grid(row=4, column=3, sticky=E+W, padx=tabpadx)
    en_person25.grid(row=5, column=3, sticky=E+W, padx=tabpadx)
    en_person26.grid(row=6, column=3, sticky=E+W, padx=tabpadx)
    en_person27.grid(row=7, column=3, sticky=E+W, padx=tabpadx)
    toxic.grid(row=0, column=4, sticky=W+E, padx=tabpadx)
    toxic1.grid(row=1, column=4, sticky=E+W, padx=tabpadx)
    toxic2.grid(row=2, column=4, sticky=E+W, padx=tabpadx)
    toxic3.grid(row=3, column=4, sticky=E+W, padx=tabpadx)
    toxic4.grid(row=4, column=4, sticky=E+W, padx=tabpadx)
    toxic5.grid(row=5, column=4, sticky=E+W, padx=tabpadx)
    toxic6.grid(row=6, column=4, sticky=E+W, padx=tabpadx)
    toxic7.grid(row=7, column=4, sticky=E+W, padx=tabpadx)
    ButtonGer.grid_forget()
    ButtonEn.grid_forget()
    ButtonSendEn.grid(row=8, column=4, sticky=W, padx=tabpadx, pady=20)
    ButtonScan.grid(row=8, column=1, rowspan=2,
                    stick=W+E, pady=20, padx=tabpadx)
    # Activate scanning ability
    ButtonScan["state"] = tk.NORMAL


# ------------------------ Buttons um zum Hauptbildschirm zu gelangen ------------------------
ButtonGer = tk.Button(languageframe, image=germanflag, command=SelectGerman)
ButtonEn = tk.Button(languageframe, image=englishflag, command=SelectEnglish)

# Sprachauswahl Widgets
languageframe.grid(row=1, column=1)
labelHeadline.grid(row=0, column=0, sticky=W+E, columnspan=3)
ButtonGer.grid(row=0, column=0, sticky=W+E, padx=tabpadx, pady=20)
ButtonEn.grid(row=1, column=0, sticky=W+E, padx=tabpadx, pady=20)

'''
def dismiss(event):
    label2.grid_forget()
    loginframe.grid(row=1, column=1)
    username.grid(row=0, sticky=W)
    passwordtext.grid(row=1, sticky=W)
    entry0.grid(row=0, column=1)
    entry1.grid(row=1, column=1)
    label1.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
    button1.grid(row=2, column=1, sticky=W+E)
    button2.grid(row=2, column=3, sticky=W+E, padx=10)
        
# Tastenbindung
window.bind('<Escape>', dismiss)

# Mainloop
'''
if __name__ == "__main__":
    # Lock cursor inside gui
    pyautogui.FAILSAFE = False
    #root.bind('<Motion>', motion)
    # reset_mouse(event=None)
    #top2.bind('<Enter>', reset_mouse)
    top2.config(cursor="none")

    warning_popup = None
    picture_popup = None

    # start door checking thread
    chk_door = Check_pin(door_lock_pin)
    c1 = Thread(target=chk_door.checkloop)
    c1.start()

    videopanel = tk.Frame(top2)
    canvas = tk.Canvas(videopanel,  bg="black", bd=0, highlightthickness=0,
                       relief='ridge').pack(fill=tk.BOTH, expand=1)
    videopanel.pack(fill=tk.BOTH, expand=1)
    window.mainloop()
