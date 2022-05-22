from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from ttkwidgets.autocomplete import AutocompleteEntry
from hdpitkinter import HdpiTk
from PIL import Image, ImageTk
from pathlib import Path
import sqlite3
import json
import cryptography
import shelve
import pyperclip
import os
import re
import random
import sys
import uuid
import base64
import db

version = '1.0'


# font&colors
boxfont = ("consolas", 18)
boxfont_l = ("roboto", 14)
root_bg = "#004853"
softblue = "#14596d"
softblue2 = "#2c7e96"
splash_bg = "#3c5c5b"
splash_txt_color = "#adbcdf"
button_font = ("consolas", 13, "bold")
button_bg = "#036e72"
labelfont = ("roboto", 14)
labelfont_large = ("helvatica", 18, 'bold')
labelfont_small = ("roboto", 12)
labelfont_l = ("roboto", 12)  # little
labelfont_h = ("roboto", 12)
labelfont_c = ("consolas", 13)
nightblue = "#0799c2"
blue2 = "#0a9dad"
blue3 = "#064a89"
deepred = "#c51827"
mint = '#00ffec'
deepgreen = '#004444'

icon_dir = Path.cwd()/'static'
applogo = icon_dir/'key.ico'
setup_dir = Path.home()/'AppData/Roaming/passito/appsys'

def pass_generator(length=12):
    special_characters = ('@', '#', '$', '%', '&', '*', '?', '!')
    lowercases = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                  'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                  'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                  'z'
                  )
    uppercases = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                  'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                  'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                  'Z'
                  )
    numbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
    all_chars = (special_characters + lowercases + uppercases + numbers)

    rand_special = random.choice(special_characters)
    rand_lower = random.choice(lowercases)
    rand_upper = random.choice(uppercases)
    rand_number = random.choice(numbers)

    temp_pass = rand_special + rand_upper + rand_lower + rand_number

    for i in range(length-4):
        anything = random.choice(all_chars)
        temp_pass = temp_pass + anything

    result_password = ''.join(random.sample(temp_pass, len(temp_pass)))
    return result_password

if not setup_dir.exists():
    try:
        os.makedirs(setup_dir)
        security_key = pass_generator(35)
        sysdata = {
            'gall_interval':10,
            'gp_length':12, 
            'security_key':security_key,
            'getall_posx':0,
            'getall_posy':0,
            'backup_dir': str(Path.home()/'Documents/passito_backup'),
        }
        sysfile = str(setup_dir/'config.json')
        with open(sysfile, 'w') as f:
            json.dump(sysdata, f, indent=4)
        
    except Exception as exc:
        res_ = messagebox.showerror('error', f'An unexpected error occured\nError info: {exc}')
        if res_:
            try:
                sys.exit()
            except:
                pass

data_dir = Path.home()/'AppData/Roaming/passito/database'
if not data_dir.exists():
    os.makedirs(data_dir)

# Database initialization
db_file = data_dir/'passito.db'
if not db_file.exists():
    conn = sqlite3.connect(str(db_file))
    db.create_passito(conn)

conn = sqlite3.connect(str(db_file))
all_accounts = db.get_id_name_list(conn)


def on_enter(button, bg='#006666'):
    button['background'] = bg

def on_leave(button, bg=button_bg):
    button['background'] = bg

def get_sysdata(key=None):
    sysfile = str(setup_dir/'config.json')
    with open(sysfile, 'r') as f:
        sysdata = json.loads(f.read())
    if key is None:
        return sysdata
    else:
        return sysdata[key]

def add_sysdata(key, value):
    sysfile = str(setup_dir/'config.json')
    _sysdata = get_sysdata()
    _sysdata[key] = value
    with open(sysfile, 'w') as f:
        json.dump(_sysdata, f, indent=4)

def update_sysdata(key, newvalue):
    sysfile = str(setup_dir/'config.json')
    _sysdata = get_sysdata()
    _sysdata[key] = newvalue
    with open(sysfile, 'w') as f:
        json.dump(_sysdata, f, indent=4)

def generate_pass_checkpost():
    sysdata = get_sysdata()
    length = sysdata['gp_length']
    password = pass_generator(length)
    pyperclip.copy(password)


def get_key(base=None) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=32,
        salt=b'K2?uY#I%K3n4',
        iterations=100000,
        backend=default_backend()
    )
    if base is None:
        sysdata = get_sysdata()
        security_key = sysdata['security_key']
    else:
        security_key = base
    _key_ = base64.urlsafe_b64encode(kdf.derive(security_key.encode()))
    return _key_


current_key = get_key()


def encrypt_(string: str, key=current_key) -> str:
    engine_ = Fernet(key)
    cipher = engine_.encrypt(string.encode())
    return cipher.decode()


def decrypt_(cipher: str, key=current_key) -> str:
    engine_ = Fernet(key)
    bytes_ = engine_.decrypt(cipher.encode())
    return bytes_.decode()


def reset_security_key():
    ree = HdpiTk()
    width_ = ree.winfo_screenmmwidth()
    height_ = ree.winfo_screenheight()
    ree.geometry(f'520x240+{int(width_ * 1.7)}+{int(height_ * 0.4)}')
    ree.overrideredirect(True)
    ree.configure(bg=deepgreen)
    ree.attributes('-topmost', True)
    ree.resizable(width=0, height=0)
    ree.iconbitmap(applogo)
    ree.focus_set()

    load_img = Image.open(icon_dir / 'warn1.png')
    warn_i = ImageTk.PhotoImage(load_img)

    def continue_command(event=None):
        got__security_key = idbox_.get()
        if len(got__security_key) == 0:
            f1 = Frame(ree, bg=deepgreen, bd=0)
            f1.place(x=30, y=190)

            Label(f1, image=warn_i, bg=deepgreen).pack(side=LEFT)
            Label(f1, text='Enter correct security key', font=('segoe ui', 12, 'bold'), fg='yellow',
                  bg=deepgreen, padx=5).pack(side=RIGHT)
            idbox_.delete(0, END)
            try:
                ree.after(1500, lambda: clear_widget(widget=f1, window=ree))
            except:
                pass
            return None
        update_sysdata('security_key', got__security_key)
        res_ = messagebox.showinfo(title='updated', message='security key updated\nnow restart passito')
        if res_:
            sys.exit()

    # logo
    s_logo = ImageTk.PhotoImage(Image.open(icon_dir / 'pg2.png'))
    s_logo_label = Label(ree, image=s_logo, bg=deepgreen)
    s_logo_label.place(x=10, y=10)

    # other elements
    _label_ = Label(ree, text="Invalid security key", bg=deepred, fg='white', font=("Seoge UI", 13, 'bold')
                    , width=48)
    _label_.place(x=17, y=50)
    _label = Label(ree, text="Please enter correct security key, otherwise\n"
                             "you won't be able to access data",
                   bg=deepgreen, fg=mint, font=("Seoge UI", 12), justify=LEFT)
    _label.place(x=15, y=95)

    idbox_ = Entry(ree, width=35, font=boxfont, bg='#006666', fg='#1fff00', bd=0, insertbackground='#1fff00')
    idbox_.place(x=30, y=150)
    idbox_.focus_force()
    idbox_.bind('<Return>', continue_command)

    close_b = Button(ree, text='☓', font=('Segoe UI', 12), width=3, command=lambda: sys.exit(),
                     bg=splash_bg, fg="#FFFFFF", bd=0, activebackground='red',
                     activeforeground="white")
    close_b.place(x=486, y=0)
    close_b.bind('<Enter>', lambda event: on_enter(close_b, bg=deepred))
    close_b.bind('<Leave>', lambda event: on_leave(close_b, bg=splash_bg))

    continue_ = Button(ree, text='continue', bg='#005555', font=button_font, fg='#ffffff', bd=0, width=10,
                       command=continue_command, activebackground='cyan', relief='flat', activeforeground="#0799c2")
    continue_.place(x=390, y=190)
    continue_.bind('<Enter>', lambda event: on_enter(continue_))
    continue_.bind('<Leave>', lambda event: on_leave(continue_, bg='#005555'))
    ree.mainloop()


def setup_pass():
    setup_w = HdpiTk()
    s_width = setup_w.winfo_screenmmwidth()
    s_height = setup_w.winfo_screenheight()
    setup_w.geometry(f"470x315+{int(s_width * 1.805)}+{int(s_height * 0.4)}")
    setup_w.overrideredirect(True)
    setup_w.resizable(width=0, height=0)
    setup_w.iconbitmap(applogo)
    setup_w.configure(bg=root_bg)
    setup_w.attributes('-topmost', True)
    l1 = Label(setup_w, text='Welcome to ',
               bg=root_bg, fg='#abedef', font=("Segoe UI", 18))
    l1.place(x=112, y=26)
    l2 = Label(setup_w, text='Please choose a PassKey',
               bg=root_bg, fg='#00ffec', font=labelfont_c)
    l2.place(x=40, y=77)

    # artwork
    baymax = ImageTk.PhotoImage(Image.open(icon_dir / "c.png"))
    bmx_banner_label = Label(setup_w, image=baymax, bg=root_bg, bd=0)
    bmx_banner_label.place(x=360, y=35)
    # logo
    logo_image = ImageTk.PhotoImage(Image.open(icon_dir / 'b2c.png'))
    logo_image_label = Label(setup_w, image=logo_image, bg=root_bg, bd=0)
    logo_image_label.place(x=255, y=25)

    success_value = BooleanVar(setup_w)

    # functions
    def save_command(event=None):
        passkey = passwordbox.get()
        r_password = r_password_box.get()
        if len(passkey) == 0 or len(r_password) == 0:
            messagebox.showwarning(title='blank fields', message='All the required fields needs to be filled')
            return None
        if passkey != r_password:
            messagebox.showwarning(title="unmatched", message='Passkeys doesn\'t match')
            try:
                r_password_box.delete(0, END)
                r_password_box.focus_force()
            except TclError:
                pass
            return None
        else:
            try:
                _e_passkey = encrypt_(passkey)
                add_sysdata('passkey', _e_passkey)
                res = messagebox.showinfo(title='welcome', message='Good To Go!\nAlways remember this passkey.\n'
                                                                   'If you forget this, passito will forget you.\n'
                                                                   'So please.. remember one for passito, '
                                                                   'passito will remember rest of yours.')
                if res:
                    success_value.set(True)
                    try:
                        setup_w.destroy()
                    except:
                        pass
            except Exception as exc_:
                messagebox.showerror('error', f'An unexpected error occured\nError info: {exc_}')
            return None

    def repres(state_var, box):
        if state_var.get():
            box.config(show='●')
            state_var.set(False)
            return
        else:
            box.config(show='')
            state_var.set(True)
            return

    # boxes
    password_box_label = Label(setup_w, text='passkey', bg='#006666', fg='white', width=9, font=button_font)
    password_box_label.place(x=44, y=121)
    passwordbox = Entry(setup_w, width=22, font=boxfont, show='●', bg='#008080', fg=mint, bd=0)
    passwordbox.place(x=130, y=120)
    pb_state = BooleanVar(setup_w)
    passwordbox.bind('<Escape>', lambda event: repres(pb_state, passwordbox))

    passwordbox.focus_force()
    passwordbox.configure(insertbackground=mint)
    passwordbox.focus_force()
    passwordbox.bind('<Return>', lambda event: r_password_box.focus_force())
    passwordbox.bind('<Down>', lambda event: r_password_box.focus_force())
    r_password_box_label = Label(setup_w, text='retype', bg='#006666', fg='white', width=9, font=button_font)
    r_password_box_label.place(x=44, y=161)
    r_password_box = Entry(setup_w, width=22, font=boxfont, show='●', bg='#008080', fg=mint, bd=0)
    r_password_box.place(x=130, y=160)
    r_pb_state = BooleanVar(setup_w)
    r_password_box.bind('<Escape>', lambda event: repres(r_pb_state, r_password_box))
    r_password_box.configure(insertbackground=mint)
    r_password_box.bind('<Up>', lambda event: passwordbox.focus_force())

    l_ = Label(setup_w, text="press Esc to show/hide",
               bg=root_bg, fg='gray', font=("Segoe UI", 11))
    l_.place(x=260, y=190)
    l3 = Label(setup_w, text="you'll need this passkey whenever you start the app",
               bg=root_bg, fg='#00ffec', font=("Segoe UI", 13))
    l3.place(x=35, y=220)
    # button
    save_b = Button(setup_w, text='looks good', font=button_font, width=20, command=save_command,
                        bg=button_bg, fg="#FFFFFF", bd=0, activebackground='cyan',
                        activeforeground="#0799c2")
    save_b.place(x=138, y=262)
    save_b.bind('<Enter>', lambda event: on_enter(save_b))
    save_b.bind('<Leave>', lambda event: on_leave(save_b))
    close_b = Button(setup_w, text='☓', font=('Segoe UI', 12), width=3, command=lambda: setup_w.destroy(),
                        bg=splash_bg, fg="#FFFFFF", bd=0, activebackground='red',
                        activeforeground="white")
    close_b.place(x=437, y=0)
    close_b.bind('<Enter>', lambda event: on_enter(close_b, bg=deepred))
    close_b.bind('<Leave>', lambda event: on_leave(close_b, bg=splash_bg))
    setup_w.mainloop()
    return success_value.get()


