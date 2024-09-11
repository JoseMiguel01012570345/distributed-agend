"""
activity view
"""

import tkinter as Tk
import re
from datetime import datetime
from frontend.fonts import *
from time import gmtime

size = '1200x600'

def save_activity(date_struct,description,msg_logger,activity,callback=None,father=None,view=None):
    
    y = date_struct.year.get()
    mon = date_struct.mounth.get()
    d = date_struct.day.get()
    h = date_struct.hour.get()
    m = date_struct.minute.get()
    s = date_struct.second.get()
    
    date = f'{y}-{mon}-{d} {h}:{m}:{s}'
    desc = description.get('1.0',Tk.END)
    msg_logger.config(text=activity.update(date=date,description=desc[:len(desc) - 1]))
    
    if callback:
        callback(activity)
        pass
    if father and view:
        finish(father,view)
        pass
    pass

def finish(father,view):
    father.deiconify()
    view.destroy()
    pass

def cancel(master,father=None):
    if father:
        father.deiconify()
        pass
    master.destroy()
    pass

def validate_date(date,hour):
    date_parsed = date.split('-')
    hour_parsed = hour.split(':')
    year,mounth,day = int(date_parsed[0]),int(date_parsed[1]),int(date_parsed[2])
    hour,minute,second = int(hour_parsed[0]),int(hour_parsed[1]),int(hour_parsed[2])
    if mounth < 1 or mounth > 12 or day < 1 or day > 31 or hour > 24 or minute > 59 or second > 59: return False 
    if mounth < 8:
        if mounth % 2 == 1:
            return True
        if mounth == 2:
            if year % 400 == 0 or (year % 4 == 0 and not year % 100 == 0):
                return day < 30
            return day < 29
        return day < 31
    elif mounth % 2 == 1:
        return day < 31
    return True
    
def parse_str_to_date(string):
        
    class dparse_result:
        
        def __init__(self,date,message):
            self.date = date
            self.message = message
            pass
        
        pass
    
    date_pattern = '\d+-\d+-\d+'
    hour_pattern = '\d+:\d+:\d+'
    date = re.findall(date_pattern,string)
    hour = re.findall(hour_pattern,string)
        
    if not len(date) == 1 or not len(hour) == 1:
        return dparse_result(None,'la cantidad de valores dados no coincide con la esperada')
    if validate_date(date[0],hour[0]):
        return dparse_result(f'{date[0]} {hour[0]}','OK')
    return dparse_result(None,'La fecha dada no es una fecha valida')

