"""
agend view

here's defined the agend view page
"""

import tkinter as Tk
from frontend.fonts import *
from frontend import activity_view
from frontend.activity_view import Activity,ActivityView

size = '1200x600'

class ActivityItem:
    
    def __init__(self,master,activity,agend,root):
        self._root = root
        self._master = master
        self._agend = agend
        self._frame = Tk.Canvas(master,relief='solid',width=500,borderwidth=2)
        self._activity = activity
        self._date_label = Tk.Label(self._frame,text='Fecha',font=AUTH_FONT)
        self._activity_date_label = Tk.Label(self._frame,text=activity.date,font=AUTH_FONT)
        self._description_label = Tk.Label(self._frame,text='Detalles',font=AUTH_FONT)
        self._activity_description_label = Tk.Label(self._frame,text=activity.description)
        self._edit_btn = Tk.Button(self._frame,text='Edit',font=AUTH_FONT,command=lambda : self._edit())
        self._delete_btn = Tk.Button(self._frame,text='Delete',font=AUTH_FONT,command=lambda : self.destroy())
        self._show()
        pass
    
    @property
    def activity(self):
        return self._activity
    
    def _edit(self):
        
        def change_activity(old,new,act_label,desc_label,agend):
            index = agend.activitys.index(old)
            agend.activitys[index] = new
            old = new
            act_label.configure(text=new.date)
            desc_label.configure(text=new.description)
            pass
        
        self._root.withdraw()
        ActivityView(self._root,self._activity,lambda activity: change_activity(self._activity,activity,self._activity_date_label,self._activity_description_label,self._agend))
        pass
    
    def _show(self):
        self._frame.pack(side='top',pady=20,fill='both',expand=True)
        self._date_label.pack(side='top',pady=5,padx=300)
        self._activity_date_label.pack(side='top',pady=5,padx=300)
        self._description_label.pack(side='top',pady=5,padx=300)
        self._activity_description_label.pack(side='top',pady=5,padx=300)
        self._edit_btn.pack(side='left',pady=5,padx=20)
        self._delete_btn.pack(side='right',pady=5,padx=20)
        pass
    
    def destroy(self):
        self._frame.destroy()
        pass
    
    pass

class Agend:
    
    def __init__(self,owner,*activitys):
        self._owner = owner
        self._activitys = list(activitys)
        pass
    
    def __getitem__(self,index):
        return self._activitys[index]
    
    def __setitem__(self,index,value):
        self._activitys[index] = value
        pass
    
    @property
    def activitys(self):
        return self._activitys
    
    @property
    def owner(self):
        return self._owner
    
    def add(self,activity):
        self._activitys.append(activity)
        pass
    
    pass

def set_agend_view(master,agend,root):
    return [ActivityItem(master,activity,agend,root) for activity in agend.activitys]

def create_activity(view_master,agend,root,view_frame):
    
    def add_activity(activity):
        activity = ActivityItem(view_master,activity,agend,root).activity
        agend.add(activity)
        view_master.update_idletasks()
        view_frame.configure(scrollregion=view_frame.bbox('all'))
        pass
    
    ActivityView(root,Activity(''),add_activity)
    pass

def set_agend_header_view(master,agend,view=None,root=None,view_frame=None):
    Frame = Tk.Canvas(master,relief='solid',borderwidth=2)
    OwnerLabel = Tk.Label(Frame,text=agend.owner,font=AUTH_FONT)
    ActivityLabel = Tk.Label(Frame,text=f'Actividades programadas: {len(agend.activitys)}',font=AUTH_FONT)
    add_activity_btn = Tk.Button(Frame,text='Add',font=AUTH_FONT,command=lambda : create_activity(view,agend,root,view_frame))
    
    Frame.grid(row=10,column=10,padx=5,pady=5)
    OwnerLabel.pack(side='top',padx=5,pady=10)
    ActivityLabel.pack(side='top',padx=5,pady=10)
    add_activity_btn.pack(side='top',padx=5,pady=10)
    pass    

def set_window(root,agend):
    Frame = Tk.Canvas(root,width=500,height=500)
    Frame.pack(side='left',padx=5,pady=5,expand=True,fill='both')
    ScrollBar = Tk.Scrollbar(root,orient='vertical',command=Frame.yview)
    ScrollBar.pack(side='right',fill='y')
    Frame.configure(yscrollcommand=ScrollBar.set)
    
    View = Tk.Frame(Frame)
    Frame.create_window((600,0),window=View,anchor='nw')
        
    set_agend_header_view(Frame,agend,View,root,Frame)
    set_agend_view(View,agend,root)
    
    View.update_idletasks()
    Frame.configure(scrollregion=Frame.bbox('all'))
    pass

class AgendView(Tk.Toplevel):
    
    def __init__(self,agend,callback=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.geometry(size)
        self.title('Agend View')
        set_window(self,agend)
        pass
    
    pass