def clear_widget(widget, window):
    widget.place_forget()
    window.update()
    return None


def checkpost():
    _e_pass = get_sysdata('passkey')
    try:
        passkey = decrypt_(_e_pass)
    except cryptography.fernet.InvalidToken:
        reset_security_key()
        return None
    except Exception as ec_:
        messagebox.showerror('error', f'An unexpected error occured!\nerror info: {ec_}')
        return None

    cp_w = HdpiTk()
    screen_width = cp_w.winfo_screenmmwidth()
    screen_height = cp_w.winfo_screenheight()
    cp_w.geometry(f"500x200+{int(screen_width * 1.746)}+{int(screen_height * 0.4)}")
    cp_w.resizable(width=0, height=0)
    cp_w.title(f'passito checkpost')
    cp_w.iconbitmap(icon_dir/'l2.ico')
    cp_w.configure(bg=root_bg)
    cp_w.attributes('-topmost', True)

    l2 = Label(cp_w, text='Enter PassKey',
               bg=root_bg, fg='cyan', font=("consolas", 14, 'bold'))
    l2.place(x=36, y=60)
    lamp = BooleanVar(cp_w)
    # banner
    f1 = Frame(cp_w, bg=root_bg, bd=0)
    f1.pack(side=TOP, fill=X)
    banners = ['b6.png', 'b4.png', 'b5.png']
    current_banner = random.choice(banners)
    info_banner = ImageTk.PhotoImage(Image.open(icon_dir / current_banner))
    info_banner_label = Button(f1, image=info_banner, bg=root_bg, command=generate_pass_checkpost,
                               bd=0, activebackground=root_bg)
    info_banner_label.pack()
    load_img = Image.open(icon_dir / 'warn1.png')
    warn_i = ImageTk.PhotoImage(load_img)

    def sign_in(event=None):
        got_password = passwordbox.get()
        if len(got_password) == 0:
            f2 = Frame(cp_w, bg=root_bg, bd=0)
            f2.place(x=40, y=130)

            Label(f2, text='please enter passkey', font=('segoe ui', 12, 'bold'), fg='#00ff44',
                  bg=root_bg, padx=5).pack(side=RIGHT)
            try:
                cp_w.after(1200, lambda: clear_widget(widget=f2, window=cp_w))
            except:
                pass
            return None
        if passkey != got_password:
            f = Frame(cp_w, bg=root_bg, bd=0)
            f.place(x=41, y=130)
            Label(f, image=warn_i, bg=root_bg).pack(side=LEFT)
            Label(f, text='wrong passkey', font=('segoe ui', 12, 'bold'), fg='yellow', bg=root_bg, width=15,
                  padx=5, anchor='w').pack(side=RIGHT)
            passwordbox.delete(0, END)
            try:
                cp_w.after(1200, lambda: clear_widget(widget=f, window=cp_w))
            except:
                pass
            return None

        if passkey == got_password:
            lamp.set(True)
            cp_w.destroy()
            return None

    def b_icon(state_var, on_i, off_i):
        if state_var.get():
            state_var.set(False)
            return on_i
        else:
            state_var.set(True)
            return off_i

    def repres(state_var, box):
        if state_var.get():
            box.config(show='●')
            hu_.config(image=b_icon(hu_state, on_, off_))
            state_var.set(False)
            return
        else:
            box.config(show='')
            hu_.config(image=b_icon(hu_state, on_, off_))
            state_var.set(True)
            return

    # icons
    load1 = Image.open(icon_dir/'view.png')
    on_ = ImageTk.PhotoImage(load1)
    load2 = Image.open(icon_dir/'hide.png')
    off_ = ImageTk.PhotoImage(load2)

    # box
    passwordbox = Entry(cp_w, width=30, font=boxfont, bg=softblue, fg="cyan", bd=0, show='●')  # 357256
    passwordbox.place(x=40, y=95)
    passwordbox.focus()
    passwordbox.configure(insertbackground='cyan')
    passwordbox.bind('<Return>', sign_in)
    pb_state = BooleanVar(cp_w)
    passwordbox.bind('<Escape>', lambda event: repres(pb_state, passwordbox))

    hu_state = BooleanVar(cp_w)
    hu_ = Button(cp_w, image=b_icon(hu_state, on_, off_), bg=root_bg, command=lambda: repres(pb_state, passwordbox),
                        bd=0, activebackground=root_bg,)
    hu_.place(x=440, y=97)

    login_image = ImageTk.PhotoImage(Image.open(icon_dir / 'l.png'))
    enter_b = Button(cp_w, image=login_image, command=sign_in,
                         bg=root_bg, bd=0, activebackground=root_bg,
                         activeforeground="#0799c2")
    enter_b.place(x=230, y=138)

    cp_w.mainloop()
    return lamp.get()


sysfile = get_sysdata()
sysfile_parameters = list(sysfile.keys())

if 'passkey' in sysfile_parameters:
    confirm = checkpost()
    if confirm:
        pass
    else:
        sys.exit()
else:
    done = setup_pass()
    if done:
        pass
    else:
        sys.exit()

# main_window
root = HdpiTk()
root.focus_force()
width = root.winfo_screenmmwidth()
height = root.winfo_screenheight()
root.geometry(f"700x380+{int(width*1.5)}+{int(height*0.38)}")
root.resizable(width=0, height=0)
root.title(f'passito v{version}')
root.configure(bg=root_bg)

root.iconbitmap(applogo)

width_corner = int(width*1.05)
height_corner = int(height*0.65)

# icons
id_icon = ImageTk.PhotoImage(Image.open(icon_dir/'user.png'))
user_icon = ImageTk.PhotoImage(Image.open(icon_dir/'at.png'))
pass_icon = ImageTk.PhotoImage(Image.open(icon_dir/'pass2.png'))
retype_icon = ImageTk.PhotoImage(Image.open(icon_dir/'redo2.png'))


def close(window):
    window.destroy()
    return None


def show_info(title, message):
    messagebox.showinfo(title=title, message=message)


def email_or_user(string):
    pat = re.compile(f".*@.*\.")
    match = pat.search(string)
    if match:
        return 'Email'
    else:
        return 'Username'


def mymessage(geo, message, labelpos_x, labelpos_y, artwork, artpos_x, artpos_y, justify=CENTER, no_titlebar=True,
              bg_=splash_bg, delay=1.2, box_pos_x=(width * 1.9), box_pos_y=(height * 0.5),
              label_fg=splash_txt_color, topmost_value=True, transparency=0.95, to_be_focused=None):

    splash = Toplevel()
    splash.geometry(f'{geo}+{int(box_pos_x)}+{int(box_pos_y)}')
    splash.attributes('-topmost', topmost_value)
    splash.overrideredirect(no_titlebar)
    splash.configure(bg=bg_)
    splash.attributes('-alpha', transparency)
    splash.resizable(width=0, height=0)
    splash.iconbitmap(applogo)
    splash.focus_set()

    def close_splash():
        if to_be_focused is None:
            splash.destroy()
            return None
        else:
            splash.destroy()
            try:
                to_be_focused.focus_force()
            except TclError:
                pass
            return None

    splash.after(int(delay*1000), close_splash)

    Label(splash, text=message, bg=bg_, fg=label_fg, font=labelfont, justify=justify).place(x=labelpos_x, y=labelpos_y)
    pass_gen_w_art_image = ImageTk.PhotoImage(Image.open(artwork))
    pass_gen_w_art_label = Label(splash, image=pass_gen_w_art_image, bg=bg_)
    pass_gen_w_art_label.place(x=artpos_x, y=artpos_y)
    splash.mainloop()


def info_buttton_command(parent):
    if 'info' in wins:
        try:
            win = wins['info']
            win.focus_force()
        except:
            pass
        return None

    info_w = Toplevel(parent)
    info_w.title('About')
    info_w.geometry(f'400x300+{int(width_corner * 1.2)}+{int(height_corner)}')
    info_w.transient(parent)
    info_w.configure(bg=root_bg)
    info_w.resizable(width=0, height=0)
    info_w.iconbitmap(applogo)
    info_w.focus_set()
    wins['info'] = info_w

    def on_closing_():
        del wins['info']
        info_w.destroy()
        return None

    info_banner = ImageTk.PhotoImage(Image.open(icon_dir/'info_back_banner2.png'))
    info_banner_label = Label(info_w, image=info_banner, bg=root_bg, bd=0)
    info_banner_label.place(x=-1, y=-1)

    Label(info_w, text=f'version: {version}', font=('consolas',12), bg=root_bg, fg='gray').place(x=136, y=80)
    Label(info_w, text='Passito is a simple password manager app written in\n'
                       'python. All the associated data are stored only in your\n'
                       'pc unlike any cloud based password managers which\n'
                       'is not completely trustworthy. Passito was developed\n'
                       'with  a  goal  to  provide  users the full  control of  their\n'
                       'data.',
          font=labelfont_l, bg=root_bg, fg="#63A5AD", justify=LEFT).place(x=14, y=110)
    Label(info_w, text='A project by:', font=('consolas', 12), bg=root_bg, fg="#63A5AD").place(x=60, y=230)
    Label(info_w, text='Md. Saiful Islam Rony', font=('Segoe UI', 12), bg=root_bg, fg='#00C5CD').place(x=190, y=230)
    Label(info_w, text='To report an issue, pm me at ', font=('roboto', 11), bg=root_bg, fg="#63A5AD").place(x=30, y=260)
    Label(info_w, text='rniumo@gmail.com ', font=('Segoe UI', 12), bg=root_bg, fg='gray').place(x=225, y=257)
    info_w.protocol("WM_DELETE_WINDOW", on_closing_)
    info_w.mainloop()


def id_box_checker(id_name, id_list):
    if len(id_name) == 0:
        messagebox.showwarning(title='No input', message='Try entering an ID name or index')
        return None
    if id_name in id_list:
        return True
    else:
        messagebox.showerror(title=f'{id_name} not found', message='No such ID in the database!')
        return None


gall_posx = get_sysdata('getall_posx')
gall_posy = get_sysdata('getall_posy')


def gall_last_click(event):
    global gall_posx, gall_posy
    gall_posx = event.x
    gall_posy = event.y


def get_idnpass_direct(id_name, user, password_):
    def copy_n_close():
        pyperclip.copy(password_)
        splash.destroy()
        return None

    def tickle():
        tic = i.get()
        if tic > 1:
            i.set(tic-1)
            l_['text'] = f'{usernametype} Copied to Clipboard\nPassword will be copied\nafter {tic-1} seconds later'
            splash.update()
            splash.after(1000, tickle)
        else:
            pyperclip.copy(password_)
            splash.geometry(f'380x130')
            l_['text'] = 'Password Copied\nto clipboard'
            l_['font'] = ("segoe ui", 16)
            l_.place(x=73, y=45)
            done_ = ImageTk.PhotoImage(Image.open(icon_dir/'done.png'))
            art_label.configure(image=done_)
            art_label.image = done_
            art_label.place(x=30, y=47)
            copynow_b.place_forget()
            close_b.pack_forget()
            splash.update()
            splash.after(1500, lambda: splash.destroy())
            return None

    def dragging(event):
        x, y = event.x - gall_posx + splash.winfo_x(), event.y - gall_posy + splash.winfo_y()
        splash.geometry("+%s+%s" % (x, y))

    try:
        interval = get_sysdata('gall_interval')
    except Exception as e:
        messagebox.showerror('error', e)
        return None

    splash = Toplevel()
    splash.geometry(f'380x157+{int(width * 3.7)}+{int(height * 1)}')
    splash.attributes('-topmost', True)
    splash.overrideredirect(True)
    splash.configure(bg=softblue)
    splash.attributes('-alpha', 0.7)
    splash.resizable(width=0, height=0)
    splash.iconbitmap(applogo)
    splash.focus_set()
    splash.bind('<Button-1>', gall_last_click)
    splash.bind('<B1-Motion>', dragging)

    pyperclip.copy(user)
    usernametype = email_or_user(user)
    i = IntVar(splash, int(interval))
    f1 = Frame(splash, bg=softblue2, bd=0)
    f1.pack(side=TOP, fill=X)
    _l = Label(f1, text=f'>> {id_name}',
               bg=softblue2, fg=mint, font=('segoe ui', 13), anchor='w', padx=10)
    _l.pack(side=LEFT)
    l_ = Label(splash, text=f'{usernametype} Copied to Clipboard\nPassword will be copied\n'
                            f'after {i.get()} seconds later', bg=softblue, fg='#99aab5', font=labelfont, width=24)
    l_.place(x=85, y=37)
    splash.after(1000, tickle)
    art_image = ImageTk.PhotoImage(Image.open(icon_dir/'clock.png'))
    art_label = Label(splash, image=art_image, bg=softblue)
    art_label.place(x=17, y=48)

    copynow_b = Button(splash, text='Copy Now', command=copy_n_close,
                           font=button_font, width=22, bg='#198c8c', fg="#FFFFFF", bd=0, activebackground=deepgreen,
                           relief='ridge', cursor='dotbox', activeforeground="#00ff44")
    copynow_b.place(x=120, y=115)
    copynow_b.bind('<Enter>', lambda event: on_enter(copynow_b, bg=softblue2))
    copynow_b.bind('<Leave>', lambda event: on_leave(copynow_b, bg='#198c8c'))
    close_b = Button(f1, text='☓', font=('Segoe UI', 11), width=3, command=lambda: splash.destroy(),
                     bg=softblue2, fg="#FFFFFF", bd=0, activebackground='red',
                     activeforeground="white")
    close_b.pack(side=RIGHT)
    close_b.bind('<Enter>', lambda event: on_enter(close_b, bg=deepred))
    close_b.bind('<Leave>', lambda event: on_leave(close_b, bg=softblue2))

    splash.mainloop()
    return None


