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
    
    def __init__(self,master,activity,agend,root,on_delete_callback=None):
        self._root = root
        self._on_delete_callback = on_delete_callback
        self._master = master
        self._agend = agend
        self._frame = Tk.Canvas(master,relief='solid',width=500,borderwidth=2)
        self._activity = activity
        self._date_label = Tk.Label(self._frame,text='Fecha',font=AUTH_FONT)
        self._activity_date_label = Tk.Label(self._frame,text=activity.date,font=AUTH_FONT)
        self._description_label = Tk.Label(self._frame,text='Detalles',font=AUTH_FONT)
        self._activity_description_label = Tk.Label(self._frame,text=activity.description)
        self._edit_btn = Tk.Button(self._frame,text='Edit',font=AUTH_FONT,command=lambda : self._edit(),bg=rgb_to_hex(100,100,100),fg='white')
        self._delete_btn = Tk.Button(self._frame,text='Delete',font=AUTH_FONT,command=lambda : self._delete(),bg=rgb_to_hex(100,100,100),fg='white')
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
    
    def _delete(self):
        index = self._agend.activitys.index(self._activity)
        self._agend.activitys.pop(index)
        self.destroy()
        if self._on_delete_callback:
            self._on_delete_callback()
            pass
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
        self._group = None
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
    
    @property
    def group(self):
        return self._group
    
    def add(self,activity):
        self._activitys.append(activity)
        pass
    
    def set_group(self,group):
        self._group = group
        pass
    
    pass

def set_agend_view(master,agend,root):
    return [ActivityItem(master,activity,agend,root) for activity in agend.activitys]

def create_activity(view_master,agend,root,view_frame,counter_label):
    
    def add_activity(activity):
        activity = ActivityItem(view_master,activity,agend,root,lambda : update(counter_label,agend)).activity
        agend.add(activity)
        counter_label.config(text=f'Actividades programadas: {len(agend.activitys)}')
        view_master.update_idletasks()
        view_frame.configure(scrollregion=view_frame.bbox('all'))
        pass
    
    root.withdraw()
    ActivityView(root,Activity(''),add_activity)
    pass

def update(counter_label,agend):
    counter_label.config(text=f'Actividades programadas: {len(agend.activitys)}')
    pass

