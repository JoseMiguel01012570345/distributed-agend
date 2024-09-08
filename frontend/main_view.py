"""
main view

here's defined the main view page
"""

import tkinter as Tk
from frontend import auth_page,agend_view,activity_view
from frontend.activity_view import Activity
from frontend.agend_view import Agend,AgendView
from frontend.fonts import *

size= '1200x600'

class AgendItem:
    
    def __init__(self,master,agend,root=None):
        self._root = root
        self._master = master
        self._agend = agend
        self._frame = Tk.Canvas(master,relief='solid',width=500,borderwidth=2)
        self._owner_label = Tk.Label(self._frame,text=self._agend.owner,font=AUTH_FONT)
        self._activity_counter_label = Tk.Label(self._frame,text=f'Actividades programadas {len(agend.activitys)}',font=AUTH_FONT)
        self._edit_btn = Tk.Button(self._frame,text='Edit',command=lambda : self._edit(),font=AUTH_FONT)
        self._show()
        pass
    
    def _show(self):
        self._frame.pack(side='top',padx=5,pady=5,expand=True,fill='x')
        self._owner_label.pack(side='top',padx=300,pady=10)
        self._activity_counter_label.pack(side='top',padx=300,pady=10)
        self._edit_btn.pack(side='top',padx=5,pady=5)
        pass
    
    def _edit(self):
        if self._root:
            self._root.withdraw()
            pass
        AgendView(self._agend,lambda agend : print(len(agend.activitys)))
        pass
    
    def destroy(self):
        self._frame.destroy()
        pass
    
    pass

class MainView(Tk.Tk):
    
    def __init__(self,agends,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.geometry(size)
        self.title('Agends')
        self._Frame = Tk.Canvas(self,width=500,height=500)
        self._Frame.pack(side='left',padx=5,pady=5,expand=True,fill='both')
        self._ScrollBar = Tk.Scrollbar(self,orient='vertical',command=self._Frame.yview)
        self._ScrollBar.pack(side='right',fill='y')
        self._Frame.configure(yscrollcommand=self._ScrollBar.set)
        self._View = Tk.Frame(self._Frame)
        self._Frame.create_window((600,0),window=self._View,anchor='nw')
        set_agend_list(self._View,agends,self)
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox('all'))
        pass
    
    pass

def set_agend_list(master,agends,root=None):
    return [AgendItem(master,agend,root) for agend in agends]

def run(agends=[]):
    
    SCREEN = Tk.Tk()
    SCREEN.geometry(size)
    SCREEN.title('Main View')
    
    Frame = Tk.Canvas(SCREEN,width=500,height=500)
    Frame.pack(side='left',padx=5,pady=5,expand=True,fill='both')
    ScrollBar = Tk.Scrollbar(SCREEN,orient='vertical',command=Frame.yview)
    ScrollBar.pack(side='right',fill='y')
    Frame.configure(yscrollcommand=ScrollBar.set)
    
    View = Tk.Frame(Frame)
    Frame.create_window((600,0),window=View,anchor='nw')
    
    set_agend_list(View,agends,SCREEN)
    
    View.update_idletasks()
    Frame.configure(scrollregion=Frame.bbox('all'))
    
    SCREEN.mainloop()
    
    pass