def get_fnc(event=None):
    all_id = db.get_id_name_list(conn)
    raw_id_name = idbox.get()
    if raw_id_name.isdigit():
        test = int(raw_id_name)
        if test > len(all_id) or test <= 0:
            messagebox.showerror('invalid index', 'ID index is not valid')
            return None
        id_name = all_id[test - 1]
    else:
        id_name = raw_id_name
        if id_box_checker(id_name, all_id):
            pass
        else:
            return None

    credential = db.get_credential(conn, id_name)
    _e_password = credential['password']
    try:
        password = decrypt_(_e_password)
    except cryptography.fernet.InvalidToken:
        pass
        return None

    pyperclip.copy(password)
    idbox.after(1200, lambda: idbox.delete(0, END))
    mymessage(geo='400x120', labelpos_x=100, labelpos_y=35, artwork=icon_dir/'copy.png', justify=LEFT,
              artpos_x=15, artpos_y=30, message=f">> {id_name}\nPassword Copied to Clipboard")
    return None


def get_all_fnc(event=None):
    all_id = db.get_id_name_list(conn)
    raw_id_name = idbox.get()

    if raw_id_name.isdigit():
        test = int(raw_id_name)
        if test > len(all_id) or test <= 0:
            messagebox.showerror('invalid index', 'ID index is not valid')
            return None
        id_name = all_id[test - 1]
    else:
        id_name = raw_id_name
        if id_box_checker(id_name, all_id):
            pass
        else:
            return None

    credential = db.get_credential(conn, id_name)
    _e_password = credential['password']
    _e_username = credential['username']
    try:
        username = decrypt_(_e_username)
        password = decrypt_(_e_password)
    except cryptography.fernet.InvalidToken:
        reset_security_key()
        return None
    except Exception as e_:
        messagebox.showerror('error', f'An error occurred!\nerror info: {e_}')
        return None
    idbox.delete(0, END)
    get_idnpass_direct(id_name=id_name, user=username, password_=password)
    return None


def paste2box(box):
    box.delete(0, END)
    info = str(pyperclip.paste())
    box.insert(0, info)
    return None


def generate_pass_command():
    length = get_sysdata('gp_length')
    password = pass_generator(int(length))
    pyperclip.copy(password)
    if show_info:
        mymessage(geo='400x200', labelpos_x=25, labelpos_y=20, artwork=icon_dir / 'ekey.png',
                  artpos_x=160, artpos_y=85,
                  message=f"{length} characters long password generated\nand copied to clipboard")
        return None


def setting_command():
    # \\\
    def set_time_int():
        _gall_int_ = get_sysdata('gall_interval')
        value = spin.get()
        try:
            time = int(value)
        except ValueError:
            res = messagebox.showwarning('unsupported', 'Please insert an integer number')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        except Exception as e_:
            res = messagebox.showerror('error', f'Unexpected Error!\ninfo: {e_}')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        if int(_gall_int_) == time:
            res__ = messagebox.showwarning('unchanged', f'Current value is {time} second\n'
                                                       f'Try changing the value, if you wish')
            if res__:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        if time < 1 or time > 60:
            res = messagebox.showwarning('range error', 'Valid Interval Range is between 1s to 60s')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        update_sysdata('gall_interval', time)
        res = messagebox.showinfo('updated', f'Time interval set to {time} second')
        if res:
            try:
                setting_w.focus_force()
            except TclError:
                pass
        return None

    def g_pass_length():
        value = spin2.get()
        _gp_len_ = get_sysdata('gp_length')
        try:
            length = int(value)
        except ValueError:
            res = messagebox.showwarning('unsupported', 'Please insert an integer number')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        except Exception as _exc:
            res = messagebox.showerror('error', f'Unexpected Error!\ninfo: {_exc}')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        if int(_gp_len_) == length:
            res = messagebox.showwarning('unchanged', f'Current value is {length} characters\n'
                                                       f'Try changing the value, if you wish')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        if length < 8:
            res = messagebox.showwarning('too short', 'Password length should be atleast 8 characters long')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        if length > 100:
            res = messagebox.showwarning('too long', 'Max password length is 100 characters')
            if res:
                try:
                    setting_w.focus_force()
                except TclError:
                    pass
            return None
        update_sysdata('gp_length', length)
        res = messagebox.showinfo('updated', f'From now on, generated password will be {length} characters long')
        if res:
            try:
                setting_w.focus_force()
            except TclError:
                pass
        return None

    def reset_passkey():
        if 'reset_' in wins:
            try:
                win_ = wins['reset_']
                win_.focus_force()
            except:
                pass
            return None
        setup_w = Toplevel(setting_w)
        s_width = setup_w.winfo_screenmmwidth()
        s_height = setup_w.winfo_screenheight()
        setup_w.geometry(f"490x325+{int(s_width * 1.753)}+{int(s_height * 0.43)}")
        setup_w.transient(setting_w)
        setup_w.resizable(width=0, height=0)
        setup_w.title(f'reset')
        setup_w.iconbitmap(applogo)
        setup_w.configure(bg=root_bg)
        setup_w.focus_set()

        wins['reset_'] = setup_w
        l1 = Label(setup_w, text='Reset PassKey',
                   bg=root_bg, fg=nightblue, font=("Segoe UI", 18, 'bold'))
        l1.place(x=180, y=25)
        l2 = Label(setup_w, text='Enter Current PassKey',
                   bg=root_bg, fg='#00ffec', font=labelfont_c)
        l2.place(x=40, y=85)

        # logo
        logo_image = ImageTk.PhotoImage(Image.open(icon_dir / 'passkey.png'))
        logo_image_label = Label(setup_w, image=logo_image, bg=root_bg, bd=0)
        logo_image_label.place(x=44, y=15)

        # functions

        def on_closing_():
            del wins['reset_']
            setup_w.destroy()
            setting_w.focus_force()

        def save_command(event=None):
            got_prev = prev_box.get()
            password = password_box.get()
            r_password = r_password_box.get()
            _e_sys_prev = get_sysdata('passkey')
            try:
                sys_prev = decrypt_(_e_sys_prev)
            except cryptography.fernet.InvalidToken:
                reset_security_key()
                return None
            except Exception as _exc:
                messagebox.showerror('error', f'An error occurred\nerror info: {_exc}')
                return None
            if len(got_prev) == 0 or len(password) == 0 or len(r_password) == 0:
                res = messagebox.showwarning(title='blank fields',
                                             message='All the required fields needs to be filled')
                if res:
                    try:
                        r_password_box.focus_force()
                    except TclError:
                        pass
                return None
            if got_prev != sys_prev:
                res__ = messagebox.showwarning(title="wrong passkey", message="current passkey is not valid")
                if res__:
                    try:
                        prev_box.delete(0, END)
                        prev_box.focus_force()
                    except TclError:
                        pass
                return None
            if password != r_password:
                _res_ = messagebox.showwarning(title="unmatched", message="PassKeys doesn\'t match")
                if _res_:
                    try:
                        r_password_box.delete(0, END)
                        r_password_box.focus_force()
                        r_password_box.focus_force()
                    except TclError:
                        pass
                return None
            if password == sys_prev:
                _res_ = messagebox.showwarning(title="unchanged!", message="New passkey is the current passkey.\n"
                                                                           "You can change it, if you wish")
                if _res_:
                    try:
                        password_box.delete(0, END)
                        r_password_box.delete(0, END)
                        password_box.focus_force()
                    except TclError:
                        pass
                return None

            else:
                _e_passkey = encrypt_(password)
                update_sysdata('passkey', _e_passkey)
                res = messagebox.showinfo(title='success', message='PassKey reset successfully')
                if res:
                    try:
                        on_closing_()
                    except:
                        pass
                return None

        def b_ico_(button_state, on_i, off_i):
            if button_state.get():
                button_state.set(False)
                return on_i
            else:
                button_state.set(True)
                return off_i

        def repres(box, box_state, button, button_state):
            if box_state.get():
                box.config(show='●')
                button.config(image=b_ico_(button_state, on_, off_))
                box_state.set(False)
                return
            else:
                box.config(show='')
                button.config(image=b_ico_(button_state, on_, off_))
                box_state.set(True)
                return

        # icons
        load1 = Image.open(icon_dir / 'view.png')
        on_ = ImageTk.PhotoImage(load1)
        load2 = Image.open(icon_dir / 'hide.png')
        off_ = ImageTk.PhotoImage(load2)

        # boxes
        # prev_key
        prev_box = Entry(setup_w, width=22, font=boxfont, bg="#2c7e96", fg=mint, bd=0, show='●')
        prev_box.place(x=79, y=115)
        prev_box.focus_force()
        cp_state = BooleanVar(setup_w)
        cp_state.set(False)
        hu_cp_state = BooleanVar(setup_w)
        hu_cp_state.set(False)
        hu_cp = Button(setup_w, image=b_ico_(hu_cp_state, on_, off_), bg=root_bg,
                       command=lambda: repres(prev_box, cp_state, hu_cp, hu_cp_state), bd=0, activebackground=root_bg)
        hu_cp.place(x=40, y=116)
        prev_box.bind('<Escape>', lambda event: repres(prev_box, cp_state, hu_cp, hu_cp_state))
        prev_box.configure(insertbackground=mint)
        prev_box.bind('<Return>', lambda event=None: password_box.focus_force())
        prev_box.bind("<Down>", lambda event: password_box.focus_force())
        prev_box_label = Label(setup_w, text='current', bg="#14596d", fg='white', width=9, font=button_font)
        prev_box_label.place(x=367, y=116.2)
        # new_key
        l3 = Label(setup_w, text='Enter New PassKey',
                   bg=root_bg, fg='#00ffec', font=labelfont_c)
        l3.place(x=40, y=153)
        password_box_label = Label(setup_w, text='new', bg="#006666", fg='white', width=9, font=button_font)
        password_box_label.place(x=44, y=181)
        password_box = Entry(setup_w, width=22, font=boxfont, bg="#008080", fg="#daffff", bd=0, show='●')
        password_box.place(x=130, y=180)
        password_box.configure(insertbackground=mint)
        p_state = BooleanVar(setup_w)
        p_state.set(False)
        hu_p_state = BooleanVar(setup_w)
        hu_p_state.set(False)
        hu_p = Button(setup_w, image=b_ico_(hu_p_state, on_, off_), bg=root_bg,
                      command=lambda: repres(password_box, p_state, hu_p, hu_p_state), bd=0, activebackground=root_bg)
        hu_p.place(x=430, y=181)
        password_box.bind('<Escape>', lambda event: repres(password_box, p_state, hu_p, hu_p_state))
        password_box.bind('<Return>', lambda event=None: r_password_box.focus_force())
        password_box.bind("<Down>", lambda event: r_password_box.focus_force())
        password_box.bind("<Up>", lambda event: prev_box.focus_force())
        # retype_new
        r_password_box_label = Label(setup_w, text='retype', bg="#006666", fg='white', width=9, font=button_font)
        r_password_box_label.place(x=44, y=221)
        r_password_box = Entry(setup_w, width=22, font=boxfont, bg="#008080", fg="#daffff", bd=0, show='●')
        r_password_box.place(x=130, y=220)
        r_password_box.configure(insertbackground=mint)

        r_pb_state = BooleanVar(setup_w)
        r_pb_state.set(False)
        hu_state = BooleanVar(setup_w)
        hu_state.set(False)
        hu_ = Button(setup_w, image=b_ico_(hu_state, on_, off_), bg=root_bg,
                     command=lambda: repres(box=r_password_box, box_state=r_pb_state,
                                            button=hu_, button_state=hu_state), bd=0, activebackground=root_bg)
        hu_.place(x=430, y=221)
        r_password_box.bind('<Escape>', lambda event: repres(box=r_password_box, box_state=r_pb_state,
                                                             button=hu_, button_state=hu_state))
        r_password_box.bind("<Up>", lambda event: password_box.focus_force())
        # button
        save_b = Button(setup_w, text='Reset', font=button_font, width=20, command=save_command,
                            bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg,
                            activeforeground=mint)
        save_b.place(x=140, y=272)
        save_b.bind('<Enter>', lambda event: on_enter(save_b))
        save_b.bind('<Leave>', lambda event: on_leave(save_b))
        setup_w.protocol("WM_DELETE_WINDOW", on_closing_)
        setup_w.mainloop()
        return None

    def mydevice():
        if 'device' in wins:
            try:
                win_ = wins['device']
                win_.focus_force()
            except:
                pass
            return None
        sysdata = get_sysdata()
        current_uid = sysdata['security_key']
        device_w = Toplevel(setting_w)
        width_ = device_w.winfo_screenmmwidth()
        height_ = device_w.winfo_screenheight()
        device_w.geometry(f'496x230+{int(width_ * 1.1)}+{int(height_ * 0.58)}')
        device_w.title('passito security key')
        device_w.transient(setting_w)
        device_w.configure(bg=root_bg)
        device_w.resizable(width=0, height=0)
        device_w.iconbitmap(icon_dir/'code.ico')
        device_w.focus_set()

        wins['device'] = device_w
        info_ = Label(device_w, text='Your security_key is your current encryption key. All your\n'
                                   'data is encrypted with this key. If you reinstall passito and\n'
                                   'wish to use backed up data you will need this key. This is\n'
                                   'for security purpose. Without this key you won\'t be able\n'
                                   'to access data. Please save this id in a secure place.',
                      font=('segoe ui', 13), width=47, bg=softblue, fg=mint, bd=0, justify=LEFT, pady=11)
        info_.place(x=12, y=12)
        Label(device_w, text='your security key:', font=('segoe ui', 13), bg=root_bg, fg=mint, bd=0).place(x=14, y=157)
        sk_ = Label(device_w, text=current_uid, width=42, font=('consolas', 15), bg='#006666', fg='#1fff00', bd=0)
        sk_.place(x=15, y=190)

        def saveit():
            dir_ = filedialog.asksaveasfile('w', parent=device_w, initialfile='passito__security_key',
                                            title='Save security key', filetypes=[("Text files", "*.txt")],
                                            defaultextension=".txt")
            if dir_:
                dir_.write(current_uid)
                dir_.close()
                mymessage(geo='370x120', labelpos_x=120, labelpos_y=35, bg_=softblue,
                          artwork=icon_dir / 'sf.png',
                          artpos_x=25, artpos_y=30, message=f'Saved successfully\n'
                                                            f'Always keep it private', delay=3)
            return None

        def _on_closing_():
            del wins['device']
            device_w.destroy()
            setting_w.focus_force()
            return None

        saveimg = ImageTk.PhotoImage(Image.open(icon_dir / 'u.png'))
        save_b = Button(device_w, image=saveimg, bg=root_bg, bd=0,
                        command=saveit, activebackground=root_bg)
        save_b.place(x=435, y=157)
        device_w.protocol("WM_DELETE_WINDOW", _on_closing_)
        device_w.mainloop()
    # ///

    if 'setting' in wins:
        try:
            win = wins['setting']
            win.focus_force()
        except:
            pass
        return None

    # data
    try:
        _sysfile_ = get_sysdata()
        gall_int_ = _sysfile_['gall_interval']
        gp_length_ = _sysfile_['gp_length']
    except Exception as e:
        messagebox.showerror('error', message=e)
        return None

    setting_w = Toplevel(root)
    setting_w.title('settings')
    setting_w.geometry(f'500x275+{int(width * 1.74)}+{int(height * 0.45)}')
    setting_w.configure(bg=root_bg)
    setting_w.transient(root)
    setting_w.resizable(width=0, height=0)
    setting_w.iconbitmap(applogo)
    setting_w.focus_set()

    wins['setting'] = setting_w
    # icon & Title
    s_icon = ImageTk.PhotoImage(Image.open(icon_dir / 's2.png'))
    Label(setting_w, image=s_icon, bg=root_bg).place(x=120, y=10)
    Label(setting_w, text='Quick Settings', bg=root_bg, fg=nightblue, font=("Segoe UI", 20, 'bold')).place(x=190, y=15)

    def on_closing():
        del wins['setting']
        if 'device' in wins:
            del wins['device']
        if 'reset_' in wins:
            del wins['reset_']
        if 'info' in wins:
            del wins['info']
        setting_w.destroy()

    # time interval
    fr1 = Frame(setting_w, bg=root_bg, bd=0)
    fr1.place(x=25, y=90)
    time_label = Label(fr1, text='Time interval in GetAll command', bg=splash_bg,
                       fg=mint, font=("Segoe UI", 13, 'bold'), padx=16)
    time_label.pack(side=LEFT)
    spin = Spinbox(fr1, from_=1, to=60, bg=splash_bg, fg='#aeb4ac', font=('consolas', 16), width=3, bd=2,
                   relief='flat')
    spin.pack(side=LEFT, padx=10)
    spin.configure(insertbackground=mint)
    spin.delete(0, END)
    spin.insert(0, gall_int_)
    set_button1 = Button(fr1, text='Set', font=button_font, command=set_time_int, width=7,
                         bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='ridge',
                         activeforeground=mint)
    set_button1.pack(side=LEFT)
    set_button1.bind('<Enter>', lambda event: on_enter(set_button1))
    set_button1.bind('<Leave>', lambda event: on_leave(set_button1))

    # generated pass length
    fr2 = Frame(setting_w, bg=root_bg, bd=0)
    fr2.place(x=25, y=135)
    gpl_label = Label(fr2, text='Generated password length', bg=splash_bg, width=25,
                      fg=mint, font=("Segoe UI", 13, 'bold'), padx=19)
    gpl_label.pack(side=LEFT)
    spin2 = Spinbox(fr2, from_=8, to=32, bg=splash_bg, fg='#aeb4ac', font=('consolas', 16), width=3, bd=2,
                    relief='flat')
    spin2.pack(side=LEFT, padx=10)
    spin2.configure(insertbackground=mint)
    spin2.delete(0, END)
    spin2.insert(0, gp_length_)
    set_button2 = Button(fr2, text='Set', font=button_font, width=8, command=g_pass_length,
                         bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='flat',
                         activeforeground=mint)
    set_button2.pack(side=LEFT)
    set_button2.bind('<Enter>', lambda event: on_enter(set_button2))
    set_button2.bind('<Leave>', lambda event: on_leave(set_button2))

    # Reset Passkey
    reset_button = Button(setting_w, text='Reset PassKey', font=button_font, width=49, command=reset_passkey,
                          bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='ridge',
                          activeforeground=mint)
    reset_button.place(x=25, y=185)
    reset_button.bind('<Enter>', lambda event: on_enter(reset_button))
    reset_button.bind('<Leave>', lambda event: on_leave(reset_button))

    # Logo
    s_logo = ImageTk.PhotoImage(Image.open(icon_dir / 'pg2.png'))
    s_logo_label = Label(setting_w, image=s_logo, bg=root_bg)
    s_logo_label.place(x=395, y=230)

    # Device
    code_ = ImageTk.PhotoImage(Image.open(icon_dir / 'code.png'))
    device__ = Button(setting_w, image=code_, command=mydevice,
                      bg=root_bg, fg="#1fff00", bd=0, activebackground=root_bg)
    device__.place(x=30, y=230)

    # about
    about_button_logo = ImageTk.PhotoImage(Image.open(icon_dir / 'info.png'))
    about_button = Button(setting_w, image=about_button_logo, bg=root_bg, bd=0,
                          command=lambda: info_buttton_command(setting_w), activebackground=root_bg)
    about_button.place(x=365, y=234)
    setting_w.protocol("WM_DELETE_WINDOW", on_closing)
    setting_w.mainloop()


