import wx

class BarcodeScannerApp(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(BarcodeScannerApp, self).__init__(*args, **kwargs)

        self.panel = wx.Panel(self)
        self.device_id_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        self.read_barcode_button = wx.Button(self.panel, label="Read Barcode")
        self.read_barcode_button.Bind(wx.EVT_BUTTON, self.on_read_barcode)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.device_id_text, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.read_barcode_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.panel.SetSizerAndFit(sizer)
        self.SetTitle("Barcode Scanner App")
        self.Show()

    def on_read_barcode(self, event):
        scanned_barcode = input("Scan a barcode: ")
        self.device_id_text.SetValue(scanned_barcode)

if __name__ == "__main__":
    app = wx.App(False)
    frame = BarcodeScannerApp(None, size=(300, 150))
    app.MainLoop()
