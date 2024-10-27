"""
auth page

here's defined the authentication page
"""

import tkinter as Tk
from frontend.fonts import *
from string import whitespace

size = '800x600'

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
    
    """
    on_login_callback: func(str,str,callback) donde callback no recibe argumentos
    """
    
    def __init__(self,on_login_callback=None,on_create_account_callback=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._on_login_callback = on_login_callback
        self._on_create_account_callback = on_create_account_callback
        self._authenticated = False
        self._msg = ''
        self._center_win()
        self.title('log in')
        self.config(bg=rgb_to_hex(100,100,200))
        self._username = Tk.StringVar(self)
        self._password = Tk.StringVar(self)
        self._title_label = Tk.Label(self,text='Title',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._username_label = Tk.Label(self,text='Username',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._password_label = Tk.Label(self,text='Password',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._auth_msg_label = Tk.Label(self,text='',bg=rgb_to_hex(100,100,200))
        self._auth_name_textbox = Tk.Entry(self,font=AUTH_FONT,text=self._username)
        self._auth_password_textbox = Tk.Entry(self,font=AUTH_FONT,text=self._password)
        self._log_btn = Tk.Button(self,text='Log in',font=AUTH_FONT,command=self._log_in)
        self._sign_in_btn = Tk.Button(self,text='Create Account',font=AUTH_FONT,command=self._create_account)
        self._show()
        self.mainloop()
        pass
    
    def _center_win(self):
        win_width,win_height = self.winfo_screenwidth(),self.winfo_screenheight()
        width,height = int(size.split('x')[0]),int(size.split('x')[0])
        x,y = win_width // 2 - width // 2,win_height // 2 - height // 2
        self.geometry(f'{size}+{x}+{y}')
        pass
    
    def _create_account(self):
        self.withdraw()
        LoginView(self,self._on_create_account_callback)
        pass
    
    def _show(self):
        self._title_label.pack(side='top',pady=20)
        self._username_label.pack(side='top',pady=5)
        self._auth_name_textbox.pack(side='top',pady=5)
        self._password_label.pack(side='top',pady=5)
        self._auth_password_textbox.pack(side='top',pady=5)
        self._auth_msg_label.pack(side='top',pady=5)
        self._log_btn.pack(side='top',pady=20)
        self._sign_in_btn.pack(side='top',pady=5)
        pass
    
    def _log_in(self):
        
        val = validate(self._username.get(),self._password.get())
        if val.result:
            log_result = confirm(self._username.get(),self._password.get())
            self._authenticated = log_result.result
            self._msg = log_result.message
            if self._on_login_callback:
                self._on_login_callback(self._username.get(),self._password.get(),self.destroy)
                pass
            pass
        else:
            self._authenticated = False
            self._msg = val.message
            self._auth_msg_label.config(text=self._msg,fg='red')
            pass
        pass
    
    pass

class LoginView(Tk.Toplevel):
    
    def __init__(self,root=None,on_create_account_callback=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._root = root
        self._on_create_account_callback = on_create_account_callback
        self._center_win()
        self.title('Create Account')
        self.config(bg=rgb_to_hex(100,100,200))
        self._frame = Tk.Frame(self)
        self._username = Tk.StringVar(self._frame)
        self._password = Tk.StringVar(self._frame)
        self._password_confirm = Tk.StringVar(self._frame)
        self._username_label = Tk.Label(self,text='Username',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._password_label = Tk.Label(self,text='Password',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._password_confirm_label = Tk.Label(self,text='Confirm',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._username_textbox = Tk.Entry(self,text=self._username,font=AUTH_FONT)
        self._password_textbox = Tk.Entry(self,text=self._password,font=AUTH_FONT)
        self._password_confirm_textbox = Tk.Entry(self,text=self._password_confirm,font=AUTH_FONT)
        self._notify_label = Tk.Label(self,text='',bg=rgb_to_hex(100,100,200))
        self._create_btn = Tk.Button(self,text='Create',font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white',command=self._create_account)
        self._cancel_btn = Tk.Button(self,text='Cancel',font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white',command=self._cancel)
        self.protocol('WM_DELETE_WINDOW',self._cancel)
        self._show()
        self.mainloop()
        pass
    
    def _center_win(self):
        win_width,win_height = self.winfo_screenwidth(),self.winfo_screenheight()
        width,height = int(size.split('x')[0]),int(size.split('x')[0])
        x,y = win_width // 2 - width // 2,win_height // 2 - height // 2
        self.geometry(f'{size}+{x}+{y}')
        pass
    
    def _show(self):
        self._username_label.pack(side='top',padx=300,pady=10)
        self._username_textbox.pack(side='top',padx=10,pady=10)
        self._password_label.pack(side='top',padx=10,pady=10)
        self._password_textbox.pack(side='top',padx=10,pady=10)
        self._password_confirm_label.pack(side='top',padx=10,pady=10)
        self._password_confirm_textbox.pack(side='top',padx=10,pady=10)
        self._notify_label.pack(side='top',padx=10,pady=10)
        self._create_btn.pack(side='top',padx=10,pady=15)
        self._cancel_btn.pack(side='top',padx=10,pady=15)
        pass
    
    def _create_account(self):
        if not self._password.get() == self._password_confirm.get():
            self._notify_label.config(text="the passwords doesn't matches")
            return
        r = validate(self._username.get(),self._password.get())
        if r.result:
            if self._on_create_account_callback:
                self._on_create_account_callback(self._username.get(),self._password.get(),self.destroy)
                if self._root:
                    self._root.deiconify()
                    pass
                pass
            elif self._root:
                self._root.deiconify()
                pass
            pass
        else:
            self._notify_label.config(text=r.message)
            pass
        pass
    
    def _cancel(self):
        if self._root:
            self._root.deiconify()
            pass
        self.destroy()
        pass
    
    pass