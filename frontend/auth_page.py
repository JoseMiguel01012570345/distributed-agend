"""
auth page

here's defined the authentication page
"""

import tkinter as Tk
from frontend.fonts import *
from string import whitespace

global authenticated
global message

size = '800x400'
authenticated = False
message = ''

def validate(username,password):
    
    class validation_result:
        
        def __init__(self,result,message=None):
            self.result = result
            self.message = message
            pass

        pass
    
    if not type(username) == str or not type(password) == str:
        return validation_result(False,'"username" y "password" deben ser cadenas de caracteres')
    if len(username) == 0 or len(password) == 0:
        return validation_result(False,'Ambos campos deben ser llenados')
    for char in whitespace:
        if char in username or char in password:
            return validation_result(False,'Los valores de los campos no deben contener ninguno de los carateres \\t,\\n o espacios en blanco')
        pass
    return validation_result(True)

def confirm(username,password):
    
    class auth_response:
        
        def __init__(self,result,message=None):
            self.result = result
            self.message = message
            pass
        
        pass
    
    return auth_response(True,'OK')

def log_in(username,password,auth_msg):
    global authenticated
    global message
    
    val = validate(username,password)
    if val.result:
        log_result = confirm(username,password)
        authenticated = log_result.result
        message = log_result.message
        pass
    else:
        authenticated = False
        message = val.message
        pass
    auth_msg.config(text=message)
    pass        
    
def run(url):
    global authenticated
    global message
    
    SCREEN = Tk.Tk()
    SCREEN.geometry(size)
    SCREEN.title('Log in')
    UserName = Tk.StringVar(SCREEN)
    Password = Tk.StringVar(SCREEN)

    title = Tk.Label(SCREEN,text='Title',font=AUTH_FONT)
    auth_msg_label = Tk.Label(SCREEN,text='')
    
    auth_name_textbox = Tk.Entry(SCREEN,font=AUTH_FONT,text=UserName)
    auth_password_textbox = Tk.Entry(SCREEN,font=AUTH_FONT,text=Password)
    
    log_btn = Tk.Button(SCREEN,text='Log in',font=AUTH_FONT,command=lambda: log_in(UserName.get(),Password.get(),auth_msg_label))
    
    title.pack(side='top',pady=20)
    auth_name_textbox.pack(side='top',pady=5)
    auth_password_textbox.pack(side='top',pady=5)
    auth_msg_label.pack(side='top',pady=5)
    log_btn.pack(side='top',pady=20)

    SCREEN.mainloop()
    
    return authenticated,message