# IDbox
idbox = AutocompleteEntry(root, width=18, font=boxfont, completevalues=all_accounts)
idbox.place(x=55, y=100)
idbox.focus_force()
idbox.bind('<Return>', get_fnc)
idbox.bind('<Shift-Return>', get_all_fnc)
idbox_icon_label = Label(root, image=id_icon, bg=root_bg)
idbox_icon_label.place(x=20, y=102)

# logo + Info
info_w_count = IntVar(root, 0)
banner_logo = ImageTk.PhotoImage(Image.open(icon_dir/'b2c.png'))
banner_button = Button(root, image=banner_logo, bg=root_bg, bd=0,
                       command=lambda: info_buttton_command(root), activebackground=root_bg)
banner_button.place(x=5, y=15)

# display_art
arts_list = ("a1.png", "owl.png", "cl.png", 'p2.png', "r.png", 'pda.png')
art = random.choice(arts_list)
artfile = icon_dir/art
icon = ImageTk.PhotoImage(Image.open(artfile))   # icon_dimension: 128x128
iconlabel = Label(root, image=icon, bg=root_bg)
iconlabel.place(x=520, y=235)


# IDbox getbutton
getButton = Button(root, text='Get Pass',command=get_fnc, font=button_font, width=9,
                   bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg,
                   relief='ridge', cursor='dotbox', activeforeground=mint)
getButton.place(x=104, y=135)
getAllButton = Button(root, text='Get All', command=get_all_fnc, width=10, font=button_font, bg=button_bg,
                      fg="#FFFFFF", bd=0, activebackground=softblue2, relief='ridge',
                      cursor='dotbox', activeforeground='#ffffff')
getAllButton.place(x=199, y=135)
getButton.bind('<Enter>', lambda event: on_enter(getButton))
getButton.bind('<Leave>', lambda event: on_leave(getButton))
getAllButton.bind('<Enter>', lambda event: on_enter(getAllButton))
getAllButton.bind('<Leave>', lambda event: on_leave(getAllButton))

# Pass Generator
gen_button_logo = ImageTk.PhotoImage(Image.open(icon_dir/'gen_pass.png'))
gen_button = Button(root, image=gen_button_logo, bg=root_bg, command=generate_pass_command,
                    bd=0, activebackground=root_bg, cursor='exchange')
gen_button.place(x=116, y=225)
gen_button_label = Label(root, text="Generate Password", bg=root_bg, fg="#0799c2", font=labelfont)
gen_button_label.place(x=95, y=305)

# setting_button
setting_button_logo = ImageTk.PhotoImage(Image.open(icon_dir/'set.png'))
setting_button = Button(root, image=setting_button_logo, bg=root_bg, bd=0,
                        command=setting_command,activebackground=root_bg)
setting_button.place(x=657, y=10)


def refresh_accounts():
    all_accounts = db.get_id_name_list(conn)
    idbox.configure(completevalues=all_accounts)
    idbox.update()
    
# Console_Buttons
def focus_empty_box(id_box, user_box, password_box, re_pass_box, update_d=False, check=None):
    id_len = len(id_box.get())
    user_len = len(user_box.get())
    pass_len = len(password_box.get())
    re_pass_len = len(re_pass_box.get())

    if id_len == 0 and user_len == 0 and pass_len == 0 and re_pass_len == 0:
        messagebox.showwarning('empty', 'All the fields needs to be filled')
        try:
            id_box.focus_force()
        except TclError:
            pass
        return None
    if id_len == 0:
        if update_d:
            messagebox.showwarning('empty', 'Enter ID Name or Index')
        else:
            messagebox.showwarning('empty', 'Enter the ID Name to be saved')
        try:
            id_box.focus_force()
        except TclError:
            pass
        return None
    if user_len == 0:
        if update_d:
            if not check:
                messagebox.showwarning('empty', 'Enter the updated Username or Email of the ID')
                user_box.focus_force()
                return None
            else:
                pass
        else:
            messagebox.showwarning('empty', 'Enter the username or email of the ID')
            try:
                user_box.focus_force()
                return None
            except TclError:
                return None
    if pass_len == 0:
        messagebox.showwarning('empty', 'Enter the password of the ID')
        try:
            password_box.focus_force()
        except TclError:
            pass
        return None
    if re_pass_len == 0:
        messagebox.showwarning('empty', 'Retype the password')
        try:
            re_pass_box.focus_force()
        except TclError:
            pass
        return None


