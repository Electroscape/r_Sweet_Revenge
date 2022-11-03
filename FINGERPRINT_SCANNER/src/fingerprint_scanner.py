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
Global tkinter variables
=========================================================================================================
'''

root = tk.Tk()
scrW = root.winfo_screenwidth()
scrH = root.winfo_screenheight()
top2 = tk.Toplevel(root, bg='#000000')
geo_str = str(scrW) + "x" + str(scrH)
window = root
window.geometry(geo_str)
window.title("Forensik Hamburg")
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(2, weight=1)
window.configure(background=config['TKINTER']['background-color'])
window.attributes('-fullscreen', True)


pyautogui.FAILSAFE = False
warning_popup = None
picture_popup = None

# ------------------------ Frame ----------------------------------
frame_login = tk.Frame(window, bg=config['TKINTER']['background-color'], bd=0, height=700, width=1620)
frame_language = tk.Frame(window, bg=config['TKINTER']['background-color'], bd=200, height=700, width=700)

# ------------------------ Images ---------------------------------
bg_image_de = tk.PhotoImage(file = config['PATH']['image'] + city + '/background/deu/background.png')
bg_image_en = tk.PhotoImage(file = config['PATH']['image'] + city + '/background/eng/background.png')
flag_deu = tk.PhotoImage(file = config['PATH']['image'] + 'deu.png')
flag_eng = tk.PhotoImage(file = config['PATH']['image'] + 'eng.png')

# ------------------------ Label ----------------------------------
label_headline = tk.Label(window, text="Sprache wählen | Please select your language", bg=config['TKINTER']['background-color'], font="HELVETICA 40 bold")
label_background_deu = tk.Label(window, image=bg_image_de)
label_background_eng = tk.Label(window, image=bg_image_en)
#label_background_eng = tk.Label(frame_login, bg='#FFFFFF')
label_flag_deu = tk.Label(frame_language, image=flag_deu)
label_flag_eng = tk.Label(frame_language, image=flag_eng)
label_text_deu = tk.Label(frame_language, text="Deutsch", bg=config['TKINTER']['background-color'], font="HELVETICA 30 bold")
label_text_eng = tk.Label(frame_language, text="English", bg=config['TKINTER']['background-color'], font="HELVETICA 30 bold")

# ------------------------ Buttons ------------------------

button_deu = tk.Button(frame_language, image=flag_deu, command=lambda: select_deu())
button_eng = tk.Button(frame_language, image=flag_eng, command=lambda: select_eng())

'''
=========================================================================================================
Global VLC variables
=========================================================================================================
'''

vlc_instance = vlc.Instance("--no-xlib") # creating Instance class object
player = vlc_instance.media_player_new() # creating a new media object


'''
=========================================================================================================
PN532 init
=========================================================================================================
'''

pn532 = PN532_I2C(busio.I2C(board.SCL, board.SDA), debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
sleep(0.5)  # this delay avoids some problems after wakeup
pn532.SAM_configuration()   # Configure PN532 to communicate with MiFare cards


'''
=========================================================================================================
GPIO init
=========================================================================================================
'''
GPIO.setmode(GPIO.BCM)

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
                    #scan_field()
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
VLC init
=========================================================================================================
'''
def play_video(path):

    '''
    Description
    -----------
    Displaying the video once sensor is high
    set the mrl of the video to the mediaplayer
    play the video and

    "mp4" = scanner video.mp4

    '''
    #player.set_fullscreen(True) # set full screen
    player.set_xwindow(videopanel.winfo_id())

    player.set_mrl(path)    #setting the media in the mediaplayer object created
    player.play()           # play the video
    if path[-3:] == "mp4":  #check if its the scanner video
        while player.get_state() != vlc.State.Ended : # loop until the video is finished
            continue
        return True
    else : 
        while True:
            continue

'''
=========================================================================================================
RFID functions
=========================================================================================================
'''
def authenticate(uid, read_block): #does the authentication if its a classic tag
    rc = 0
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rc = pn532.mifare_classic_authenticate_block(
        uid, read_block, MIFARE_CMD_AUTH_A, key)
   
    return rc

def card_func(sample_var):
    sleep(1)
    global picture_popup

    try:
        picture_popup.destroy()
    except (AttributeError, NameError):
        picture_popup = None

    toplevel = tk.Toplevel()

   
    x = root.winfo_x()
    y = root.winfo_y()
    str_geo = "+%d+%d" % (x, y)
    print("img @ " + str_geo)
    toplevel.geometry(str_geo)

    toplevel.title("Scanning result")
    FA_Bild = tk.PhotoImage(file = config['PATH']['image'] + 'fingerprints/' + config["CARDS_IMAGES"].get(sample_var, config["CARDS_IMAGES"]["unk"]))
    FA_Label = tk.Label(toplevel, image=FA_Bild)
    FA_Label.image = FA_Bild
    FA_Label.grid()

  
    toplevel.resizable(0, 0)  # will remove the top badge of window
    toplevel.lift(root)
    picture_popup = toplevel

