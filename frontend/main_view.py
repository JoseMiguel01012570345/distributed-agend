"""
main view

here's defined the main view page
"""

import tkinter as Tk
from frontend import auth_page,agend_view,activity_view
from frontend.activity_view import Activity
from frontend.agend_view import Agend,AgendView,AgendViewCreate
from frontend.fonts import *

size= '1200x600'

class AgendItem:
    
    def __init__(self,master,agend,root=None):
        self._root = root
        self._master = master
        self._agend = agend
        self._frame = Tk.Canvas(master,relief='solid',width=500,borderwidth=2,bg=rgb_to_hex(100,100,100))
        self._owner_label = Tk.Label(self._frame,text=self._agend.owner,font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white')
        self._agend_group = Tk.Label(self._frame,text=self._agend.group,font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white')
        self._activity_counter_label = Tk.Label(self._frame,text=f'Actividades programadas: {len(agend.activitys)}',font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white')
        self._edit_btn = Tk.Button(self._frame,text='Edit',command=lambda : self._edit(),font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white')
        self._show()
        pass
    
    def _show(self):
        self._frame.pack(side='top',padx=5,pady=5,expand=True,fill='x')
        self._owner_label.pack(side='top',padx=300,pady=10)
        self._agend_group.pack(side='top',padx=300,pady=10)
        self._activity_counter_label.pack(side='top',padx=300,pady=10)
        self._edit_btn.pack(side='top',padx=5,pady=5)
        pass
    
    def _edit(self):
        
        def update():
            self._activity_counter_label.config(text=f'Actividades programadas: {len(self._agend.activitys)}')
            self._agend_group.config(text=self._agend.group)
            pass
        
        self._root.withdraw()
        AgendView(self._agend,lambda: update(),self._root)
        pass
    
    def destroy(self):
        self._frame.destroy()
        pass
    
    pass

class MainView(Tk.Tk):
    
    """
    agends: list(Agend)
    on_save_data_callback: func(list(Agend),Agend) -> bool (debe retornar true si el guardado de datos fue exitoso)
    """
    
    def __init__(self,agends=[],on_save_data_callback=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._on_save_data_callback = on_save_data_callback
        self._center_win()
        self.title('Agends')
        self._Frame = Tk.Canvas(self,width=500,height=500,bg=rgb_to_hex(100,100,200))
        self._Frame.pack(side='left',padx=5,pady=5,expand=True,fill='both')
        self._ScrollBar = Tk.Scrollbar(self,orient='vertical',command=self._Frame.yview)
        self._ScrollBar.pack(side='right',fill='y')
        self._Frame.configure(yscrollcommand=self._ScrollBar.set)
        self._View = Tk.Frame(self._Frame,bg=rgb_to_hex(100,100,200))
        self._Frame.create_window((600,0),window=self._View,anchor='nw')
        self._agends = agends
        set_agend_list(self._View,agends,self)
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox('all'))
        self._add_agend_btn = Tk.Button(self,text='Add',font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white',command=lambda : self._add_agend())
        self._add_agend_btn.pack(side='bottom',pady=10,padx=10)
        self.config(bg=rgb_to_hex(100,100,200))
        self.mainloop()
        pass

    def _center_win(self):
        win_width,win_height = self.winfo_screenwidth(),self.winfo_screenheight()
        width,height = int(size.split('x')[0]),int(size.split('x')[0])
        x,y = win_width // 2 - width // 2,win_height // 2 - height // 2
        self.geometry(f'{size}+{x}+{y}')
        pass

    def _add_agend(self):
        
        def update(agend):
            if self._on_save_data_callback:
                if self._on_save_data_callback(agend):
                    self._agends.append(agend)
                    AgendItem(self._View,agend,self)
                    self._View.update_idletasks()
                    self._Frame.configure(scrollregion=self._Frame.bbox('all'))
                    pass
                pass
            else:
                self._agends.append(agend)
                AgendItem(self._View,agend,self)
                self._View.update_idletasks()
                self._Frame.configure(scrollregion=self._Frame.bbox('all'))
                pass
            pass
        
        self.withdraw()
        AgendViewCreate(lambda agend: update(agend),self)
        pass
    
    pass

def set_agend_list(master,agends,root=None):
    return [AgendItem(master,agend,root) for agend in agends]