def set_date_editor(master):
    
    class date_struct:
        
        def __init__(self,year,mounth,day,hour,minute,second):
            self.year = year
            self.mounth = mounth
            self.day = day
            self.hour = hour
            self.minute = minute
            self.second = second
            pass
        
        pass
    
    DateFrame = Tk.Canvas(master,width=500,height=500,relief='groove',bg=rgb_to_hex(100,100,200))
    DateFrame.pack(side='top')
    
    now = gmtime()
    
    YearValue = Tk.IntVar(DateFrame)
    YearValue.set(now.tm_year)
    
    MounthValue = Tk.IntVar(DateFrame)
    MounthValue.set(now.tm_mon)
    
    DayValue = Tk.IntVar(DateFrame)
    DayValue.set(now.tm_mday)
    
    HourValue=Tk.IntVar(DateFrame)
    HourValue.set(now.tm_hour)
    
    MinuteValue = Tk.IntVar(DateFrame)
    MinuteValue.set(now.tm_min)
    
    SecondValue = Tk.IntVar(DateFrame)
    SecondValue.set(now.tm_sec)
    
    YearLabel = Tk.Label(DateFrame,text='Year',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
    MounthLabel = Tk.Label(DateFrame,text='Mounth',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
    DayLabel = Tk.Label(DateFrame,text='Day',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
    HourLabel = Tk.Label(DateFrame,text='Hour',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
    MinuteLabel = Tk.Label(DateFrame,text='Minute',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
    SecondLabel = Tk.Label(DateFrame,text='Second',font=AUTH_FONT,bg=rgb_to_hex(100,100,200))
    YearEntry = Tk.Spinbox(DateFrame,from_=0,to=3000,increment=1,textvariable=YearValue)
    MounthEntry = Tk.Spinbox(DateFrame,from_=1,to=12,increment=1,textvariable=MounthValue)
    DayEntry = Tk.Spinbox(DateFrame,from_=1,to=31,increment=1,textvariable=DayValue)
    HourEntry = Tk.Spinbox(DateFrame,from_=0,to=24,increment=1,textvariable=HourValue)
    MinuteEntry = Tk.Spinbox(DateFrame,from_=0,to=59,increment=1,textvariable=MinuteValue)
    SecondEntry = Tk.Spinbox(DateFrame,from_=0,to=59,increment=1,textvariable=SecondValue)
    
    YearLabel.grid(row=20,column=15,padx=5,pady=5)
    MounthLabel.grid(row=20,column=115,padx=5,pady=5)
    DayLabel.grid(row=20,column=215,padx=5,pady=5)
    HourLabel.grid(row=20,column=315,padx=5,pady=5)
    MinuteLabel.grid(row=20,column=415,padx=5,pady=5)
    SecondLabel.grid(row=20,column=515,padx=5,pady=5)
    YearEntry.grid(row=30,column=15,padx=5,pady=5)
    MounthEntry.grid(row=30,column=115,padx=5,pady=5)
    DayEntry.grid(row=30,column=215,padx=5,pady=5)
    HourEntry.grid(row=30,column=315,padx=5,pady=5)
    MinuteEntry.grid(row=30,column=415,padx=5,pady=5)
    SecondEntry.grid(row=30,column=515,padx=5,pady=5)
    
    return date_struct(YearValue,MounthValue,DayValue,HourValue,MinuteValue,SecondValue)

def set_description_editor(master):
    DescriptionFrame = Tk.Canvas(master)
    DescriptionFrame.pack(side='top',fill='both',pady=5,padx=5)    
    DescriptionTexbox = Tk.Text(DescriptionFrame,width=1200)
    DescriptionTexbox.pack(side='top')
    return DescriptionTexbox

def set_controls(master,date_struct,description,activity,callback=None,father=None,view=None):
    ControlsFrame = Tk.Canvas(master,bg=rgb_to_hex(100,100,200))
    ControlsFrame.pack(side='bottom')
    
    MSGLabel = Tk.Label(ControlsFrame,text='',bg=rgb_to_hex(100,100,200))
    save_btn = Tk.Button(ControlsFrame,bg=rgb_to_hex(100,100,100),fg='white',text='Save',font=AUTH_FONT,command=lambda : save_activity(date_struct,description,MSGLabel,activity,callback,father,view))
    cancel_btn = Tk.Button(ControlsFrame,bg=rgb_to_hex(100,100,100),fg='white',text='Cancel',font=AUTH_FONT,command=lambda: cancel(master,father))
    
    MSGLabel.grid(row=0,column=10,padx=5,pady=10)
    save_btn.grid(row=10,column=10,padx=15,pady=10)
    cancel_btn.grid(row=10,column=110,padx=15,pady=10)
    pass

class Activity:
    
    def __init__(self,description,date=str(datetime.now())):
        self._description = description
        result = parse_str_to_date(date)
        if result.date:
            self._date = result.date
            pass
        else:
            raise Exception(result.message)
        pass
    
    def _set_date(self,date):
        date = parse_str_to_date(date)
        if date.date:
            self._date = date.date
            return True,''
        return False,date.message
    
    @property
    def description(self):
        return self._description
    
    @property
    def date(self):
        return self._date
    
    def update(self,**kwargs):
        if 'date' in kwargs.keys():
            result,msg = self._set_date(kwargs['date'])
            if not result: return msg
        if 'description' in kwargs.keys():
            self._description = kwargs['description']
            pass
        return 'OK'
    
    pass

class ActivityView(Tk.Toplevel):
    
    def __init__(self,father,activity,callback=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._father = father
        self._callback = callback
        self._center_win()
        self.title('Editar')
        self.config(bg=rgb_to_hex(100,100,200))
        self._date = set_date_editor(self)
        self._description = set_description_editor(self)
        set_controls(self,self._date,self._description,activity,callback,father,self)
        self.protocol('WM_DELETE_WINDOW',lambda : self._close())
        self.mainloop()
        pass
    
    def _center_win(self):
        win_width,win_height = self.winfo_screenwidth(),self.winfo_screenheight()
        width,height = int(size.split('x')[0]),int(size.split('x')[0])
        x,y = win_width // 2 - width // 2,win_height // 2 - height // 2
        self.geometry(f'{size}+{x}+{y}')
        pass
    
    def _close(self):
        if self._father:
            self._father.deiconify()
            pass
        self.destroy()
        pass
    
    pass