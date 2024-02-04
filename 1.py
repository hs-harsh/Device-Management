import wx
import cv2
import qrcode
import numpy as np

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)

        self.text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL)

        self.qr_button = wx.Button(self.panel, label="Read QR Code")
        self.qr_button.Bind(wx.EVT_BUTTON, self.on_read_qr_code)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.text_ctrl, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.qr_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.panel.SetSizerAndFit(sizer)
        self.Show()

    def on_read_qr_code(self, event):
        # Open the camera for video capture
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()

            # Convert the captured image to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Use OpenCV's QRCodeDetector to detect QR codes
            qr_code_detector = cv2.QRCodeDetector()
            decoded_objects = qr_code_detector.detectAndDecodeMulti(gray_frame)

            if decoded_objects is not None and len(decoded_objects) > 0:
                value = decoded_objects[0]

                # Crop the region containing the QR code
                qr_code_rect = qr_code_detector.rectPoints
                if qr_code_rect is not None:
                    qr_code_rect = qr_code_rect.astype(np.int32)
                    min_x, min_y = np.min(qr_code_rect, axis=0)
                    max_x, max_y = np.max(qr_code_rect, axis=0)
                    cropped_qr_code = gray_frame[min_y:max_y, min_x:max_x]

                    # Save the captured and processed QR code images
                    captured_image_path = self.save_image(frame, "captured_image.png")
                    processed_image_path = self.save_image(cropped_qr_code, "processed_image.png")

                    # Show a pop-up with both images and QR code value
                    self.show_popup(captured_image_path, processed_image_path, value)

                    self.text_ctrl.SetValue(value)

                break  # Stop processing frames after detecting a QR code

            wx.Yield()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def save_image(self, image, filename):
        # Save the image
        image_path = filename
        cv2.imwrite(image_path, image)
        return image_path

    def show_popup(self, captured_image_path, processed_image_path, qr_code_value):
        dlg = wx.Dialog(self, title="Detected QR Code", size=(800, 400))
        panel = wx.Panel(dlg)

        # Load the saved captured image
        captured_image = wx.Image(captured_image_path, wx.BITMAP_TYPE_ANY)
        captured_bitmap = wx.StaticBitmap(panel, -1, wx.Bitmap(captured_image), (0, 0), (captured_image.GetWidth(), captured_image.GetHeight()))

        # Load the saved processed image
        processed_image = wx.Image(processed_image_path, wx.BITMAP_TYPE_ANY)
        processed_bitmap = wx.StaticBitmap(panel, -1, wx.Bitmap(processed_image), (captured_image.GetWidth(), 0), (processed_image.GetWidth(), processed_image.GetHeight()))

        # Display QR code value
        qr_code_label = wx.StaticText(panel, label=f"QR Code Value: {qr_code_value}")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(captured_bitmap, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(processed_bitmap, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(qr_code_label, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizerAndFit(sizer)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, title="QR Code Reader App", size=(600, 300))
    app.MainLoop()
