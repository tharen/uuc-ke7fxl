import venster.ce as vce
import venster.layout as vl

class MyWindow(vce.CeMainWindow):
    _window_title=u'VCE Test'
    BTN1ID = 1001
    BTN2ID = 1002
    
    @msg_handler(vce.WM_CREATE)
    def OnCreate(self, event):
        self.label=vce.Static(u'My Label',parent=self)
        
        LABELH = -20
        
        self.sizer=vce.BoxSizer(vce.VERTICAL, border=(2,2,2,2))
        sizer1 = vce.BoxSizer(vce.VERTICAL)
        sizer1.append(self.label)
        self.sizer.append(sizer1)
        CeMainWindow.OnCreate(self, event)
    
def main() :
    w = MyWindow()
    app = vce.Application()
    app.Run()
   
if __name__ == '__main__' :
    main()