def add_command(event=None):
    if 'add' in wins:
        try:
            win = wins['add']
            win.focus_force()
        except:
            pass
        return None

    addwindow = Toplevel(root)
    addwindow.title('add')
    addwindow.geometry(f'500x270+{int(width*1.1)}+{int(height*0.65)}')
    addwindow.configure(bg=root_bg)
    addwindow.transient(root)
    addwindow.resizable(width=0, height=0)
    addwindow.iconbitmap(applogo)
    addwindow.focus_set()

    addwindow.bind('<Left>', lambda evnt: idbox.focus_force())
    addwindow.bind('<Right>', lambda evnt: idbox.focus_force())
    addwindow.bind("<Shift-Escape>", lambda ev: on_closing(force=False))
    label_ = Label(addwindow, text='Add New Credentials', bg=softblue, fg=mint, font=("Seoge UI", 16),
                   width=42)
    label_.place(x=0, y=0)

    def on_closing(force=False):
        def finish():
            del wins['add']
            if 'add_help' in wins:
                del wins['add_help']
            addwindow.destroy()

        if force:
            finish()
            return None

        id_name = id_name_box.get()
        email = emailbox.get()
        password = passwordbox.get()
        r_password = r_passwordbox.get()

        if len(id_name) != 0 or len(email) != 0 or len(password) != 0 or len(r_password) != 0:
            res__ = messagebox.askyesno('add', 'Are you sure to close?')
            if res__:
                pass
            else:
                try:
                    id_name_box.focus_force()
                except Exception as exc__:
                    messagebox.showwarning('error', f'An error occurred\ninfo: {exc__}')
                return None
        finish()

    def save_new(event_=None):
        all_id_ = db.get_id_name_list(conn)
        id_name = id_name_box.get()
        email = emailbox.get()
        password = passwordbox.get()
        r_password = r_passwordbox.get()
        if len(id_name) == 0 or len(email) == 0 or len(password) == 0 or len(r_password) == 0:
            focus_empty_box(id_name_box, emailbox, passwordbox, r_passwordbox)
            return None
        if id_name.isdigit():
            messagebox.showwarning('invalid name', 'ID name cannot be an integer!')
            id_name_box.focus_force()
            return None
        if id_name in all_id_:
            res = messagebox.showwarning(title=f'{id_name}',
                                   message=f"{id_name} is already in the database\n"
                                           f"click 'Update' to modify data of this profile")
            if res:
                try:
                    id_name_box.focus_force()
                except TclError:
                    pass
            return None
        if password != r_password:
            res = messagebox.showwarning(title="unmatched", message='Passwords doesn\'t match')
            if res:
                try:
                    r_passwordbox.focus_force()
                except TclError:
                    pass
            return None
        else:
            _e_email = encrypt_(email)
            _e_password = encrypt_(password)
            db.add_account(conn, id_name=id_name, usernaname=_e_email, password=_e_password)
            refresh_accounts()
            add_msgbox(message=f"Credentials Saved Successfully")
        return None

    def help_add():
        if 'add_help' in wins:
            try:
                win_ = wins['add_help']
                win_.focus_force()
            except:
                pass
            return None
        add_h_w = Toplevel(addwindow)
        add_h_w.title("add")
        add_h_w.geometry(f'520x320+{int(width * 1.75)}+{int(height * 0.44)}')
        add_h_w.configure(bg=splash_bg)
        add_h_w.transient(addwindow)
        add_h_w.resizable(width=0, height=0)
        add_h_w.iconbitmap(applogo)
        add_h_w.focus_set()

        wins['add_help'] = add_h_w

        _label_ = Label(add_h_w, text="User Guide (Add)", bg=softblue, fg=mint, font=("Seoge UI", 14), width=47)
        _label_.place(x=0, y=0)

        def on_closing_a_h():
            del wins['add_help']
            add_h_w.destroy()
            return None

        # ID
        id_name_label = Label(add_h_w, image=id_icon, bg=splash_bg)
        id_name_label.place(x=18, y=45)
        label_id = Label(add_h_w, text="ID Name", bg=softblue2, fg=mint, font=('consolas', 15), width=8)
        label_id.place(x=55, y=45)
        id_info_label = Label(add_h_w, text="Enter a name for the ID (example: stackoverflow)", bg=splash_bg,
                              fg="#99e0f4", font=('roboto', 12))
        id_info_label.place(x=155, y=47)

        # User/Mail
        id_name_label = Label(add_h_w, image=user_icon, bg=splash_bg)
        id_name_label.place(x=18, y=119)
        label_id = Label(add_h_w, text="Email\nor\nUsername", bg=softblue2, fg=mint, font=('consolas', 15), width=8)
        label_id.place(x=55, y=95)
        id_info_label = Label(add_h_w, text="Enter the email or username linked with the ID\n"
                                            "(example1: mymail@gmail.com)\n"
                                            "(example2: MyUserName)", bg=splash_bg, fg="#99e0f4", justify=LEFT,
                              font=('roboto', 12))
        id_info_label.place(x=155, y=100)

        # Password
        pass_label_ = Label(add_h_w, image=pass_icon, bg=splash_bg)
        pass_label_.place(x=18, y=190)
        label_pass = Label(add_h_w, text="Password", bg=softblue2, fg=mint, font=('consolas', 15), width=8)
        label_pass.place(x=55, y=190)
        pass_info_label = Label(add_h_w, text="Enter the password of the ID", bg=splash_bg, fg="#99e0f4",
                                font=('roboto', 12))
        pass_info_label.place(x=155, y=192)

        # retype Password
        r_pass_label_ = Label(add_h_w, image=retype_icon, bg=splash_bg)
        r_pass_label_.place(x=18, y=235)
        label_r_pass = Label(add_h_w, text="Retype", bg=softblue2, fg=mint, font=('consolas', 15), width=8)
        label_r_pass.place(x=55, y=235)
        r_pass_info_label = Label(add_h_w, text="Retype the password", bg=splash_bg, fg="#99e0f4",
                                  font=('roboto', 12))
        r_pass_info_label.place(x=155, y=237)

        # Paste_button
        paste_button1_ = Label(add_h_w, text='ᐁ', font=("segoe ui", 14, "bold"), width=3,
                              bg=softblue2, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                              activeforeground="#0799c2")
        paste_button1_.place(x=180, y=280)
        pb_info_label = Label(add_h_w, text="the Paste Button", bg=splash_bg, fg=mint,
                              font=('roboto', 12))
        pb_info_label.place(x=220, y=280)

        add_h_w.protocol("WM_DELETE_WINDOW", on_closing_a_h)
        add_h_w.mainloop()
        return None

    def paste_on_enter(button_obj):
        button_obj['background'] = '#45a5c1'
        button_obj['foreground'] = softblue

    def paste_on_leave(button_obj, bg=softblue2):
        button_obj['background'] = bg
        button_obj['foreground'] = '#ffffff'

    def b_ico_(button_state, on_i, off_i):
        if button_state.get():
            button_state.set(False)
            return on_i
        else:
            button_state.set(True)
            return off_i

    def repres(box, box_state, button, button_state):
        if box_state.get():
            box.config(show='●')
            button.config(image=b_ico_(button_state, on_, off_))
            box_state.set(False)
            return
        else:
            box.config(show='')
            button.config(image=b_ico_(button_state, on_, off_))
            box_state.set(True)
            return

    def add_msgbox(message):
        splash = Toplevel()
        splash.geometry(f'400x120+{int(width*1.9)}+{int(height*0.5)}')
        splash.attributes('-topmost', True)
        splash.overrideredirect(True)
        splash.configure(bg=splash_bg)
        splash.attributes('-alpha', 0.95)
        splash.resizable(width=0, height=0)
        splash.iconbitmap(applogo)
        splash.focus_set()

        def close_parent_msg():
            on_closing(force=True)
            splash.destroy()
            return None

        splash.after(1200, close_parent_msg)

        Label(splash, text=message, bg=splash_bg, fg=splash_txt_color, font=labelfont).place(x=100, y=48)
        pass_gen_w_art_image = ImageTk.PhotoImage(Image.open(icon_dir/'s.png'))
        pass_gen_w_art_label = Label(splash, image=pass_gen_w_art_image, bg=splash_bg)
        pass_gen_w_art_label.place(x=20, y=30)
        splash.mainloop()

    # icons
    load1 = Image.open(icon_dir / 'view.png')
    on_ = ImageTk.PhotoImage(load1)
    load2 = Image.open(icon_dir / 'hide.png')
    off_ = ImageTk.PhotoImage(load2)

    # retype_passwordbox
    r_password_box_label = Label(addwindow, image=retype_icon, bg=root_bg,)
    r_password_box_label.place(x=25, y=171)
    r_passwordbox = Entry(addwindow, width=25, font=boxfont, bg=softblue, fg=mint, bd=0, show='●')
    r_passwordbox.place(x=70, y=170)
    r_passwordbox.bind("<Return>", save_new)
    r_passwordbox.bind("<Up>", lambda event: id_name_box.focus_force())
    r_passwordbox.configure(insertbackground=mint)

    r_pb_state = BooleanVar(addwindow)
    r_pb_state.set(False)
    hu_state = BooleanVar(addwindow)
    hu_state.set(False)
    hu_ = Button(addwindow, image=b_ico_(hu_state, on_, off_), bg=root_bg,
                 command=lambda: repres(r_passwordbox, r_pb_state, hu_, hu_state),bd=0, activebackground=root_bg)
    hu_.place(x=440, y=172)
    r_passwordbox.bind('<Escape>', lambda event: repres(r_passwordbox, r_pb_state, hu_, hu_state))

    paste_button3 = Button(addwindow, text='ᐁ', font=button_font, width=3, command=lambda: paste2box(r_passwordbox),
                           bg=softblue2, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                           activeforeground="#0799c2")
    paste_button3.place(x=397, y=169.3)
    paste_button3.bind('<Enter>', lambda event: paste_on_enter(paste_button3))
    paste_button3.bind('<Leave>', lambda event: paste_on_leave(paste_button3))
    # passwordbox
    password_box_label = Label(addwindow, image=pass_icon, bg=root_bg)
    password_box_label.place(x=25, y=131)
    passwordbox = Entry(addwindow, width=25, font=boxfont, bg=softblue, fg=mint, bd=0, show='●')
    passwordbox.place(x=70, y=130)
    passwordbox.configure(insertbackground=mint)
    p_state = BooleanVar(addwindow)
    p_state.set(False)
    hu_p_state = BooleanVar(addwindow)
    hu_p_state.set(False)
    hu_p = Button(addwindow, image=b_ico_(hu_p_state, on_, off_), bg=root_bg,
                  command=lambda: repres(passwordbox, p_state, hu_p, hu_p_state), bd=0, activebackground=root_bg)
    hu_p.place(x=440, y=131)
    passwordbox.bind('<Escape>', lambda event: repres(passwordbox, p_state, hu_p, hu_p_state))
    passwordbox.bind('<Return>', lambda event=None: r_passwordbox.focus_force())
    passwordbox.bind("<Up>", lambda event: emailbox.focus_force())
    passwordbox.bind("<Down>", lambda event: r_passwordbox.focus_force())
    paste_button2 = Button(addwindow, text='ᐁ', font=button_font, width=3, command=lambda: paste2box(passwordbox),
                           bg=softblue2, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                           activeforeground="#0799c2")
    paste_button2.place(x=397, y=129.3)
    paste_button2.bind('<Enter>', lambda event: paste_on_enter(paste_button2))
    paste_button2.bind('<Leave>', lambda event: paste_on_leave(paste_button2))

    # Emailbox
    emailbox_label = Label(addwindow, image=user_icon, bg=root_bg)
    emailbox_label.place(x=25, y=91)
    emailbox = Entry(addwindow, width=29, font=boxfont, bg=softblue2, fg="#daffff", bd=0)
    emailbox.place(x=70, y=90)
    emailbox.configure(insertbackground=mint)
    emailbox.bind('<Return>', lambda event=None: passwordbox.focus_force())
    emailbox.bind("<Up>", lambda event: id_name_box.focus_force())
    emailbox.bind("<Down>", lambda event: passwordbox.focus_force())
    paste_button1 = Button(addwindow, text='ᐁ', command=lambda: paste2box(emailbox), font=button_font, width=3,
                           bg=softblue, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                           activeforeground="#0799c2")
    paste_button1.place(x=443, y=89.3)
    paste_button1.bind('<Enter>', lambda event: paste_on_enter(paste_button1))
    paste_button1.bind('<Leave>', lambda event: paste_on_leave(paste_button1, bg=softblue))

    # IDname box
    idbox_label = Label(addwindow, image=id_icon, bg=root_bg)
    idbox_label.place(x=25, y=51)
    id_name_box = Entry(addwindow, width=25, font=boxfont, bg=softblue2, fg="#daffff", bd=0)
    id_name_box.place(x=70, y=50)
    id_name_box.focus_force()
    wins['add'] = id_name_box
    id_name_box.configure(insertbackground=mint)
    id_name_box.bind('<Return>', lambda ev=None: emailbox.focus_force())
    id_name_box.bind("<Down>", lambda ev: emailbox.focus_force())

    # Buttons
    # help_button
    help_button_logo = ImageTk.PhotoImage(Image.open(icon_dir / 'w2.png'))
    help_button = Button(addwindow, image=help_button_logo, bg=softblue, bd=0,
                         command=help_add, activebackground=softblue)
    help_button.place(x=465, y=5)
    # savebutton
    save_b = Button(addwindow, text='Save',command=save_new, font=button_font, width=20,
                        bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='ridge',
                        cursor='dotbox', activeforeground=mint)
    save_b.place(x=155, y=220)
    save_b.bind('<Enter>', lambda event: on_enter(save_b))
    save_b.bind('<Leave>', lambda event: on_leave(save_b))

    addwindow.protocol("WM_DELETE_WINDOW", on_closing)
    addwindow.mainloop()
    return None


