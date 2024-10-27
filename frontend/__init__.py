"""
visual

contains constants for the visual of the frontend
"""

from frontend.agend_view import AgendView,Agend,AgendViewCreate
from frontend.activity_view import Activity,ActivityView
from frontend.main_view import MainView
from frontend.auth_page import AuthView,LoginView
from frontend.frontend_callbacks import *
from frontend.fonts import *
import tkinter as Tk
from tkinter import messagebox

class Application:
    
    def __init__(self,url,**kwargs):
        self._callbacks = kwargs
        pass
    
    def run(self):
        
        def on_login_callback(username,password,callback):
            if self._callbacks['on_login_callback'](username,password):
                callback()
                MainView()
                pass
            else:
                messagebox.showwarning('Connection Error',message='Fallo al autenticarse')
                pass
            pass
        
        def on_create_account_callback(username,password,callback):
            if not self._callbacks['on_create_account_callback'](username,password):
                messagebox.showwarning('Connection Error',message='Fallo al crear la cuenta')
                pass
            callback()
            pass    
                
        if 'on_login_callback' in self._callbacks.keys():
            if 'on_create_account_callback' in self._callbacks.keys():
                AuthView(on_login_callback,on_create_account_callback)
                pass
            else:
                AuthView(on_login_callback,lambda username,password,callback: callback())
                pass
            pass
        else:
            AuthView(null_login,lambda username,password,callback: callback())
            pass
        pass
    
    pass

def null_login(username,password,callback):
    callback()
    MainView()
    pass