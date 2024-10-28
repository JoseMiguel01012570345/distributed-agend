import tkinter as tk
import time
from frontend.group_view import GroupView
from tkinter import messagebox

class MainView(tk.Toplevel):
    
    def __init__(self,server,root,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._root = root
        self.server = server
        self.title('Main View')
        self.geometry('1600x800')
        self._Frame = tk.Canvas(self,width=1000,height=600)
        self._Frame.pack(side=tk.LEFT,padx=5,pady=5,expand=True,fill=tk.BOTH)
        self._ScrollBar = tk.Scrollbar(self,orient=tk.VERTICAL,command=self._Frame.yview)
        self._ScrollBar.pack(side=tk.RIGHT,fill=tk.Y)
        self._Frame.configure(yscrollcommand=self._ScrollBar.set)
        self._View = tk.Frame(self._Frame)
        self._Frame.create_window((600,0),window=self._View,anchor=tk.NW)
        self._groups = server.get_all_groups()
        self._groups_items = []
        if self._groups:
            self._groups_items = [GroupItem(group,self._groups[group]['agends'],self._View,self,self.server) for group in self._groups.keys()]
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
        self._create_group_btn = tk.Button(self,text='Create group',command=self.create_group)
        self._create_group_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self._log_out_btn = tk.Button(self,text='log out',command=self.cancel)
        self._log_out_btn.pack(side=tk.TOP,pady=10,padx=10)
        self.protocol('WM_DELETE_WINDOW',self.cancel)
        self.mainloop()
        pass
    
    def cancel(self):
        self.destroy()
        self._root.deiconify()
        pass
    
    def create_group(self):
        self.withdraw()
        CreateGroupView(self,self.server)
        pass
    
    def update_view(self):
        self._groups = self.server.get_all_groups()
        if self._groups:
            for group in self._groups_items:
                group.destroy()
                pass
            self._groups_items = [GroupItem(group,self._groups[group]['agends'],self._View,self,self.server) for group in self._groups.keys()]
            self._View.update_idletasks()
            self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        pass
    
    pass

class CreateGroupView(tk.Toplevel):
    
    def __init__(self,root,server,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._root = root
        self.server = server
        self.title('Create Group')
        self.geometry('800x600')
        self._frame = tk.Frame(self)
        self._groupname = tk.StringVar(self._frame)
        self._groupname_textbox = tk.Entry(self,text=self._groupname)
        self._groupname_label = tk.Label(self,text='Group Name')
        self._create_btn = tk.Button(self,text='Create',command=self.create_group)
        self._cancel_btn = tk.Button(self,text='Cancel',command=self.cancel)
        self._groupname_label.pack(side=tk.TOP,pady=10,padx=10)
        self._groupname_textbox.pack(side=tk.TOP,pady=10,padx=10)
        self._cancel_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self._create_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self.protocol('WM_DELETE_WINDOW',self.cancel)
        self.mainloop()
        pass
    
    def create_group(self):
        if self.server.create_group(self._groupname.get()):
            self.destroy()
            self._root.deiconify()
            self._root.update_view()
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        pass
    
    def cancel(self):
        self.destroy()
        self._root.deiconify()
        pass
    
    pass

class GroupItem:
    
    def __init__(self,name,agends,root,master,server):
        self.server = server
        self._master = master
        self._name = name
        self._agends = agends
        self._root = root
        self._name_label = tk.Label(self._root,text=self._name)
        self._edit_btn = tk.Button(self._root,text='Edit',command=self.edit)
        self._delete_btn = tk.Button(self._root,text='Delete',command=self.delete)
        self._name_label.pack(side=tk.TOP,pady=30,padx=10)
        self._edit_btn.pack(side=tk.TOP,pady=5,padx=10)
        self._delete_btn.pack(side=tk.TOP,pady=5,padx=10)
        pass
    
    def destroy(self):
        self._name_label.destroy()
        self._edit_btn.destroy()
        self._delete_btn.destroy()
        pass
    
    def delete(self):
        if self.server.delete_group(self._name):
            self.destroy()
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        pass
    
    def edit(self):
        self._master.withdraw()
        GroupView(self._master,self.server,self._name)
        pass
    
    pass