def update_command(event=None):
    if 'update' in wins:
        try:
            win = wins['update']
            win.focus_force()
        except:
            pass
        return None

    update_window = Toplevel(root)
    update_window.title('update')
    update_window.geometry(f'500x300+{int(width*1.15)}+{int(height*0.65)}')
    update_window.configure(bg=root_bg)
    update_window.transient(root)
    update_window.resizable(width=0, height=0)
    update_window.iconbitmap(applogo)
    update_window.focus_set()

    update_window.bind('<Up>', lambda evnt: idbox.focus_force())
    update_window.bind('<Down>', lambda evnt: idbox.focus_force())
    update_window.bind("<Shift-Escape>", lambda ev: on_closing(force=False))
    wins['update'] = update_window
    tlabel = Label(update_window, text='Update Existing Credentials', bg=softblue, fg=mint, font=("Seoge UI", 16),
                   width=42)
    tlabel.place(x=0, y=0)

    cb1 = Label(update_window, text='leave empty to keep previous email/username',bg=root_bg, fg='gray')
    cb1.place(x=160, y=120)

    def on_closing(force=False):
        def finish():
            try:
                del wins['update']
            except KeyError:
                pass
            if 'update_help' in wins:
                del wins['update_help']
            update_window.destroy()
            return None

        if force:
            finish()
            return None

        id_name = id_box.get()
        email = emailbox.get()
        password = passwordbox.get()
        r_password = r_passwordbox.get()

        if len(id_name) != 0 or len(email) != 0 or len(password) != 0 or len(r_password) != 0:
            res__ = messagebox.askyesno('update', 'Are you sure to close?')
            if res__:
                pass
            else:
                try:
                    id_box.focus_force()
                except Exception as exc__:
                    messagebox.showwarning('error', f'An error occurred\ninfo: {exc__}')
                return None
        finish()
    
    def idbox_return(event=None):
        all_id = db.get_id_name_list(conn)
        raw_id_name = id_box.get()
        if raw_id_name.isdigit():
            test = int(raw_id_name)
            if test > len(all_id) or test <= 0:
                messagebox.showerror('invalid index', 'ID index is not valid')
                id_box.focus_force()
                return None
            id_name = all_id[test - 1]
            id_box.delete(0, END)
            id_box.insert(0, id_name)
        emailbox.focus_force()

    def update(event=None):
        all_id = db.get_id_name_list(conn)
        raw_id_name = id_box.get()
        if raw_id_name.isdigit():
            test = int(raw_id_name)
            if test > len(all_id) or test <= 0:
                messagebox.showerror('invalid index', 'ID index is not valid')
                id_box.focus_force()
                return None
            id_name = all_id[test - 1]

        else:
            id_name = raw_id_name

        email = emailbox.get()
        password = passwordbox.get()
        r_password = r_passwordbox.get()

        if len(id_name) == 0 or len(password) == 0 or len(r_password) == 0:
            focus_empty_box(id_box, emailbox, passwordbox, r_passwordbox, update_d=True)
            return None

        elif id_name not in all_id:
            res = messagebox.showerror(title=f'{id_name} not found', message='Non-existing id cannot be updated!')
            if res:
                try:
                    id_box.focus_force()
                except TclError:
                    pass
            return None
        if password != r_password:
            res = messagebox.showwarning(title="unmatched", message='Passwords doesn\'t match')
            if res:
                try:
                    r_passwordbox.focus_force()
                except TclError:
                    pass
            return None
        if len(email) < 1:
            credential = db.get_credential(conn, id_name)
            _e_prev_mail = credential['username']
            _e_password = encrypt_(password)
            db.update_credential_by_name(conn, id_name, _e_prev_mail, _e_password)
            refresh_accounts()
            update_msgbox("Password Updated Successfully", icon_=icon_dir/'info2.png', geo='420x120')
            return None
        else:
            _e_user = encrypt_(email)
            _e_pass = encrypt_(password)
            db.update_credential_by_name(conn, id_name, _e_user, _e_pass)
            refresh_accounts()
            update_msgbox("Data Updated Successfully", icon_=icon_dir/'refresh.png', geo='390x120')
            return None

    def update_help():
        if 'update_help' in wins:
            try:
                win_ = wins['update_help']
                win_.focus_force()
            except:
                pass
            return None

        update_h_w = Toplevel(update_window)
        update_h_w.title('update')
        update_h_w.geometry(f'600x300+{int(width * 1.64)}+{int(height * 0.45)}')
        update_h_w.configure(bg=splash_bg)
        update_h_w.transient(update_window)
        update_h_w.resizable(width=0, height=0)
        update_h_w.iconbitmap(applogo)
        update_h_w.focus_set()

        wins['update_help'] = update_h_w

        label_ = Label(update_h_w, text="User Guide (Update)", bg=softblue, fg=mint, font=("Seoge UI", 14), width=54)
        label_.place(x=0, y=0)

        def on_closing_u_h():
            del wins['update_help']
            update_h_w.destroy()
            return None

        # ID
        id_name_label = Label(update_h_w, image=id_icon, bg=splash_bg)
        id_name_label.place(x=18, y=45)
        label_id = Label(update_h_w, text="ID Name", bg=softblue2, fg=mint, font=('consolas', 15), width=9)
        label_id.place(x=55, y=45)
        id_info_label = Label(update_h_w, text="Enter the name of a previously saved ID (example: gmail)", bg=splash_bg,
                              fg="#99e0f4", font=('roboto', 12))
        id_info_label.place(x=165, y=47)

        # User/Mail
        username_label = Label(update_h_w, image=user_icon, bg=splash_bg)
        username_label.place(x=18, y=119)
        label_user = Label(update_h_w, text="Email\nor\nUsername", bg=softblue2, fg=mint, font=('consolas', 15),
                           width=9)
        label_user.place(x=55, y=96)
        user_info_label = Label(update_h_w, text="Leave this field empty if the email/username is unchanged\n"
                                                 "or enter the new email or username linked with the ID",
                                bg=splash_bg, fg="#99e0f4", justify=LEFT, font=('roboto', 12))
        user_info_label.place(x=165, y=90)
        user_info_label3 = Label(update_h_w, text="(example1: mynewmail@gmail.com)\n"
                                                  "(example2: MyNewUserName)", bg=splash_bg,
                                 fg="#99e0f4", justify=LEFT, font=('roboto', 12))
        user_info_label3.place(x=165, y=130)

        # Password
        pass_label_ = Label(update_h_w, image=pass_icon, bg=splash_bg)
        pass_label_.place(x=18, y=200)
        label_pass = Label(update_h_w, text="Password", bg=softblue2, fg=mint, font=('consolas', 15), width=9)
        label_pass.place(x=55, y=200)
        pass_info_label = Label(update_h_w, text="Enter the new password of the ID \n"
                                                 "(enter current password if unchanged)", bg=splash_bg, fg="#99e0f4",
                                font=('roboto', 12), justify=LEFT)
        pass_info_label.place(x=165, y=193)

        # retype Password
        r_pass_label_ = Label(update_h_w, image=retype_icon, bg=splash_bg)
        r_pass_label_.place(x=18, y=242)
        label_r_pass = Label(update_h_w, text="Retype", bg=softblue2, fg=mint, font=('consolas', 15), width=9)
        label_r_pass.place(x=55, y=242)
        r_pass_info_label = Label(update_h_w, text="Retype the password", bg=splash_bg, fg="#99e0f4",
                                  font=('roboto', 12))
        r_pass_info_label.place(x=165, y=244)

        update_h_w.protocol("WM_DELETE_WINDOW", on_closing_u_h)
        update_h_w.mainloop()

    def paste_on_enter(button_obj):
        button_obj['background'] = '#45a5c1'
        button_obj['foreground'] = softblue

    def paste_on_leave(button_obj, bg=softblue2):
        button_obj['background'] = bg
        button_obj['foreground'] = '#ffffff'

    def b_ico_(button_state, on_i, off_i):
        if button_state.get():
            button_state.set(False)
            return on_i
        else:
            button_state.set(True)
            return off_i

    def repres(box, box_state, button, button_state):
        if box_state.get():
            box.config(show='●')
            button.config(image=b_ico_(button_state, on_, off_))
            box_state.set(False)
            return
        else:
            box.config(show='')
            button.config(image=b_ico_(button_state, on_, off_))
            box_state.set(True)
            return

    def update_msgbox(message, icon_, geo='400x120'):
        splash = Toplevel()
        splash.geometry(f'{geo}+{int(width*1.9)}+{int(height*0.5)}')
        splash.attributes('-topmost', True)
        splash.overrideredirect(True)
        splash.configure(bg=splash_bg)
        splash.attributes('-alpha', 0.95)
        splash.resizable(width=0, height=0)
        splash.iconbitmap(applogo)
        splash.focus_set()

        def close_parent_msg():
            on_closing(force=True)
            splash.destroy()
            return None

        splash.after(1000, close_parent_msg)

        Label(splash, text=message, bg=splash_bg, fg=splash_txt_color, font=labelfont).place(x=100, y=47)
        pass_gen_w_art_image = ImageTk.PhotoImage(Image.open(icon_))
        pass_gen_w_art_label = Label(splash, image=pass_gen_w_art_image, bg=splash_bg)
        pass_gen_w_art_label.place(x=20, y=30)
        splash.mainloop()
        return None


    # icons
    load1 = Image.open(icon_dir / 'view.png')
    on_ = ImageTk.PhotoImage(load1)
    load2 = Image.open(icon_dir / 'hide.png')
    off_ = ImageTk.PhotoImage(load2)

    # retype_passwordbox
    r_password_box_label = Label(update_window, image=retype_icon, bg=root_bg)
    r_password_box_label.place(x=25, y=196)
    r_passwordbox = Entry(update_window, width=25, font=boxfont, bg=softblue, fg=mint, bd=0, show='●')
    r_passwordbox.place(x=70, y=195)
    r_passwordbox.configure(insertbackground=mint)
    r_passwordbox.bind("<Return>", update)
    r_passwordbox.bind("<Up>", lambda event: passwordbox.focus_force())
    r_passwordbox.bind("<Shift-Escape>", lambda ev: on_closing(force=False))

    r_pb_state = BooleanVar(update_window)
    r_pb_state.set(False)
    hu_state = BooleanVar(update_window)
    hu_state.set(False)
    hu_ = Button(update_window, image=b_ico_(hu_state, on_, off_), bg=root_bg,
                 command=lambda: repres(r_passwordbox, r_pb_state, hu_, hu_state), bd=0, activebackground=root_bg)
    hu_.place(x=440, y=196)
    r_passwordbox.bind('<Escape>', lambda event: repres(r_passwordbox, r_pb_state, hu_, hu_state))

    paste_button3 = Button(update_window, text='ᐁ', font=button_font, width=3, command=lambda: paste2box(r_passwordbox),
                           bg=softblue2, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                           activeforeground="#0799c2")
    paste_button3.place(x=397, y=194.3)
    paste_button3.bind('<Enter>', lambda event: paste_on_enter(paste_button3))
    paste_button3.bind('<Leave>', lambda event: paste_on_leave(paste_button3))

    # passwordbox
    password_box_label = Label(update_window, image=pass_icon, bg=root_bg)
    password_box_label.place(x=25, y=156)
    passwordbox = Entry(update_window, width=25, font=boxfont, bg=softblue, fg=mint, bd=0, show='●')
    passwordbox.place(x=70, y=155)
    passwordbox.configure(insertbackground=mint)
    passwordbox.bind('<Return>', lambda event=None: r_passwordbox.focus_force())
    passwordbox.bind("<Up>", lambda event: emailbox.focus_force())
    passwordbox.bind("<Down>", lambda event: r_passwordbox.focus_force())
    passwordbox.bind("<Shift-Escape>", lambda ev: on_closing(force=False))

    p_state = BooleanVar(update_window)
    p_state.set(False)
    hu_p_state = BooleanVar(update_window)
    hu_p_state.set(False)
    hu_p = Button(update_window, image=b_ico_(hu_p_state, on_, off_), bg=root_bg,
                  command=lambda: repres(passwordbox, p_state, hu_p, hu_p_state), bd=0, activebackground=root_bg)
    hu_p.place(x=440, y=156)
    passwordbox.bind('<Escape>', lambda event: repres(passwordbox, p_state, hu_p, hu_p_state))

    paste_button2 = Button(update_window, text='ᐁ', font=button_font, width=3, command=lambda: paste2box(passwordbox),
                           bg=softblue2, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                           activeforeground="#0799c2")
    paste_button2.place(x=397, y=154.3)
    paste_button2.bind('<Enter>', lambda event: paste_on_enter(paste_button2))
    paste_button2.bind('<Leave>', lambda event: paste_on_leave(paste_button2))

    # Emailbox
    emailbox_label = Label(update_window, image=user_icon, bg=root_bg)
    emailbox_label.place(x=25, y=91)
    emailbox = Entry(update_window, width=29, font=boxfont, bg=softblue2, fg="#daffff", bd=0)
    emailbox.place(x=70, y=90)
    emailbox.configure(insertbackground=mint)
    emailbox.bind('<Return>', lambda event=None: passwordbox.focus_force())
    emailbox.bind("<Up>", lambda event: id_box.focus_force())
    emailbox.bind("<Down>", lambda event: passwordbox.focus_force())
    emailbox.bind("<Shift-Escape>", lambda ev: on_closing(force=False))
    paste_button1 = Button(update_window, text='ᐁ', command=lambda: paste2box(emailbox), font=button_font, width=3,
                           bg=softblue, fg="#FFFFFF", bd=0, activebackground='cyan', relief='ridge',
                           activeforeground="#0799c2")
    paste_button1.place(x=443, y=89.3)
    paste_button1.bind('<Enter>', lambda event: paste_on_enter(paste_button1))
    paste_button1.bind('<Leave>', lambda event: paste_on_leave(paste_button1, bg=softblue))

    # IDname box
    idbox_label = Label(update_window, image=id_icon, bg=root_bg)
    idbox_label.place(x=25, y=51)
    id_box = Entry(update_window, width=20, font=boxfont, bg=softblue2, fg="#daffff", bd=0)
    id_box.place(x=70, y=50)
    wins['update'] = id_box
    id_box.configure(insertbackground=mint)
    id_box.bind('<Return>', lambda event=None: idbox_return())
    id_box.bind("<Down>", lambda ev: emailbox.focus_force())
    id_box.focus_force()

    # Buttons
    # help_button
    help_button_logo = ImageTk.PhotoImage(Image.open(icon_dir / 'w2.png'))
    help_button = Button(update_window, image=help_button_logo, bg=softblue, bd=0,
                         command=update_help, activebackground=softblue)
    help_button.place(x=465, y=5)
    update_b = Button(update_window, text='Update', font=button_font, width=20, command=update,
                          bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg, cursor='dotbox',
                          activeforeground=mint)
    update_b.place(x=155, y=250)
    update_b.bind('<Enter>', lambda event: on_enter(update_b))
    update_b.bind('<Leave>', lambda event: on_leave(update_b))

    update_window.protocol("WM_DELETE_WINDOW", on_closing)
    update_window.mainloop()
    return None


