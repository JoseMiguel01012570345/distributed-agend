import tkinter as tk
from tkinter import messagebox
from frontend.main_view import MainView
class AuthPage(tk.Tk):
    
    def __init__(self,server,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.server = server
        self.title('login')
        self.geometry('700x400')
        self._username = tk.StringVar(self)
        self._password = tk.StringVar(self)
        self._username_label = tk.Label(self,text='Username')
        self._password_label = tk.Label(self,text='Password')
        self._auth_name_textbox = tk.Entry(self,text=self._username)
        self._auth_password_textbox = tk.Entry(self,text=self._password)
        self._log_btn = tk.Button(self,text='Log in',command=self._log_in)
        self._sign_in_btn = tk.Button(self,text='Create Account',command=self._sign_in)
        self._show()
        self.mainloop()
        pass
    
    def _show(self):
        self._username_label.pack(side='top',pady=5)
        self._auth_name_textbox.pack(side='top',pady=5)
        self._password_label.pack(side='top',pady=5)
        self._auth_password_textbox.pack(side='top',pady=5)
        self._log_btn.pack(side='top',pady=20)
        self._sign_in_btn.pack(side='top',pady=5)
        pass
    
    def _sign_in(self):
        self.withdraw()
        CreateAccount(self)
        pass
    
    def _log_in(self):
        if self.server.authenticate_user(self._username.get(),self._password.get()):
            self.destroy()
            MainView(self.server)
            pass
        else:
            messagebox.showwarning('No autenticado','El usuario no esta registrado')
            pass
        pass
    
    pass

class CreateAccount(tk.Toplevel):
    
    def __init__(self,root,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._root = root
        self.title('Create Account')
        self.geometry('700x400')
        self._frame = tk.Frame(self)
        self._username = tk.StringVar(self._frame)
        self._password = tk.StringVar(self._frame)
        self._password_confirmation = tk.StringVar(self._frame)
        self._username_label = tk.Label(self,text='Username')
        self._password_label = tk.Label(self,text='Password')
        self._password_confirmation_label = tk.Label(self,text='Password confirmation')
        self._username_textbox = tk.Entry(self,text=self._username)
        self._password_textbox = tk.Entry(self,text=self._password)
        self._password_confirmation_textbox = tk.Entry(self,text=self._password_confirmation)
        self._create_btn = tk.Button(self,text='Create Account',command=self.create_account)
        self._cancel_btn = tk.Button(self,text='Cancel',command=self.cancel)
        self._show()
        self.protocol('WM_DELETE_WINDOW',self.cancel)
        pass
    
    def _show(self):
        self._username_label.pack(side='top',padx=300,pady=10)
        self._username_textbox.pack(side='top',padx=10,pady=10)
        self._password_label.pack(side='top',padx=10,pady=10)
        self._password_textbox.pack(side='top',padx=10,pady=10)
        self._password_confirmation_label.pack(side='top',padx=10,pady=10)
        self._password_confirmation_textbox.pack(side='top',padx=10,pady=10)
        self._create_btn.pack(side='top',padx=10,pady=15)
        self._cancel_btn.pack(side='top',padx=10,pady=15)
        pass
    
    def cancel(self):
        self.destroy()
        self._root.deiconify()
        pass
    
    def create_account(self):
        
        if len(self._username.get()) > 0 and self._password.get() == self._password_confirmation.get():
            self._root.server.create_user(self._username.get(),self._password.get())
            self.destroy()
            self._root.deiconify()
            pass
        else:
            messagebox.showwarning('Invalid data','Username most be filled and password most matchs')
            pass
        
        pass
    
    pass