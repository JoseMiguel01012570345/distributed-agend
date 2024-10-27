import tkinter as tk
from frontend.activity_view import ActivityView

class AgendView(tk.Toplevel):
    
    def __init__(self,root,server,agend_id,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title('Agend View')
        self.geometry('1600x800')
        self._agend_id = agend_id
        self._root = root
        self.server = server   
        self._Frame = tk.Canvas(self,width=1000,height=600)
        self._Frame.pack(side=tk.LEFT,padx=5,pady=5,expand=True,fill=tk.BOTH)
        self._ScrollBar = tk.Scrollbar(self,orient=tk.VERTICAL,command=self._Frame.yview)
        self._ScrollBar.pack(side=tk.RIGHT,fill=tk.Y)
        self._Frame.configure(yscrollcommand=self._ScrollBar.set)
        self._View = tk.Frame(self._Frame)
        self._Frame.create_window((600,0),window=self._View,anchor=tk.NW)
        self._events = self.server.get_events(self._agend_id)
        self._event_items = []
        for event in self._events['events']:
            _event = self.server.get_event(event)
            if 'date' in _event.keys() and 'description' in _event.keys():
                self._event_items.append(ActivityItem(self._View,self,self.server,event))
                pass
            pass
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
        
        self._create_activity_btn = tk.Button(self,text='Create Activity',command=self.create_activity)
        self._create_activity_btn.pack(side=tk.BOTTOM,pady=10,padx=10)
        self.protocol('WM_DELETE_WINDOW',self.cancel)
        self.mainloop()
        
        pass
    
    def cancel(self):
        self.destroy()
        self._root.deiconify()
        pass
    
    def create_activity(self):
        self.withdraw()
        ActivityView(self,self.server,self._agend_id)
        pass
    
    def update_view(self):
        self._events = self.server.get_events(self._agend_id)
        for event in self._event_items:
            event.destroy()
            pass
        self._event_items = []
        for event in self._events['events']:
            _event = self.server.get_event(event)
            if 'date' in _event.keys() and 'description' in _event.keys():
                self._event_items.append(ActivityItem(self._View,self,self.server,event))
                pass
            pass
        self._View.update_idletasks()
        self._Frame.configure(scrollregion=self._Frame.bbox(tk.ALL))
        pass
    
    pass

class ActivityItem:
    
    def __init__(self,root,master,server,activity_id):
        self._root = root
        self._master = master
        self.server = server
        self._activity_id = activity_id
        self._event = self.server.get_event(self._activity_id)
        self._activity_label = tk.Label(root,text=activity_id)
        self._delete_btn = tk.Button(root,text='Delete',command=self.delete)
        self._date_label = tk.Label(self._root,text=self._event['date'])
        self._description_label = tk.Label(self._root,text=self._event['description'])
        self._activity_label.pack(side=tk.TOP,pady=10,padx=5)
        self._date_label.pack(side=tk.TOP,pady=5,padx=5)
        self._description_label.pack(side=tk.TOP,pady=5,padx=5)
        self._delete_btn.pack(side=tk.TOP,pady=5,padx=5)
        pass
    
    def destroy(self):
        self._activity_label.destroy()
        self._delete_btn.destroy()
        self._date_label.destroy()
        self._description_label.destroy()
        pass
    
    def delete(self):
        self.server.delete_event(self._activity_id)
        self.destroy()
        pass
        
    pass