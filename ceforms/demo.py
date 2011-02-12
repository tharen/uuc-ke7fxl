#!/usr/bin/python

import ceforms
import Tkinter as tk
import tkFont

class MyApp(ceforms.CEFormApp):
    def __init__(self):
        ceforms.CEFormApp.__init__(
                self,
                'Demo App',
                False)
        frame=tk.Frame(self.winFrame)
        frame.grid(sticky='new')
        frame.grid_columnconfigure(0,weight=1)
        self.font=tkFont.Font(family='tahoma',size=10)
        #ent1=LabelEntry(frame,'date',str,'Date:')
        #ent1.grid(row=0,column=0,sticky='new')
        self.fields={}
        
        self.fields['date'] = \
                FormField('date',
                'text','Date:',
                order=0,
                font=self.font
                )
        self.fields['odometer'] = \
                FormField('odometer',
                'text','Odometer:',
                order=1,
                font=self.font
                )
        self.fields['gallons'] = \
                FormField('gallons',
                'text','Gallons:',
                order=2,
                font=self.font
                )
        self.fields['cost'] = \
                FormField('cost',
                'text','Cost:',
                order=3,
                font=self.font
                )
        self.fields['station'] = \
                FormField('station',
                'text','Station:',
                order=4,
                font=self.font
                )
        self.fields['comment'] = \
                FormField('comment',
                'text','Comment:',
                order=5,
                font=self.font,
                multiline=2,
                layout='stacked'
                )
        
        for k,v in self.fields.items():
            v.grid(frame)


class DataField(tk.Frame):
    def __init__(self,parent,
            label='',):
        tk.Frame.__init__(self,parent)
        
class FormField:
    def __init__(self,fieldName,
            dataType,label=None,
            format=None,order=0,
            required=True,
            multiline=False,
            font=None,
            layout='horizontal'
            ):
        self.fieldName=fieldName
        self.dataType=dataType
        self.label=label
        self.format=format
        self.order=order
        self.required=required
        self.multiline=multiline
        self.font=font
        self.layout=layout
        
        self.value=''
        self._variable=tk.StringVar()
        self._variable.trace('w',
                self._validate)
        
        self.visible=False
        
    def grid(self,parent):
        fr=tk.Frame(parent)
        fr.grid(row=self.order,
                padx=2,pady=2,
                sticky='new',
                columnspan=2)
        fr.rowconfigure(0,weight=1)
        fr.columnconfigure(1,weight=1)

        self._lbl=tk.Label(fr,
                text=self.label,
                font=self.font)
        self._lbl.grid(row=0,column=0,
                sticky='nw')
        
        if self.layout=='stacked':
            r=1
            c=0
        else:
            r=0
            c=1
            
        if self.dataType=='text':
            if not self.multiline:
                ent=tk.Entry(fr,
                        textvariable=self._variable,
                        font=self.font)
                ent.grid(row=r,
                        column=c,
                        sticky='new')
            else:
                txt=tk.Text(fr,
                        height=self.multiline,
                        font=self.font)
                def updateVar(*args):
                    self._variable.set(txt.get(1.0,tk.END))
                txt.bind('<FocusOut>',
                        updateVar)
                txt.grid(row=r,
                        column=c,
                        sticky='new')
                        
        self.visible=True
        
    def _validate(self,*args,**kargs):
        if self.dataType=='text':
            self.value=str(self._variable.get())

    def labelWidth(self,chars=None):
        if not self.visible:
            return False
        if chars==None:
            w=self._lbl.cget('width')
            return w
        else:
            self._lbl.configure(
                    width=chars)
            return True
        

class LabelEntry(tk.Frame):
    def __init__(self,parent,fieldName,dataType,label,*args,**kargs):
        """
        Labelled validating entry widget
        """
        tk.Frame.__init__(
                self,parent,
                pady=2
                )
        self.font=tkFont.Font(family='tahoma',size=10)
        self.parent=parent
        self.fieldName=fieldName
        self.dataType=dataType
        self.label=label
        self.__value=None
        self.__variable=tk.StringVar()
        self.__variable.set(None)
        self.__variable.trace('w',
                self.__callback)
        self._label=tk.Label(
                self,text=label,
                font=self.font,
                )
        self._entry=tk.Entry(
                self,
                textvariable=self.__variable,
                font=self.font,
                )
        
        self._label.grid(
                row=0,column=0,
                sticky='nsew',
                )
        self._entry.grid(
                row=0,column=1,
                sticky='nsew'
                )
        self.grid_columnconfigure(
                1,weight=1)
        
    def __callback(self,*args):
        """Validation callback"""
        value=self.__variable.get()
        new_value=self.validate(value)
        if new_value == None:
            self.__variable.set(self.__value)
        elif new_value != value:
            self.__value = new_value
            self.__variable.set(new_value)
        else:
            self.__value=value

    def validate(self,value):
        """
        Return the value if valid
        None if not
        """
        print 'validating entry'
        return value
    
            
app=MyApp()
app.mainloop()
