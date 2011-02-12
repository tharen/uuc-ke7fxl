import os
import Tkinter as tk
import tkFont

import dialogs


class EntryField(tk.Entry):
    def __init__(self
            ,master
            ,fieldName=None
            ,alias=None
            ,variable=None
            ,dataType=None
            ,*args
            ,**kargs
            ):
        
        tk.Entry.__init__(self
                ,master
                ,textvariable=variable
                #,font=entryFont
                ,*args
                ,**kargs
                )
        
        self.fieldName=fieldName
        self.alias=alias
        self.dataType=dataType
        self._value=variable

        self.bind('<Button-1>'
                ,self.edit
                )

    def edit(self,e):
        v=self._value.get()
        if self.dataType=='integer':
            d=dialogs.Numpad(
                    self
                    ,v
                    ,self.alias
                    )
            d.show()
        elif self.dataType=='date':
            d=dialogs.Datepad(
                    self
                    ,v
                    ,self.alias
                    )
            d.show()
        
        else:
            return
        
        if d.result:
            self._value.set(d.result)
            
class DataGrid(tk.Frame):
    def __init__(self
            ,master
            #name,alias,
            ,dataFields=()
            ,*args
            ,**kargs
            ):
        tk.Frame.__init__(self
                ,master
                ,*args
                ,**kargs
                )
    
        self.master=master
        self.dataFields=dataFields
   
        self.font=tkFont.Font(
                family='system'
                ,size=12
                #,weight=tkFont.BOLD
                )
        
        self.master.rowconfigure(0
                ,weight=1
                )
        self.master.columnconfigure(
                0
                ,weight=1
                )
        self.grid(sticky='nsew')
        self.rowconfigure(20,weight=1)
        self.columnconfigure(1
                ,weight=1)
    
        self._formFields={}
        self._dataVars={}
    
        r=0
        for name,alias,dataType in self.dataFields:
            var=tk.StringVar()
            fld=EntryField(self
                ,name
                ,alias
                ,var
                ,dataType
                ,font=self.font
                )
            lbl=tk.Label(self
                ,text=alias
                )
            self._dataVars[name]=var
            self._formFields[name]=fld
            lbl.grid(row=r
                ,column=0
                )
            fld.grid(row=r
                ,column=1
                ,sticky='new'
                )
            r+=1

class DataForm(tk.Toplevel):
    def __init__(self
            ,master
            ,connString=''
            ,selectSql=''
            ,dbModule='sqlite3'
            ,fields=()
            ):
        tk.Toplevel.__init__(self
                ,master)
        self.master=master
        self.dbModule=dbModule
        self.selectSql=selectSql
        self.connString=connString
        self.fields=fields
        
        self.db=__import__(
                self.dbModule
                )

        conn=self.db.connect(
                self.connString
                )
        cur=conn.cursor()
        cur.execute(self.selectSql)
        

if __name__=='__main__':
    root = tk.Tk()
    flds=(
          ('fld1','Integer 1','integer')
          ,('fld2','Date 2','date')
          ,('fld3','Field 3','string')
          ,('fld4','Field 4','string')
          ,('fld5','Field 5','string')
          ,('fld6','Field 6','string')
          )
    df=DataGrid(root,flds)
    root.mainloop()
