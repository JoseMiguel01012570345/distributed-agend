import tkinter as tk
from time import gmtime

class ActivityView(tk.Toplevel):
    
    def __init__(self,root,server,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title('Activity View')
        self.geometry('1600x800')
        self._Frame = tk.Frame(self)
        
        self._year = tk.IntVar(self._Frame)
        self._mounth = tk.IntVar(self._Frame)
        self._day = tk.IntVar(self._Frame)
        self._hour = tk.IntVar(self._Frame)
        self._minute = tk.IntVar(self._Frame)
        self._seconds = tk.IntVar(self._Frame)
        self._init_time()
        
        self._controls_frame = tk.Canvas(self)
        self._controls_frame.pack(side=tk.TOP)
        
        self._year_label = tk.Label(self._controls_frame,text='Year')
        self._mounth_label = tk.Label(self._controls_frame,text='Mounth')
        self._day_label = tk.Label(self._controls_frame,text='Day')
        self._hour_label = tk.Label(self._controls_frame,text='Hour')
        self._minute_label = tk.Label(self._controls_frame,text='Minute')
        self._seconds_label = tk.Label(self._controls_frame,text='Seconds')
        
        self._year_entry = tk.Spinbox(self._controls_frame,from_=0,to=3000,increment=1,textvariable=self._year)
        self._mounth_entry = tk.Spinbox(self._controls_frame,from_=1,to=12,increment=1,textvariable=self._mounth)
        self._day_entry = tk.Spinbox(self._controls_frame,from_=1,to=31,increment=1,textvariable=self._day)
        self._hour_entry = tk.Spinbox(self._controls_frame,from_=0,to=24,increment=1,textvariable=self._hour)
        self._minute_entry = tk.Spinbox(self._controls_frame,from_=0,to=59,increment=1,textvariable=self._minute)
        self._seconds_entry = tk.Spinbox(self._controls_frame,from_=0,to=59,increment=1,textvariable=self._seconds)
        
        self._year_label.grid(row=20,column=15,padx=5,pady=5)
        self._mounth_label.grid(row=20,column=115,padx=5,pady=5)
        self._day_label.grid(row=20,column=215,padx=5,pady=5)
        self._hour_label.grid(row=20,column=315,padx=5,pady=5)
        self._minute_label.grid(row=20,column=415,padx=5,pady=5)
        self._seconds_label.grid(row=20,column=515,padx=5,pady=5)
        self._year_entry.grid(row=30,column=15,padx=5,pady=5)
        self._mounth_entry.grid(row=30,column=115,padx=5,pady=5)
        self._day_entry.grid(row=30,column=215,padx=5,pady=5)
        self._hour_entry.grid(row=30,column=315,padx=5,pady=5)
        self._minute_entry.grid(row=30,column=415,padx=5,pady=5)
        self._seconds_entry.grid(row=30,column=515,padx=5,pady=5)
        
        self._description_frame = tk.Canvas(self)
        self._description_frame.pack(side=tk.TOP,fill=tk.BOTH,pady=5,padx=5)
        self._description_textbox = tk.Text(self._description_frame,width=1200)
        self._description_textbox.pack(side=tk.TOP)
        
        self._buttons_frame = tk.Canvas(self)
        self._buttons_frame.pack(side=tk.BOTTOM)
        
        self._create_activity_btn = tk.Button(self._buttons_frame,text='Create')
        self._cancel_btn = tk.Button(self._buttons_frame,text='Cancel')
        self._create_activity_btn.pack(side=tk.LEFT,pady=10,padx=10)
        self._cancel_btn.pack(side=tk.RIGHT,pady=10,padx=10)
        
        self.mainloop()
        
        pass
    
    def _init_time(self):
        now = gmtime()
        self._year.set(now.tm_year)
        self._mounth.set(now.tm_mon)
        self._day.set(now.tm_mday)
        self._hour.set(now.tm_hour)
        self._minute.set(now.tm_min)
        self._seconds.set(now.tm_sec)
        pass
    
    pass