def delete_command(event=None):
    if 'del_' in wins:
        try:
            win = wins['del_']
            win.focus_force()
        except:
            pass
        return None
    delbg = '#004953'
    delwindow = Toplevel(root)
    delwindow.geometry(f'400x150+{int(width * 1.3)}+{int(height * 0.68)}')
    delwindow.title('delete')
    delwindow.configure(bg=delbg)
    delwindow.transient(root)
    delwindow.resizable(width=0, height=0)
    delwindow.iconbitmap(applogo)
    delwindow.focus_set()

    delwindow.bind('<Up>', lambda evnt: idbox.focus_force())
    delwindow.bind('<Down>', lambda evnt: idbox.focus_force())
    wins['del_'] = delwindow
    l_ = Label(delwindow, text='Delete Credential', bg=softblue, width=37, fg=mint, font=("Seoge UI", 14))
    l_.place(x=0, y=0)

    def on_closing():
        del wins['del_']
        delwindow.destroy()

    def remove(event=None):
        all_id = db.get_id_name_list(conn)
        raw_id_name = id_box.get()
        if raw_id_name.isdigit():
            test = int(raw_id_name)
            if test > len(all_id) or test <= 0:
                messagebox.showerror('invalid index', 'ID index is not valid')
                try:
                    id_box.focus_force()
                except TclError:
                    pass
                return None
            id_name = all_id[test - 1]
        else:
            id_name = raw_id_name

        if len(id_name) == 0:
            res = messagebox.showwarning(title='empty', message='Enter an ID name or index')
            if res:
                id_box.focus_force()
                return None
        if id_name not in all_id:
            messagebox.showerror('not found', 'Such ID doesn\'t exists')
            id_box.focus_force()
            return None
        else:
            res = messagebox.askyesno(title=f"delete '{id_name}'", message=f'Are you sure to delete {id_name}?')
            if res:
                db.delete_by_name(conn, id_name)
                refresh_accounts()
                id_box.delete(0, END)
                mymessage(geo='400x120', labelpos_x=100, labelpos_y=48, artwork=icon_dir / 'del2.png',
                          artpos_x=20, artpos_y=30, message=f"Credentials Deleted Successfully", to_be_focused=id_box)
            else:
                try:
                    id_box.focus_force()
                except:
                    pass
        return None

    # IDname box
    id_name_l = Label(delwindow, image=id_icon, bg=delbg)
    id_name_l.place(x=20, y=56)
    id_box = Entry(delwindow, width=23, font=boxfont, bg="#008080", fg=mint, bd=0)
    id_box.place(x=65, y=55)
    wins['del_'] = id_box
    id_box.configure(insertbackground=mint)
    id_box.focus_force()
    id_box.bind("<Return>", remove)
    id_box.bind("<Shift-Escape>", lambda ev: on_closing())

    del_button = Button(delwindow, text='Delete', font=button_font, width=15, command=remove,
                        bg='#0086ad', fg="#FFFFFF", bd=0, activebackground='red',
                        relief='ridge', activeforeground="#FFFFFF")
    del_button.place(x=135, y=105)
    del_button.bind('<Enter>', lambda event: on_enter(del_button, bg='#E41234'))
    del_button.bind('<Leave>', lambda event: on_leave(del_button, bg='#0086ad'))

    delwindow.protocol("WM_DELETE_WINDOW", on_closing)
    delwindow.mainloop()


def backup_command():
    if 'br' in wins:
        try:
            win = wins['br']
            win.focus_force()
        except:
            pass
        return None
    all_id = db.get_id_name_list(conn)
    br_window = Toplevel(root)
    br_window.geometry(f'490x280+{int(width * 1.05)}+{int(height * 0.65)}')
    br_window.configure(bg=root_bg)
    br_window.transient(root)
    br_window.resizable(width=0, height=0)
    br_window.iconbitmap(applogo)
    br_window.title('b&r')
    br_window.focus_set()

    wins['br'] = br_window
    label_ = Label(br_window, text='Backup and Restore Data', bg=softblue, fg=mint, font=("Seoge UI", 16),
                   width=41)
    label_.place(x=0, y=0)

    def on_closing():
        del wins['br']
        br_window.destroy()

    def backup_path_command():
        backup_path = filedialog.askdirectory(title='choose destination')
        pathbox.delete(0, END)
        pathbox.insert(0, string=backup_path)
        if backup_path:
            try:
                br_window.focus_force()
            except TclError:
                pass
        return None

    def backup_now_command():
        backup_path = pathbox.get()
        if len(all_id) == 0:
            mymessage(geo='340x120', labelpos_x=130, labelpos_y=48, artwork=icon_dir / 'edb.png', transparency=1.0,
                      bg_=softblue, box_pos_x=width * 2, artpos_x=30, artpos_y=27, message=f"Database Empty!")
            return None

        if len(backup_path) == 0:
            res = messagebox.showwarning(title='no destination',
                                         message='Nowhere to backup!\n'
                                                 'Please choose a path for the backup file destination')
            if res:
                try:
                    br_window.focus_force()
                except TclError:
                    pass
            return None
        if not Path(backup_path).exists():
            res = messagebox.showerror(title='non-existing path',
                                       message='Please provide a valid path')
            if res:
                try:
                    br_window.focus_force()
                except TclError:
                    pass
            return None
        backup_path = Path(backup_path)
        try:
            db.backup_passito(conn, backup_path)
            update_sysdata('backup_dir', str(backup_path))
            mymessage(geo='400x120', labelpos_x=110, labelpos_y=47,
                      artwork=icon_dir / 'bu.png', to_be_focused=br_window,
                      artpos_x=20, artpos_y=30, message=f'Backup created successfully\n', delay=3)
        except Exception as exc_:
            messagebox.showerror(title='error', message=f'An Error Occurred!\nError info: {exc_}')
            return None

    # Backup
    bkp_path = get_sysdata('backup_dir')
    pathbox = Entry(br_window, width=32, font=("consolas", 17), bg=softblue, fg="#daffff", bd=0)
    pathbox.insert(0, bkp_path)
    pathbox.place(x=20, y=65)

    pathbutton = Button(br_window, text='path', font=button_font, width=5, command=backup_path_command,
                       bg="#017C95", fg="#FFFFFF", bd=0, activebackground='cyan', relief='sunken',
                       activeforeground="#0799c2")
    pathbutton.place(x=412, y=64)
    pathbutton.bind('<Enter>', lambda event: on_enter(pathbutton, bg=nightblue))
    pathbutton.bind('<Leave>', lambda event: on_leave(pathbutton, bg="#017C95"))
    backup_now_button = Button(br_window, text='Backup Now', font=button_font, bg=button_bg, width=14,
                               fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='ridge',
                               command=backup_now_command, activeforeground=mint)
    backup_now_button.place(x=331, y=105)
    backup_now_button.bind('<Enter>', lambda event: on_enter(backup_now_button, bg="#329999"))
    backup_now_button.bind('<Leave>', lambda event: on_leave(backup_now_button))

    # restore
    def select_button_command():
        restorefiletype = [('passito_backup','.json')]
        try:
            restore_path = filedialog.askopenfile(mode='r', title='select a passito backup file',
                                                  filetypes=restorefiletype).name
            pathbox2.delete(0, END)
            pathbox2.insert(0, string=str(restore_path))
            if restore_path:
                try:
                    br_window.focus_force()
                except TclError:
                    pass
            return None
        except:
            return None

    def restore_now_command():
        restore_file_path = pathbox2.get()
        if len(restore_file_path) == 0:
            res = messagebox.showwarning(title='nothing selected', message='No files selected!\n'
                                                                           'Please select a passito backup file')
            if res:
                try:
                    br_window.focus_force()
                except TclError:
                    pass
            return None
        if not Path(restore_file_path).exists():
            res = messagebox.showerror(title='not found',
                                       message='Backup file doesn\'t exists!')
            if res:
                try:
                    br_window.focus_force()
                except TclError:
                    pass
            return None
        _res = None
        if len(all_id) == 0:
            _res = True
        elif len(all_id) > 0:
            _res = messagebox.askyesno(title='confirm',
                                  message='Caution: Restoring will result all existing data removed\n'
                                          'Are you sure to proceed?')
        if _res:
            restore_file_path = Path(restore_file_path)
            try:
                db.restore_passito(conn, restore_file_path)
                mymessage(geo='400x120', labelpos_x=110, labelpos_y=48,
                          artwork=icon_dir / 'info2.png', artpos_x=20, artpos_y=30,
                          message=f"Data Restored Successfully", to_be_focused=br_window)
            except Exception as exc_:
                messagebox.showerror(title='error', message=f'An Error Occured!\nError info: {exc_}')
                return None
        else:
            messagebox.showinfo(title='aborted', message='Restoration cancelled')
            try:
                br_window.focus_force()
            except TclError:
                pass
            return None
        try:
            br_window.focus_force()
        except TclError:
            pass
        return None
    pathbox2 = Entry(br_window, width=29, font=("consolas", 17), bg="#7f886a", fg="#daffff", bd=0)
    pathbox2.place(x=82.5, y=160.5)
    select_button = Button(br_window, text='select', font=button_font, width=6, command=select_button_command,
                        bg="#51614F", fg="#FFFFFF", bd=0, activebackground='cyan', relief='sunken',
                        activeforeground="#0799c2")
    select_button.place(x=22.5, y=160)
    select_button.bind('<Enter>', lambda event: on_enter(select_button, bg='#6B6E72'))
    select_button.bind('<Leave>', lambda event: on_leave(select_button, bg="#51614F"))
    restore_now_button = Button(br_window, text='Restore Now', command=restore_now_command, font=button_font,
                                bg="#357256", width=14, fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='ridge',
                                activeforeground=mint)

    restore_now_button.place(x=22.5, y=200)
    restore_now_button.bind('<Enter>', lambda event: on_enter(restore_now_button, bg='#008f77'))
    restore_now_button.bind('<Leave>', lambda event: on_leave(restore_now_button, bg="#357256"))
    cancel_b = Button(br_window, text='Cancel', command=on_closing, font=button_font,
                          width=9, bg=deepred, fg="#FFFFFF", bd=0, activebackground='red',
                          relief='ridge', activeforeground="white")

    cancel_b.place(x=375, y=230)
    cancel_b.bind('<Enter>', lambda event: on_enter(cancel_b, bg='#ad0000'))
    cancel_b.bind('<Leave>', lambda event: on_leave(cancel_b, bg=deepred))
    br_window.protocol("WM_DELETE_WINDOW", on_closing)
    br_window.mainloop()