def foo():      # dummy function
    pass

def return_to_normal():
    global ButtonScan
    ButtonScan["command"] = scan_field

def scan_field():
    
    '''
    scans the cards and checks whethers its a classic or ntag.
    if the card is present and read correctly displays the fingerprint

    '''
    global warning_popup
    global ButtonScan
    global window

    try:
        warning_popup.destroy()
    except (AttributeError, NameError):
        warning_popup = None
    
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
  
    play_video(config['PATH']['video'] + 'scannerfilm_mit_sound.mp4')

    # Found Solution
    success = False
    msg = ["Timeout!", "Beweismittel richtig einlegen \n Object not placed correctly"]
    

    uid = None
    while chk_door.is_door_closed(): #check door is closed
    
        
        uid = rfid_present()
        
        print('.', end="")
        # Try again if no card is available.
        sleep(0.2)

        if uid is None: # check if card is detected

            count += 1
            print("in")
            if count > 10:
                
                print("Timeout! Failed to read")
                break

        else: #card is found 
            print('Found card with UID:', [hex(i) for i in uid])
            break

    print("Out while")

    if uid: # ensure that the card is inside

        read_data = rfid_read(uid,config["BLOCK"]["read_block"])

        print('data is: {}'.format(read_data))
        if read_data:
            success = True
        else:
            msg = [
                "Fehler", "Beweismittel richtig einlegen - Object not placed correctly"]
    
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

def rfid_read(uid, block):

    '''
    Checks if the card is read or not 
    '''

    try:
        # if classic tag
        auth = authenticate(uid, block)
    except Exception:
        # if ntag
        auth = False

    try:
        # Switch between ntag and classic
        if auth:  # True for classic and False for ntags
            data = pn532.mifare_classic_read_block(block)
        else:
            data = pn532.ntag2xx_read_block(block)

        if data is not None:
            read_data = data.decode('utf-8')[:2]
            
        else:
            read_data = False
            print("None block")

    except Exception as e:
        print(e)

    return read_data


def rfid_present():

    '''
    checks if the card is present inside the box
    '''
    try:
        uid = pn532.read_passive_target(timeout=0.5) #read the card
    except RuntimeError:
        uid = None
        return uid 
    return uid



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
    

    try:
        warning_popup.destroy()
    except (AttributeError, NameError):
        warning_popup = None

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


def check_language(event=0):

    '''
    Displays the pictures based on whether its german or english
    '''
    
    if check_proof() == 1 and check_person1() == 1 and check_person2() == 1 and check_toxic() == 1:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + f'/messages/{language}/accepted.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    elif check_proof() == 2 and check_person1() == 2 and check_person2() == 1 and check_toxic() == 2:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + f'/messages/{language}/hint.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild
    else:
        toplevel = tk.Toplevel()
        Richter_Bild = tk.PhotoImage(file = config['PATH']['image'] + city + f'/messages/{language}/declined.png')
        Richter_Label = tk.Label(toplevel, image=Richter_Bild)
        Richter_Label.grid()
        Richter_Label.image = Richter_Bild

def check_proof():

    '''
    compares the entered proofs by th user with the correct ones
    '''

    list_proof = proof[1:]
    proof_check = [(p.var).get() for p in list_proof]

    if language == "deu":
       
        if texts[city]["deu"]["check_beweismittel_richtig"] == proof_check:
            
            var_proof =1 
    
        elif texts[city]["deu"]["check_beweismittel_fast_richtig"] == proof_check:
        
            var_proof = 2
        else :
            var_proof = 0

    else:
       
        if texts[city]["eng"]["proof_correct"] == proof_check:
            
            var_proof = 1

        elif texts[city]["eng"]["proof_almost_correct"] == proof_check:
            var_proof = 2

        else :
            var_proof = 0

    return var_proof


def check_person1():

    '''
    compares the entered person1 data by th user with the correct ones
    '''

    list_person_one = person_one[1:]
    person1_check = [(p.var).get() for p in list_person_one]

    if language == "deu":
        
        if texts[city]["deu"]["check_deu_person1_richtig"] == person1_check:
            var_person1 = 1
            

        elif texts[city]["deu"]["check_deu_person1_fast_richtig"] == person1_check:
            var_person1 = 2
        else :
            var_person1 = 0
       

    else :
     
        if texts[city]["eng"]["check_en_person1_correct"] == person1_check:
            var_person1 = 1
    
        elif texts[city]["eng"]["check_en_person1_almost_correct"] == person1_check:
            var_person1 = 2
        else :
            var_person1 = 0
 
    return var_person1
        

