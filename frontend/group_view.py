import tkinter as tk
from frontend.agend_view import AgendView
from tkinter import messagebox

class GroupView(tk.Toplevel):
    
    def __init__(self,root,server,groupname,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.server = server
        self._groupname = groupname
        self._root = root
        self.title('Group View')
        self.geometry('1600x800')
        self._add_agend_btn = tk.Button(self,text='Add Agend',command=self.create_agend)
        self._add_agend_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self._Frame = tk.Canvas(self,width=1000,height=600)
        self._Frame.pack(side=tk.LEFT,padx=5,pady=5,expand=True,fill=tk.BOTH)
        self._ScrollBar = tk.Scrollbar(self,orient=tk.VERTICAL,command=self._Frame.yview)
        self._ScrollBar.pack(side=tk.RIGHT,fill=tk.Y)
        self._Frame.configure(yscrollcommand=self._ScrollBar.set)
        self._View = tk.Frame(self._Frame)
        self._Frame.create_window((600,0),window=self._View,anchor=tk.NW)
        self._agends = self.server.get_agends_by_group(self._groupname)
        self._agends_items = []
        if self._agends:
            self._agends_items = [AgendItem(self._View,self,self.server,agend_id) for agend_id in self._agends['agends']]
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
        self.protocol('WM_DELETE_WINDOW',self.cancel)
        self.mainloop()
        pass
    
    def cancel(self):
        self.destroy()
        self._root.deiconify()
        pass
    
    def create_agend(self):
        self.withdraw()
        CreateAgendView(self,self.server,self._groupname)
        pass
    
    def update_view(self):
        self._agends = self.server.get_agends_by_group(self._groupname)
        if self._agends:
            for item in self._agends_items:
                item.destroy()
                pass
            self._agends_items = [AgendItem(self._View,self,self.server,agend_id) for agend_id in self._agends['agends']]
            self._View.update_idletasks()
            self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        pass
    
    pass

class CreateAgendView(tk.Toplevel):
    
    def __init__(self,root,server,groupname,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.server = server
        self._root = root
        self._groupname = groupname
        self.title('Create Agend')
        self.geometry('600x400')
        self._agend_name_label = tk.Label(self,text='Agend Name')
        self._Frame = tk.Frame(self)
        self._agend_name = tk.StringVar(self._Frame)
        self._agend_textbox = tk.Entry(self,text=self._agend_name)
        self._create_btn = tk.Button(self,text='Create',command=self.create_agend)
        self._cancel_btn = tk.Button(self,text='Cancel',command=self.cancel)
        self._agend_name_label.pack(side=tk.TOP,pady=10,padx=10)
        self._agend_textbox.pack(side=tk.TOP,pady=10,padx=10)
        self._cancel_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self._create_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self.protocol('WM_DELETE_WINDOW',self.cancel)
        self.mainloop()
        
        pass
    
    def cancel(self):
        self.destroy()
        self._root.deiconify()
        pass
    
    def create_agend(self):
        if self.server.create_agend(self._agend_name.get(),self._groupname):
            self.destroy()
            self._root.deiconify()
            self._root.update_view()
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        pass
    
    pass

class AgendItem:
    
    def __init__(self,root,master,server,agend_id):
        self._root = root
        self._master = master
        self.server = server
        self._agend_id = agend_id
        self._agend_name_label = tk.Label(root,text=agend_id)
        self._edit_btn = tk.Button(root,text='Edit',command=self.edit)
        self._delete_btn = tk.Button(root,text='Delete',command=self.delete)
        self._agend_name_label.pack(side=tk.TOP,pady=15,padx=5)
        self._edit_btn.pack(side=tk.TOP,pady=5,padx=5)
        self._delete_btn.pack(side=tk.TOP,pady=5,padx=5)
        pass
    
    def destroy(self):
        self._agend_name_label.destroy()
        self._edit_btn.destroy()
        self._delete_btn.destroy()
        pass
    
    def edit(self):
        self._master.withdraw()
        AgendView(self._master,self.server,self._agend_id)
        pass
    
    def delete(self):
        if self.server.delete_agend(self._agend_id):
            self.destroy()
            pass
        else:
            messagebox.showwarning('CONNECTION ERROR','No se ha podido conectar al servidor')
            pass
        pass
    
    pass