def list_command(event=None):
    all_id = db.get_id_name_list(conn)
    if len(all_id)==0:
        mymessage(geo='340x120', labelpos_x=130, labelpos_y=48, artwork=icon_dir / 'edb.png', transparency=1.0,
                  bg_=softblue, box_pos_x=width*2, artpos_x=30, artpos_y=27, message=f"Database Empty!")
        return None
    if 'list' in wins:
        try:
            win = wins['list']
            win.focus_force()
        except TclError:
            pass
        return None

    list_w = Toplevel(root)
    list_w.geometry(f'353x620+{int(width*3.3)}+{int(height*0.25)}')
    list_w.title('Database')
    list_w.configure(bg=root_bg)
    list_w.transient(root)
    list_w.resizable(width=0, height=0)
    list_w.iconbitmap(icon_dir/'list.ico')
    list_w.focus_set()
    wins['list'] = list_w

    list_w.bind('<Left>', lambda evnt: idbox.focus_force())
    list_w.bind('<Right>', lambda evnt: idbox.focus_force())
    mainframe = Frame(list_w, bg=deepgreen)
    mainframe.place(x=-1, y=-1)
    mylist = Listbox(mainframe, bg=root_bg, fg='#00C5CD', bd=0, width=26, relief='flat',
                     font=('segoe ui', 18), height=16, selectbackground=softblue2, selectforeground=mint)

    def not_selected():
        f2 = Frame(list_w, bg=deepred, bd=0)
        f2.place(x=-5, y=503)
        Label(f2, text='Select an ID first', bg=deepred, fg='#FFFFFF', width=35,
              font=('consolas', 13, 'bold')).pack()
        try:
            list_w.after(1500, lambda: clear_widget(f2, list_w))
        except:
            pass
        return None

    def create():
        all_ = db.get_id_name_list(conn)
        current_bg = None
        next_bg = None
        prev_item = None
        prev_startswith = None
        for index, item in enumerate(all_):
            mylist.insert(END, f"  [{index + 1}]  " + item)
            if prev_item is None:
                mylist.itemconfigure(index, bg=root_bg)
                current_bg = root_bg
                next_bg = softblue
            elif prev_startswith == item[0]:
                mylist.itemconfigure(index, bg=current_bg)
            elif prev_startswith != item[0]:
                mylist.itemconfigure(index, bg=next_bg)
                current_bg, next_bg = next_bg, current_bg
            prev_item = item
            prev_startswith = item[0]
        return None

    create()
    mylist.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar = Scrollbar(mainframe, width=14, bd=5)
    scrollbar.pack(side=LEFT, fill=Y)
    scrollbar.config(command=mylist.yview, bg=deepgreen, activebackground="gray")
    mylist.config(yscrollcommand=scrollbar.set)

    # \\\
    def on_closing(event_=None):
        del wins['list']
        if 'rename' in wins:
            del wins['rename']
        list_w.destroy()
    list_w.bind('<Shift-Escape>', on_closing)

    def list_getfnc():
        raw_id_name = mylist.get(ANCHOR)
        if len(raw_id_name) == 0:
            not_selected()
            return None
        id_pattern = re.compile(f"\[\d*\]\s*(.*)")
        result = id_pattern.findall(raw_id_name)
        id_name = result[0]

        try:
            credential = db.get_credential(conn, id_name)
            _e_password = credential['password']
        except Exception:
            messagebox.showerror('not found', 'Selected ID may have been deleted!')
            try:
                mylist.delete(0, END)
                create()
                list_w.focus_force()
            except:
                pass
            return None
        try:
            password = decrypt_(_e_password)
        except cryptography.fernet.InvalidToken:
            reset_security_key()
            return None

        pyperclip.copy(password)
        mymessage(geo='400x120', labelpos_x=100, labelpos_y=40, artwork=icon_dir / 'copy.png', justify=LEFT,
                  artpos_x=25, artpos_y=30, message=f">> {id_name}\nPassword Copied to Clipboard", to_be_focused=list_w)
        return None

    def list_getallfnc():
        raw_id_name = mylist.get(ANCHOR)
        if len(raw_id_name) == 0:
            not_selected()
            return None
        id_pattern = re.compile(f"\[\d*\]\s*(.*)")
        result = id_pattern.findall(raw_id_name)
        id_name = result[0]

        try:
            credential = db.get_credential(conn, id_name)
            _e_username = credential['username']
            _e_password = credential['password']
        except Exception:
            messagebox.showerror('not found', 'Selected ID may have been deleted!')
            try:
                mylist.delete(0, END)
                create()
                list_w.focus_force()
            except:
                pass
            return None

        try:
            username = decrypt_(_e_username)
            password = decrypt_(_e_password)
        except cryptography.fernet.InvalidToken:
            reset_security_key()
            return None
        except Exception as exc_:
            messagebox.showerror('error', f'An error occurred!\n info: {exc_}')
            return None
        get_idnpass_direct(id_name=id_name, user=username, password_=password)
        return None

    def edit():
        if 'rename' in wins:
            try:
                win_ = wins['rename']
                win_.focus_force()
            except:
                pass
            return None
        all_ = db.get_id_name_list(conn)
        raw_id_name = mylist.get(ANCHOR)
        if len(raw_id_name) == 0:
            not_selected()
            return None
        id_pattern = re.compile(f"\[\d*\]\s*(.*)")
        result = id_pattern.findall(raw_id_name)
        id_name = result[0]
        if id_name not in all_:
            messagebox.showerror('not found', 'Selected ID may have been deleted!')
            try:
                mylist.delete(0, END)
                create()
                list_w.focus_force()
            except:
                pass
            return None

        rename_w = Toplevel(list_w)
        rename_w.geometry(f'400x150+{int(width * 1.9)}+{int(height * 0.45)}')
        rename_w.title(f"rename '{id_name}'")
        rename_w.configure(bg=softblue)
        rename_w.transient(root)
        rename_w.resizable(width=0, height=0)
        rename_w.iconbitmap(applogo)
        rename_w.focus_set()

        l_ = Label(rename_w, text='Rename selected ID', bg=softblue, fg=mint, font=("Seoge UI", 13))
        l_.place(x=20, y=15)

        def on_closing_r():
            del wins['rename']
            rename_w.destroy()
            return None

        def rename_(event=None):
            new_id_name = id_box.get()
            if len(new_id_name) == 0:
                __res = messagebox.showwarning(title='empty', message='Choose a name')
                if __res:
                    try:
                        id_box.focus_force()
                    except TclError:
                        pass
                return None
            if new_id_name.isdigit():
                __res = messagebox.showwarning('invalid name', 'ID name cannot be an integer!')
                if __res:
                    try:
                        id_box.focus_force()
                    except TclError:
                        pass
                return None
            if new_id_name == id_name:
                __res = messagebox.showwarning(title='unchanged', message='New name is the current name.\n'
                                                                          'Try changing the name, if you wish')
                if __res:
                    try:
                        id_box.focus_force()
                    except TclError:
                        pass
                return None
            if new_id_name in all_:
                __res = messagebox.showwarning(title='duplicate', message='ID with a given name already exists!')
                if __res:
                    try:
                        id_box.focus_force()
                    except TclError:
                        pass
                return None
            db.rename_id(conn, id_name, new_name=new_id_name)
            refresh_accounts()
            _res = messagebox.showinfo(title='updated', message=f"Rename Successful")
            if _res:
                try:
                    mylist.delete(0, END)
                    create()
                    rename_w.destroy()
                    list_w.focus_force()
                except TclError:
                    pass
                return None
        # /
        id_name_l = Label(rename_w, image=id_icon, bg=softblue)
        id_name_l.place(x=20, y=56)
        id_box = Entry(rename_w, width=23, font=boxfont, bg=softblue2, fg=mint, bd=0)
        id_box.place(x=65, y=55)
        wins['rename'] = id_box
        id_box.configure(insertbackground=mint)
        id_box.focus_force()
        id_box.bind("<Return>", rename_)

        rename_b = Button(rename_w, text='Rename', font=button_font, width=15, command=rename_,
                            bg='#008080', fg="#FFFFFF", bd=0, activebackground=root_bg,
                            relief='ridge', cursor='cross', activeforeground="#FFFFFF")
        rename_b.place(x=135, y=105)
        rename_b.bind('<Enter>', lambda event: on_enter(rename_b, bg=button_bg))
        rename_b.bind('<Leave>', lambda event: on_leave(rename_b, bg='#008080'))

        rename_w.protocol("WM_DELETE_WINDOW", on_closing_r)
        rename_w.mainloop()

    def del_():
        all_ = db.get_id_name_list(conn)
        raw_id_name = mylist.get(ANCHOR)
        if len(raw_id_name) == 0:
            not_selected()
            return None
        id_pattern = re.compile(f"\[\d*\]\s*(.*)")
        result = id_pattern.findall(raw_id_name)
        id_name = result[0]
        if id_name not in all_:
            messagebox.showerror('not found', 'Selected ID may have been deleted!')
            try:
                mylist.delete(0, END)
                create()
                list_w.focus_force()
            except:
                pass
            return None
        res = messagebox.askyesno(title=f"delete '{id_name}'", message=f'Are you sure to delete {id_name}?')
        if res:
            db.delete_by_name(conn, id_name=id_name)
            try:
                mylist.delete(0, END)
                refresh_accounts()
                create()
                mymessage(geo='400x120', labelpos_x=100, labelpos_y=48, artwork=icon_dir / 'del2.png',
                          artpos_x=20, artpos_y=30, message=f"Credentials Deleted Successfully", to_be_focused=list_w)
            except TclError:
                pass
            except Exception as exc_:
                messagebox.showinfo('error', f'An error occurred\nerror info: {exc_}')
                try:
                    list_w.focus_force()
                except TclError:
                    pass
            return None
        else:
            try:
                list_w.focus_force()
            except TclError:
                pass
            return None
    # ///
    f1 = Frame(list_w, bg=deepgreen, width=353, height=120)
    f1.place(x=0, y=528)
    listget = Button(f1, text='Get Pass', command=list_getfnc, font=button_font, width=14,
                     bg=button_bg, fg="#FFFFFF", bd=0, activebackground=splash_bg, relief='ridge',
                     cursor='dotbox', activeforeground=mint)
    listget.place(x=50, y=10)
    listget.bind('<Enter>', lambda event: on_enter(listget))
    listget.bind('<Leave>', lambda event: on_leave(listget))
    gall_list_b = Button(f1, text='Get All', command=list_getallfnc, width=14, font=button_font, bg=button_bg,
                           fg="#FFFFFF", bd=0, activebackground=softblue2, relief='ridge', cursor='dotbox',
                           activeforeground='#ffffff')
    gall_list_b.place(x=193, y=10)
    gall_list_b.bind('<Enter>', lambda event: on_enter(gall_list_b))
    gall_list_b.bind('<Leave>', lambda event: on_leave(gall_list_b))
    close_b = Button(f1, text='Close', command=on_closing, font=button_font, width=30,
                     bg=splash_bg, fg="#FFFFFF", bd=0, activebackground='red', relief='ridge',
                     activeforeground="#FFFFFF")
    close_b.place(x=50, y=50)
    close_b.bind('<Enter>', lambda event: on_enter(close_b, bg=deepred))
    close_b.bind('<Leave>', lambda event: on_leave(close_b, bg=splash_bg))
    load1 = Image.open(icon_dir / 'edit.png')
    load2 = Image.open(icon_dir / 'trash.png')
    edit_i = ImageTk.PhotoImage(load1)
    del_i = ImageTk.PhotoImage(load2)
    rename = Button(f1, image=edit_i, command=edit, font=button_font,
                         bg=deepgreen, bd=0, activebackground=deepgreen, relief='ridge')
    rename.place(x=15, y=13)
    del_b = Button(f1, image=del_i, command=del_, font=button_font,
                   bg=deepgreen, bd=0, activebackground=deepgreen, relief='ridge')
    del_b.place(x=15, y=52)
    # //buttons

    list_w.protocol("WM_DELETE_WINDOW", on_closing)
    list_w.mainloop()


idbox.bind('<Shift-Left>', add_command)
idbox.bind('<Shift-Up>', update_command)
idbox.bind('<Shift-Right>', list_command)
idbox.bind('<Shift-Down>', delete_command)
wins = {}
# Add
addButton = Button(root, text='Add', font=button_font,command=add_command, bg="#036e72",
                   height=2, width=10,fg="#13f8ff", bd=0, activebackground=splash_bg, relief='ridge', cursor='dotbox',
                   activeforeground=mint)
addButton.place(x=350, y=105)
addButton.bind('<Enter>', lambda e: on_enter(button=addButton))
addButton.bind('<Leave>', lambda e: on_leave(button=addButton))

# list
listButton = Button(root, text='ViewDB', font=button_font, bg=splash_bg, height=2, command=list_command,
                    width=10, fg=mint, bd=0, activebackground='gray',
                    relief='ridge', cursor='dotbox', activeforeground=mint)
listButton.place(x=450, y=105)
listButton.bind('<Enter>', lambda e: on_enter(button=listButton, bg='#989898'))
listButton.bind('<Leave>', lambda e: on_leave(button=listButton, bg=splash_bg))

# Update
updateButton = Button(root, text='Update', font=button_font, bg=button_bg, command=update_command, height=2, width=10,
                      fg="#13f8ff", bd=0, activebackground=splash_bg, relief='ridge', cursor='dotbox',
                      activeforeground=mint)
updateButton.place(x=450, y=50)
updateButton.bind('<Enter>', lambda e: on_enter(button=updateButton))
updateButton.bind('<Leave>', lambda e: on_leave(button=updateButton))

# delete
delButton = Button(root, text='Delete', font=button_font, command=delete_command, bg=button_bg,
                   height=2, width=10, fg=mint, bd=0, activebackground='red', relief='ridge',
                   cursor='tcross', activeforeground="white")
delButton.place(x=450, y=160)
delButton.bind('<Enter>', lambda e: on_enter(button=delButton, bg=deepred))
delButton.bind('<Leave>', lambda e: on_leave(button=delButton, bg=button_bg))

# backup
backupButton = Button(root, text='Backup', command=backup_command,
                      font=button_font, bg=button_bg, height=2, width=10, fg="#13f8ff", bd=0,
                      activebackground=splash_bg, relief='ridge', cursor='dotbox', activeforeground=mint)
backupButton.place(x=550, y=105)
backupButton.bind('<Enter>', lambda e: on_enter(button=backupButton))
backupButton.bind('<Leave>', lambda e: on_leave(button=backupButton))

root.mainloop()
