"""
auth page

here's defined the authentication page
"""

import tkinter as Tk
from frontend.fonts import *
from string import whitespace

size = '800x400'

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
    
class AuthView(Tk.Tk):
    
    def __init__(self,url,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._url = url
        self._authenticated = False
        self._msg = ''
        self.geometry(size)
        self.title('log in')
        self._username = Tk.StringVar(self)
        self._password = Tk.StringVar(self)
        self._title_label = Tk.Label(self,text='Title',font=AUTH_FONT)
        self._auth_msg_label = Tk.Label(self,text='')
        self._auth_name_textbox = Tk.Entry(self,font=AUTH_FONT,text=self._username)
        self._auth_password_textbox = Tk.Entry(self,font=AUTH_FONT,text=self._password)
        self._log_btn = Tk.Button(self,text='Log in',font=AUTH_FONT,command=self._log_in)
        self._show()
        self.mainloop()
        pass
 
    @property
    def authenticated(self):
        return self._authenticated
    
    @property
    def message(self):
        return self._msg
    
    def _show(self):
        self._title_label.pack(side='top',pady=20)
        self._auth_name_textbox.pack(side='top',pady=5)
        self._auth_password_textbox.pack(side='top',pady=5)
        self._auth_msg_label.pack(side='top',pady=5)
        self._log_btn.pack(side='top',pady=20)
        pass
    
    def _log_in(self):
        
        val = validate(self._username.get(),self._password.get())
        color = 'blue'
        if val.result:
            log_result = confirm(self._username.get(),self._password.get())
            self._authenticated = log_result.result
            self._msg = log_result.message
            pass
        else:
            self._authenticated = False
            self._msg = val.message
            color = 'red'
            pass
        self._auth_msg_label.config(text=self._msg,fg=color)
        pass
    
    pass