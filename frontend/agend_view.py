import tkinter as tk

class AgendView(tk.Toplevel):
    
    def __init__(self,root,server,activitys,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title('Agend View')
        self.geometry('1600x800')
        
        self._Frame = tk.Canvas(self,width=1000,height=600)
        self._Frame.pack(side=tk.LEFT,padx=5,pady=5,expand=True,fill=tk.BOTH)
        self._ScrollBar = tk.Scrollbar(self,orient=tk.VERTICAL,command=self._Frame.yview)
        self._ScrollBar.pack(side=tk.RIGHT,fill=tk.Y)
        self._Frame.configure(yscrollcommand=self._ScrollBar.set)
        self._View = tk.Frame(self._Frame)
        self._Frame.create_window((600,0),window=self._View,anchor=tk.NW)
        # mostrar las activitys
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
        
        self._create_activity_btn = tk.Button(self,text='Create Activity')
        self._create_activity_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        
        self.mainloop()
        
        pass
    
    pass

class ActivityItem:
    
    def __init__(self,root,master,server,activity_id):
        self._root = root
        self._activity_label = tk.Label(root,text=activity_id)
        self._edit_btn = tk.Button(root,text='Edit')
        self._delete_btn = tk.Button(root,text='Delete')
        self._activity_label.pack(side=tk.TOP,pady=10,padx=5)
        self._edit_btn.pack(side=tk.TOP,pady=5,padx=5)
        self._delete_btn.pack(side=tk.TOP,pady=5,padx=5)
        
        pass
    
    pass