def check_person2():

    '''
    compares the entered person 2 data by th user with the correct ones
    '''

    list_person_two = person_two[1:]
    person2_check = [(p.var).get() for p in list_person_two]

    if language == "deu":
     
        if texts[city]["deu"]["check_deu_person2_richtig"] == person2_check:
            
            var_person2 = 1
        else :
            var_person2 = 0

    else :
        if texts[city]["eng"]["check_en_person2_correct"] == person2_check:
            var_person2 = 1
        else :
            var_person2 = 0
  
    return var_person2


def check_toxic():

    '''
    compares the entered toxic data by th user with the correct ones
    '''

    list_toxic = toxicity[1:]
    toxic_check = [(p.var).get() for p in list_toxic]

    if language == "deu":
        
         if texts[city]["deu"]["check_toxisch_richtig"] == toxic_check:
            var_toxic = 1
           
         elif texts[city]["deu"]["check_toxisch_fast_richtig"] == toxic_check:
            var_toxic = 2
         else :
            var_toxic  = 0
   
    else :  
    
        if texts[city]["eng"]["check_toxic_correct"] == toxic_check:
            var_toxic = 1

        elif texts[city]["eng"]["check_toxic_almost_correct"] == toxic_check:
            var_toxic = 2
        else :
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
    label_background_eng.place(x=0,y=0)
    label_background_eng.lower()
    evidence_collection()


def select_deu():
    global language
    language = 'deu'
    label_background_deu.place(x=0,y=0)
    label_background_deu.lower()
    evidence_collection()
    
    


def evidence_collection():

    frame_language.grid_forget()
    label_headline.grid_forget()
    button_deu.grid_forget()
    button_eng.grid_forget()
    
    
    frame_login.grid(column=1,row=1)
    ButtonScan.grid(row=8, column=1, rowspan=2, stick=W+E, pady=20, padx=config['TKINTER']['tabpadx'])

    places.append(tk.Label(frame_login, text=texts['all'][language]['head_place'], bg=config['TKINTER']['background-color'], font="HELVETICA 22 bold"))
    for i in range(1, 8):
        places.append(tk.Label(frame_login, text=i, bg=config['TKINTER']['background-color'], font="HELVETICA 18 bold"))
    for i in range(0,len(places)):
        places[i].grid(row=i, sticky=W+E, padx=config['TKINTER']['tabpadx'])

    init_dropdown(proof, texts['all'][language]['head_object'], texts[city][language]['dropdown_objects'])
    for i in range(len(proof)):
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

    if language == "deu" :
        ButtonSendGer.grid(row=8, column=4, sticky=W, padx=config['TKINTER']['tabpadx'], pady=20)    
    else:
        ButtonSendEn.grid(row=8, column=4, sticky=W, padx=config['TKINTER']['tabpadx'], pady=20)  

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
def main():

    root.title("Fingerprint scanner")

    # We will create two screens: one for the interface, one for laser scanner
    # small screen root

    top2.geometry("+0+0")
    top2.attributes('-fullscreen', tk.TRUE)
    top2.wm_attributes("-topmost", 1)  # make sure window is on top to start
    top2.config(cursor="none")
    # big screen

    root.option_add('*Dialog.msg.width', 34)
    print("Geo str: " + geo_str)
    
    
    
    ButtonScan["state"] = tk.DISABLED   # Disable scanning ability

    sleep(1)
    
    landingpage()
    

# Mainloop

if __name__ == "__main__":

    ButtonSendGer = tk.Button(frame_login, text="Absenden", font="HELVETICA 18 bold", command=check_language, bg='#E2E2E2')
    ButtonSendEn = tk.Button(frame_login, text="Submit", font="HELVETICA 18 bold", command=check_language, bg='#E2E2E2')
    ButtonScan = tk.Button(frame_login, text="SCAN", font="HELVETICA 18 bold", command=scan_field, bg='#BB3030', fg='#E0E0E0')
    ButtonScan.config(activebackground='#FF5050')

    chk_door = Check_pin(config['PIN'][city]['door'])
    c1 = Thread(target=chk_door.checkloop)
    c1.start()
    videopanel = tk.Frame(top2)
    canvas = tk.Canvas(videopanel,  bg="black", bd=0, highlightthickness=0, relief='ridge').pack(fill=tk.BOTH, expand=1)
    videopanel.pack(fill=tk.BOTH, expand=1)
    

    main()
    window.mainloop()