def set_agend_header_view(master,agend,view=None,root=None,view_frame=None):
    
    class packed_data:
        
        def __init__(self,**kwargs):
            self._attrs = kwargs
            pass
        
        def __getattr__(self,attr):
            if attr in self._attrs.keys():
                return self._attrs[attr]
            raise Exception(f'no existe el atributo {attr}')
        
        pass
    
    Frame = Tk.Canvas(master,relief='solid',borderwidth=2,bg=rgb_to_hex(100,100,100))
    OwnerLabel = Tk.Label(Frame,text=agend.owner,font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white')
    AgendGroup = Tk.Label(Frame,text=agend.group,font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white')
    ActivityLabel = Tk.Label(Frame,text=f'Actividades programadas: {len(agend.activitys)}',fg='white',font=AUTH_FONT,bg=rgb_to_hex(100,100,100))
    add_activity_btn = Tk.Button(Frame,text='Add',font=AUTH_FONT,command=lambda : create_activity(view,agend,root,view_frame,ActivityLabel),bg=rgb_to_hex(100,100,100),fg='white')
    
    Frame.pack(side='top',padx=5,pady=5)
    OwnerLabel.pack(side='top',padx=500,pady=10)
    AgendGroup.pack(side='top',padx=500,pady=10)
    ActivityLabel.pack(side='top',padx=5,pady=10)
    add_activity_btn.pack(side='top',padx=5,pady=10)
    return packed_data(group_label=AgendGroup)

def set_window(root,agend):
    
    class packed_data:
        
        def __init__(self,**kwargs):
            self._attrs = kwargs
            pass
        
        def __getattr__(self,attr):
            if attr in self._attrs.keys():
                return self._attrs[attr]
            raise Exception(f'no existe el atributo {attr}')
    
    Frame = Tk.Canvas(root,width=500,height=500,bg=rgb_to_hex(100,100,200))
    Frame.pack(side='left',padx=5,pady=5,expand=True,fill='both')
    ScrollBar = Tk.Scrollbar(root,orient='vertical',command=Frame.yview)
    ScrollBar.pack(side='right',fill='y')
    Frame.configure(yscrollcommand=ScrollBar.set)
    
    View = Tk.Frame(Frame,bg=rgb_to_hex(100,100,200))
    Frame.create_window((600,0),window=View,anchor='nw')
        
    result = set_agend_header_view(View,agend,View,root,Frame)
    set_agend_view(View,agend,root)
    
    View.update_idletasks()
    Frame.configure(scrollregion=Frame.bbox('all'))
    return packed_data(group_label=result.group_label)

class AgendView(Tk.Toplevel):
    
    def __init__(self,agend,callback=None,root=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.config(bg=rgb_to_hex(100,100,200))
        self._root = root
        self._agend = agend
        self._on_back_btn_click_callback = callback
        self.geometry(size)
        self.title('Agend View')
        self._data = set_window(self,agend)
        self._back_btn = Tk.Button(self,text='Back',font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white',command=self._back)
        self._change_group_btn = Tk.Button(self,text='Change Group',font=AUTH_FONT,bg=rgb_to_hex(100,100,100),fg='white',command=self._change_group)
        self._change_group_btn.pack(side='bottom',pady=10,padx=10)
        self._back_btn.pack(side='bottom',pady=10,padx=10)
        self.protocol('WM_DELETE_WINDOW',lambda : self._back())
        self.mainloop()
        pass
    
    def _change_group(self):
        
        def update_group():
            self._data.group_label.config(text=self._agend.group)
            pass
        
        self.withdraw()
        AgendEditGroupView(self._agend,self,update_group)
        pass
    
    def _back(self):
        if self._root:
            self._root.deiconify()
            pass
        self._on_back_btn_click_callback()
        self.destroy()
        pass
    
    pass
    
class AgendViewCreate(Tk.Toplevel):
    
    def __init__(self,on_create_agend_callback=None,root=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._root = root
        self._on_create_agend_callback = on_create_agend_callback
        self.geometry('600x400')
        self.title('Create Agend')
        self.config(bg=rgb_to_hex(100,100,200))
        self._create_agend_label = Tk.Label(self,text='Propietario',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._owner = Tk.StringVar(root)
        self._group = Tk.StringVar(root)
        self._group_enable = Tk.BooleanVar(root)
        self._owner_textbox = Tk.Entry(self,text=self._owner,font=AUTH_FONT)
        self._group_textbox = Tk.Entry(self,text=self._group,font=AUTH_FONT)
        self._group_checkbox = Tk.Checkbutton(self,text='Especificar grupo',font=AUTH_FONT,variable=self._group_enable,command=self._update_group_textbox_state,bg=rgb_to_hex(100,100,200))
        self._create_btn = Tk.Button(self,text='Acept',font=AUTH_FONT,command=self._create,bg=rgb_to_hex(100,100,100),fg='white')
        self._cancel_btn = Tk.Button(self,text='Cancel',font=AUTH_FONT,command=self._cancel,bg=rgb_to_hex(100,100,100),fg='white')
        self.protocol('WM_DELETE_WINDOW',lambda : self._close())
        self._show()
        self.mainloop()
        pass
    
    def _update_group_textbox_state(self):
        if self._group_enable.get():
            self._group_textbox.config(state=Tk.NORMAL)
            pass
        else:
            self._group_textbox.config(state=Tk.DISABLED)
            self._group.set('')
            pass
        pass
    
    def _close(self):
        if self._root:
            self._root.deiconify()
            pass
        self.destroy()
        pass
    
    def _show(self):
        self._create_agend_label.pack(side='top',pady=20,padx=20)
        self._owner_textbox.pack(side='top',padx=20,pady=5)
        self._group_textbox.pack(side='top',padx=20,pady=5)
        self._group_textbox.config(state=Tk.DISABLED)
        self._group_checkbox.pack(side='top',padx=20,pady=5)
        self._create_btn.pack(side='left',pady=10,padx=10)
        self._cancel_btn.pack(side='right',pady=10,padx=10)
        pass
    
    def _validate(self,name):
        return len(name) > 0
    
    def _create(self):
        if self._validate(self._owner.get()):
            self._root.deiconify()
            agend = Agend(self._owner.get())
            if self._group_enable.get() and self._validate(self._group.get()):
                agend.set_group(self._group.get())
                pass
            else:
                agend.set_group('sin grupo')
                pass
            if self._on_create_agend_callback:
                self._on_create_agend_callback(agend)
                pass
            self.destroy()
            pass
        pass
    
    def _cancel(self):
        if self._root:
            self._root.deiconify()
            pass
        self.destroy()
        pass
    
    pass

class AgendEditGroupView(Tk.Toplevel):
    
    def __init__(self,agend,root=None,on_change_group_callback=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._agend = agend
        self._root = root
        self.config(bg=rgb_to_hex(100,100,200))
        self._canvas = Tk.Canvas(self)
        self._on_change_group_callback = on_change_group_callback
        self.geometry('600x400')
        self.title('Change Group')
        self._group_label = Tk.Label(self,text='Grupo',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
        self._group = Tk.StringVar(self._canvas)
        self._group_textbox = Tk.Entry(self,text=self._group,font=AUTH_FONT)
        self._acept_btn = Tk.Button(self,text='Acept',font=AUTH_FONT,command=self._change_group,bg=rgb_to_hex(100,100,100),fg='white')
        self._cancel_btn = Tk.Button(self,text='Cancel',font=AUTH_FONT,command=self._close,bg=rgb_to_hex(100,100,100),fg='white')
        self.protocol('WM_DELETE_WINDOW',lambda : self._close())
        self._show()
        self.mainloop()
        pass
    
    def _validate(self,group):
        return len(group) > 0
    
    def _change_group(self):
        if self._validate(self._group.get()):
            self._agend.set_group(self._group.get())
            if self._on_change_group_callback:
                self._on_change_group_callback()
                pass
            pass
        if self._root:
            self._root.deiconify()
            pass
        self.destroy()
        pass
    
    def _show(self):
        self._group_label.pack(side='top',pady=10)
        self._group_textbox.pack(side='top',pady=10)
        self._acept_btn.pack(side='left',padx=20,pady=20)
        self._cancel_btn.pack(side='right',padx=20,pady=20)
        pass
    
    def _close(self):
        if self._root:
            self._root.deiconify()
            pass
        self.destroy()
        pass
    
    pass