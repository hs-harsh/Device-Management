import wx
import pandas as pd
from pathlib import Path
from wx.adv import NotificationMessage
from datetime import datetime

# Version - 2
class DepositDeviceForm(wx.Frame):
    def __init__(self, parent, title="Deposit Device", lobby=""):
        # super(DepositDeviceForm, self).__init__(parent, title=title, size=(400, 250))
        super(DepositDeviceForm, self).__init__(parent, title=title, size=(0, 0))  # Set initial size to (0, 0)

        self.lobby = lobby
        self.panel = wx.Panel(self)
        self.device_id_label = wx.StaticText(self.panel, label="Device ID:")
        self.device_id_text = wx.TextCtrl(self.panel)

        self.barcode_button = wx.Button(self.panel, label="Barcode")

        
        self.check_details_button = wx.Button(self.panel, label="Check Issue Details")
        self.user_id_label = wx.StaticText(self.panel, label="Depositer User ID:")
        self.user_id_text = wx.TextCtrl(self.panel)
        self.device_type_label = wx.StaticText(self.panel, label="Device Type:")
        self.device_type_choices = ["", "Walkie-Talkie", "Battery", "Fog Safe Device"]
        self.device_type_dropdown = wx.Choice(self.panel, choices=self.device_type_choices)
        self.defective_label = wx.StaticText(self.panel, label="Defective:")
        self.defective_choices = ["No", "Yes"]
        self.defective_dropdown = wx.Choice(self.panel, choices=self.defective_choices)
        self.deposit_device_button = wx.Button(self.panel, label="Deposit Device")

        self.Bind(wx.EVT_BUTTON, self.on_check_details, self.check_details_button)
        self.Bind(wx.EVT_BUTTON, self.on_deposit_device, self.deposit_device_button)
        # Bind the barcode_button to the on_barcode_scan method
        self.Bind(wx.EVT_BUTTON, self.on_barcode_scan, self.barcode_button)
        

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.device_id_label, 0, wx.ALL, 5)
        self.sizer.Add(self.device_id_text, 0, wx.EXPAND | wx.ALL, 5)

        self.sizer.Add(self.barcode_button, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.check_details_button, 0, wx.ALL, 5)
        self.sizer.Add(self.user_id_label, 0, wx.ALL, 5)
        self.sizer.Add(self.user_id_text, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.device_type_label, 0, wx.ALL, 5)
        self.sizer.Add(self.device_type_dropdown, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.defective_label, 0, wx.ALL, 5)
        self.sizer.Add(self.defective_dropdown, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.deposit_device_button, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(self.sizer)
        self.Centre()
        # After initializing the panel and sizer, set the window size to 50% of the screen size
        screen_width, screen_height = wx.GetDisplaySize()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        self.SetSize((window_width, window_height))

        # Center the window on the screen
        self.Centre()

    def on_check_details(self, event):
        device_id = self.device_id_text.GetValue()

        if device_id:
            # Check if Device ID is present in "Device_Issued_"+str(self.lobby)+".csv"
            issued_log_path = "Device_Issued_"+str(self.lobby)+".csv"

            try:
                issued_log = pd.read_csv(issued_log_path)
            except FileNotFoundError:
                wx.MessageBox("Device not issued. Please issue the device first.", "Error", wx.OK | wx.ICON_ERROR)
                return

            if device_id in issued_log['Device ID'].values:
                # Device issued, show details in a popup
                details = issued_log.loc[issued_log['Device ID'] == device_id].iloc[-1]
                details_text = f"User ID: {details['User ID']}\nDevice Type: {details['Device Type']}\nIssue Time: {details['Issue Time']}"

                # Set the device type in the dropdown
                device_type = details['Device Type']
                if device_type in self.device_type_choices:
                    self.device_type_dropdown.SetStringSelection(device_type)

                wx.MessageBox(details_text, "Issue Details", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("Device not issued. Please issue the device first.", "Error", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("Please enter Device ID to check details!", "Error", wx.OK | wx.ICON_ERROR)


    def on_deposit_device(self, event):
        device_id = self.device_id_text.GetValue()
        user_id = self.user_id_text.GetValue()
        device_type = self.device_type_dropdown.GetStringSelection()
        defective = self.defective_dropdown.GetStringSelection()

        if device_id and user_id and device_type:
            # Create or load the device deposit log file
            deposit_log_path = "Device_Deposit_"+str(self.lobby)+".csv"

            try:
                deposit_log = pd.read_csv(deposit_log_path)
            except FileNotFoundError:
                deposit_log = pd.DataFrame(columns=['Device ID', 'Depositer User ID', 'Device Type', 'Defective', 'Issuer User ID', 'Issued Time', 'Deposit Time'])

            # Get Issuer User ID and Issued Time from issued log
            issued_log_path = "Device_Issued_"+str(self.lobby)+".csv"
            try:
                issued_log = pd.read_csv(issued_log_path)
                issuer_user_id = issued_log.loc[issued_log['Device ID'] == device_id, 'User ID'].iloc[-1]
                issued_time = issued_log.loc[issued_log['Device ID'] == device_id, 'Issue Time'].iloc[-1]
            except FileNotFoundError:
                issuer_user_id = ""
                issued_time = ""

            # Append the new entry along with deposit time, Issuer User ID, Issued Time, and Depositer User ID
            deposit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = pd.DataFrame([[device_id, user_id, device_type, defective, issuer_user_id, issued_time, deposit_time]],
                                      columns=['Device ID', 'Depositer User ID', 'Device Type', 'Defective', 'Issuer User ID', 'Issued Time', 'Deposit Time'])
            deposit_log = pd.concat([deposit_log, new_entry], ignore_index=True)

            # Write to the log file
            deposit_log.to_csv(deposit_log_path, index=False)

            # Remove deposited device entry from issued log
            try:
                issued_log = issued_log[issued_log['Device ID'] != device_id]
                issued_log.to_csv(issued_log_path, index=False)
            except FileNotFoundError:
                pass

            # Show success message
            wx.MessageBox(f"Device Deposited at time {deposit_time}!", "Success", wx.OK | wx.ICON_INFORMATION)

            self.Close()
        else:
            wx.MessageBox("Please enter Device ID, Depositer User ID, and select Device Type!", "Deposit Device Error", wx.OK | wx.ICON_ERROR)

    def on_barcode_scan(self, event):
        # Simulate reading a barcode and setting the value in the Device ID text control
        scanned_barcode = input("Scan a barcode: ")
        self.device_id_text.SetValue(scanned_barcode)


# class IssueDeviceForm(wx.Frame):
#     def __init__(self, parent, title="Issue Device", lobby=""):
#         super(IssueDeviceForm, self).__init__(parent, title=title, size=(400, 200))

#         self.lobby = lobby
#         self.panel = wx.Panel(self)
#         self.user_id_label = wx.StaticText(self.panel, label="User ID:")
#         self.user_id_text = wx.TextCtrl(self.panel)
#         self.device_id_label = wx.StaticText(self.panel, label="Device ID:")
#         self.device_id_text = wx.TextCtrl(self.panel)
#         self.issue_device_button = wx.Button(self.panel, label="Issue Device")

#         self.Bind(wx.EVT_BUTTON, self.on_issue_device, self.issue_device_button)

#         self.sizer = wx.BoxSizer(wx.VERTICAL)
#         self.sizer.Add(self.user_id_label, 0, wx.ALL, 5)
#         self.sizer.Add(self.user_id_text, 0, wx.EXPAND | wx.ALL, 5)
#         self.sizer.Add(self.device_id_label, 0, wx.ALL, 5)
#         self.sizer.Add(self.device_id_text, 0, wx.EXPAND | wx.ALL, 5)
#         self.sizer.Add(self.issue_device_button, 0, wx.ALL, 5)

#         self.panel.SetSizerAndFit(self.sizer)
#         self.Centre()
#         # After initializing the panel and sizer, set the window size to 50% of the screen size
#         screen_width, screen_height = wx.GetDisplaySize()
#         window_width = int(screen_width * 0.5)
#         window_height = int(screen_height * 0.5)
#         self.SetSize((window_width, window_height))

#         # Center the window on the screen
#         self.Centre()

#     def on_issue_device(self, event):
#         user_id = self.user_id_text.GetValue()
#         device_id = self.device_id_text.GetValue()

#         if user_id and device_id:
#             # Check if Device ID is present in "Device_Registered_"+str(self.lobby)+".csv"
#             registered_log_path = "Device_Registered_"+str(self.lobby)+".csv"
#             issued_log_path = "Device_Issued_"+str(self.lobby)+".csv"

#             try:
#                 registered_log = pd.read_csv(registered_log_path)
#             except FileNotFoundError:
#                 wx.MessageBox("Device not registered. Please register the device first.", "Error", wx.OK | wx.ICON_ERROR)
#                 return

#             if device_id not in registered_log['Device ID'].values:
#                 wx.MessageBox("Device not registered. Please register the device first.", "Error", wx.OK | wx.ICON_ERROR)
#                 return

#             # Check if Device ID has not been issued already
#             try:
#                 issued_log = pd.read_csv(issued_log_path)
#             except FileNotFoundError:
#                 issued_log = pd.DataFrame(columns=['User ID', 'Device ID', 'Device Type', 'Issue Time'])

#             if device_id in issued_log['Device ID'].values:
#                 # Device already issued, show error with previous entry details
#                 previous_entry = issued_log.loc[issued_log['Device ID'] == device_id].iloc[-1]
#                 details = f"User ID: {previous_entry['User ID']}\nDevice Type: {previous_entry['Device Type']}\nIssue Time: {previous_entry['Issue Time']}"
#                 wx.MessageBox(f"Device already issued with the following details:\n\n{details}", "Error", wx.OK | wx.ICON_ERROR)
#                 return

#             # Get Device Type from "Device_Registered_"+str(self.lobby)+".csv"
#             device_type = registered_log.loc[registered_log['Device ID'] == device_id, 'Device Type'].values[0]

#             # Create or load the device issued log file
#             try:
#                 issued_log = pd.read_csv(issued_log_path)
#             except FileNotFoundError:
#                 issued_log = pd.DataFrame(columns=['User ID', 'Device ID', 'Device Type', 'Issue Time'])

#             # Append the new entry along with issue time
#             issue_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             new_entry = pd.DataFrame([[user_id, device_id, device_type, issue_time]],
#                                       columns=['User ID', 'Device ID', 'Device Type', 'Issue Time'])
#             issued_log = pd.concat([issued_log, new_entry], ignore_index=True)

#             # Write to the log file
#             issued_log.to_csv(issued_log_path, index=False)

#             # Show success message with details
#             wx.MessageBox(f"Device Issued at time {issue_time}!\n\nDevice Type: {device_type}", "Success", wx.OK | wx.ICON_INFORMATION)

#             self.Close()
#         else:
#             wx.MessageBox("Please enter User ID and Device ID!", "Issue Device Error", wx.OK | wx.ICON_ERROR)

class IssueDeviceForm(wx.Frame):
    def __init__(self, parent, title="Issue Device", lobby=""):
        super(IssueDeviceForm, self).__init__(parent, title=title, size=(400, 200))

        self.lobby = lobby
        self.panel = wx.Panel(self)
        self.user_id_label = wx.StaticText(self.panel, label="User ID:")
        self.user_id_text = wx.TextCtrl(self.panel)
        self.device_id_label = wx.StaticText(self.panel, label="Device ID:")
        self.device_id_text = wx.TextCtrl(self.panel)
        self.barcode_button = wx.Button(self.panel, label="Barcode")

        # Bind the barcode_button to the on_barcode_scan method
        self.Bind(wx.EVT_BUTTON, self.on_barcode_scan, self.barcode_button)

        self.issue_device_button = wx.Button(self.panel, label="Issue Device")
        self.Bind(wx.EVT_BUTTON, self.on_issue_device, self.issue_device_button)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.user_id_label, 0, wx.ALL, 5)
        self.sizer.Add(self.user_id_text, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.device_id_label, 0, wx.ALL, 5)
        self.sizer.Add(self.device_id_text, 0, wx.EXPAND | wx.ALL, 5)
        # self.sizer.Add(self.barcode_button, 0, wx.ALL, 5)
        self.sizer.Add(self.barcode_button, 0, wx.EXPAND | wx.ALL, 5)

        
        self.sizer.Add(self.issue_device_button, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(self.sizer)
        self.Centre()

        screen_width, screen_height = wx.GetDisplaySize()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        self.SetSize((window_width, window_height))
        self.Centre()

    def on_issue_device(self, event):
        user_id = self.user_id_text.GetValue()
        device_id = self.device_id_text.GetValue()

        if user_id and device_id:
            # Check if Device ID is present in "Device_Registered_"+str(self.lobby)+".csv"
            registered_log_path = "Device_Registered_"+str(self.lobby)+".csv"
            issued_log_path = "Device_Issued_"+str(self.lobby)+".csv"

            try:
                registered_log = pd.read_csv(registered_log_path)
            except FileNotFoundError:
                wx.MessageBox("Device not registered. Please register the device first.", "Error", wx.OK | wx.ICON_ERROR)
                return

            if device_id not in registered_log['Device ID'].values:
                wx.MessageBox("Device not registered. Please register the device first.", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Check if Device ID has not been issued already
            try:
                issued_log = pd.read_csv(issued_log_path)
            except FileNotFoundError:
                issued_log = pd.DataFrame(columns=['User ID', 'Device ID', 'Device Type', 'Issue Time'])

            if device_id in issued_log['Device ID'].values:
                # Device already issued, show error with previous entry details
                previous_entry = issued_log.loc[issued_log['Device ID'] == device_id].iloc[-1]
                details = f"User ID: {previous_entry['User ID']}\nDevice Type: {previous_entry['Device Type']}\nIssue Time: {previous_entry['Issue Time']}"
                wx.MessageBox(f"Device already issued with the following details:\n\n{details}", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Get Device Type from "Device_Registered_"+str(self.lobby)+".csv"
            device_type = registered_log.loc[registered_log['Device ID'] == device_id, 'Device Type'].values[0]

            # Create or load the device issued log file
            try:
                issued_log = pd.read_csv(issued_log_path)
            except FileNotFoundError:
                issued_log = pd.DataFrame(columns=['User ID', 'Device ID', 'Device Type', 'Issue Time'])

            # Append the new entry along with issue time
            issue_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = pd.DataFrame([[user_id, device_id, device_type, issue_time]],
                                      columns=['User ID', 'Device ID', 'Device Type', 'Issue Time'])
            issued_log = pd.concat([issued_log, new_entry], ignore_index=True)

            # Write to the log file
            issued_log.to_csv(issued_log_path, index=False)

            # Show success message with details
            wx.MessageBox(f"Device Issued at time {issue_time}!\n\nDevice Type: {device_type}", "Success", wx.OK | wx.ICON_INFORMATION)

            self.Close()
        else:
            wx.MessageBox("Please enter User ID and Device ID!", "Issue Device Error", wx.OK | wx.ICON_ERROR)

    def on_barcode_scan(self, event):
        # Simulate reading a barcode and setting the value in the Device ID text control
        scanned_barcode = input("Scan a barcode: ")
        self.device_id_text.SetValue(scanned_barcode)


# class RegisterDeviceForm(wx.Frame):
#     def __init__(self, parent, title="Register New Device", lobby=""):
#         super(RegisterDeviceForm, self).__init__(parent, title=title, size=(400, 200))


#         self.lobby = lobby
#         self.panel = wx.Panel(self)
#         self.device_id_label = wx.StaticText(self.panel, label="Device ID:")
#         self.device_id_text = wx.TextCtrl(self.panel)
#         self.device_type_label = wx.StaticText(self.panel, label="Device Type:")
#         self.device_type_choices = ["", "Walkie-Talkie", "Battery", "Fog Safe Device"]
#         self.device_type_dropdown = wx.Choice(self.panel, choices=self.device_type_choices)
#         self.register_device_button = wx.Button(self.panel, label="Register Device")

#         self.Bind(wx.EVT_BUTTON, self.on_register_device, self.register_device_button)

#         self.sizer = wx.BoxSizer(wx.VERTICAL)
#         self.sizer.Add(self.device_id_label, 0, wx.ALL, 5)
#         self.sizer.Add(self.device_id_text, 0, wx.EXPAND | wx.ALL, 5)
#         self.sizer.Add(self.device_type_label, 0, wx.ALL, 5)
#         self.sizer.Add(self.device_type_dropdown, 0, wx.EXPAND | wx.ALL, 5)
#         self.sizer.Add(self.register_device_button, 0, wx.ALL, 5)

#         self.panel.SetSizerAndFit(self.sizer)
#         self.Centre()
#         # After initializing the panel and sizer, set the window size to 50% of the screen size
#         screen_width, screen_height = wx.GetDisplaySize()
#         window_width = int(screen_width * 0.5)
#         window_height = int(screen_height * 0.5)
#         self.SetSize((window_width, window_height))

#         # Center the window on the screen
#         self.Centre()

#     def on_register_device(self, event):
#         device_id = self.device_id_text.GetValue()
#         device_type = self.device_type_dropdown.GetStringSelection()

#         if device_id and device_type:
#             # Create or load the device registered log file
#             log_file_path = "Device_Registered_"+str(self.lobby)+".csv"
#             try:
#                 device_log = pd.read_csv(log_file_path)
#             except FileNotFoundError:
#                 device_log = pd.DataFrame(columns=['Device ID', 'Device Type', 'Registration Time'])

#             # Check for duplicate entry
#             duplicate_entry = device_log[(device_log['Device ID'] == device_id) ]
#                                         #  & (device_log['Device Type'] == device_type)]

#             if not duplicate_entry.empty:
#                 # Display details of the duplicate entry
#                 details = f"Device ID: {device_id}\nDevice Type: {device_type}\nRegistration Time: {duplicate_entry['Registration Time'].iloc[0]}"
#                 wx.MessageBox(f"Duplicate entry found:\n\n{details}", "Duplicate Entry", wx.OK | wx.ICON_WARNING)
#             else:
#                 # Append the new entry along with registration time
#                 registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 new_entry = pd.DataFrame([[device_id, device_type, registration_time]],
#                                           columns=['Device ID', 'Device Type', 'Registration Time'])
#                 device_log = pd.concat([device_log, new_entry], ignore_index=True)

#                 # Write to the log file
#                 device_log.to_csv(log_file_path, index=False)

#                 # Show success message
#                 wx.MessageBox("Device Registered!", "Success", wx.OK | wx.ICON_INFORMATION)

#             self.Close()
#         else:
#             wx.MessageBox("Please enter Device ID and select Device Type!", "Registration Error", wx.OK | wx.ICON_ERROR)


class RegisterDeviceForm(wx.Frame):
    def __init__(self, parent, title="Register New Device", lobby=""):
        super(RegisterDeviceForm, self).__init__(parent, title=title, size=(400, 200))

        self.lobby = lobby
        self.panel = wx.Panel(self)
        self.device_id_label = wx.StaticText(self.panel, label="Device ID:")
        self.device_id_text = wx.TextCtrl(self.panel)
        self.barcode_button = wx.Button(self.panel, label="Barcode")
        self.device_type_label = wx.StaticText(self.panel, label="Device Type:")
        self.device_type_choices = ["", "Walkie-Talkie", "Battery", "Fog Safe Device"]
        self.device_type_dropdown = wx.Choice(self.panel, choices=self.device_type_choices)
        self.register_device_button = wx.Button(self.panel, label="Register Device")

        self.Bind(wx.EVT_BUTTON, self.on_register_device, self.register_device_button)
        self.Bind(wx.EVT_BUTTON, self.on_barcode_button, self.barcode_button)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.device_id_label, 0, wx.ALL, 5)
        sizer.Add(self.device_id_text, 0, wx.EXPAND | wx.ALL, 5)

        sizer.Add(self.barcode_button, 0, wx.EXPAND | wx.ALL, 5)  # Added Barcode button horizontally
        sizer.Add(self.device_type_label, 0, wx.ALL, 5)
        sizer.Add(self.device_type_dropdown, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.register_device_button, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(sizer)
        self.Centre()
        screen_width, screen_height = wx.GetDisplaySize()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        self.SetSize((window_width, window_height))
        self.Centre()

    def on_register_device(self, event):
        # The registration logic remains the same as before
        device_id = self.device_id_text.GetValue()
        device_type = self.device_type_dropdown.GetStringSelection()

        if device_id and device_type:
            # Create or load the device registered log file
            log_file_path = "Device_Registered_"+str(self.lobby)+".csv"
            try:
                device_log = pd.read_csv(log_file_path)
            except FileNotFoundError:
                device_log = pd.DataFrame(columns=['Device ID', 'Device Type', 'Registration Time'])

            # Check for duplicate entry
            duplicate_entry = device_log[(device_log['Device ID'] == device_id)]

            if not duplicate_entry.empty:
                details = f"Device ID: {device_id}\nDevice Type: {device_type}\nRegistration Time: {duplicate_entry['Registration Time'].iloc[0]}"
                wx.MessageBox(f"Duplicate entry found:\n\n{details}", "Duplicate Entry", wx.OK | wx.ICON_WARNING)
            else:
                registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry = pd.DataFrame([[device_id, device_type, registration_time]],
                                          columns=['Device ID', 'Device Type', 'Registration Time'])
                device_log = pd.concat([device_log, new_entry], ignore_index=True)
                device_log.to_csv(log_file_path, index=False)
                wx.MessageBox("Device Registered!", "Success", wx.OK | wx.ICON_INFORMATION)

            self.Close()
        else:
            wx.MessageBox("Please enter Device ID and select Device Type!", "Registration Error", wx.OK | wx.ICON_ERROR)

    def on_barcode_button(self, event):
        # Simulate reading a barcode and setting the value in the Device ID text control
        scanned_barcode = input("Scan a barcode: ")
        self.device_id_text.SetValue(scanned_barcode)


class LoginPage(wx.Frame):
    def __init__(self, *args, **kw):
        super(LoginPage, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.username_label = wx.StaticText(self.panel, label="Username:")
        self.username_text = wx.TextCtrl(self.panel)
        self.password_label = wx.StaticText(self.panel, label="Password:")
        self.password_text = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        self.lobby_label = wx.StaticText(self.panel, label="Lobby Name:")
        self.lobby_choices = ["", "Howrah", "Bardhaman", "Rampurhat", "Bandel", "Azimganj", "Katwa", "Pakur"]
        self.lobby_dropdown = wx.Choice(self.panel, choices=self.lobby_choices)

        self.login_button = wx.Button(self.panel, label="Login")

        self.Bind(wx.EVT_BUTTON, self.on_login, self.login_button)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_login, self.password_text)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.username_label, 0, wx.ALL, 5)
        self.sizer.Add(self.username_text, 0, wx.EXPAND|wx.ALL, 5)
        self.sizer.Add(self.password_label, 0, wx.ALL, 5)
        self.sizer.Add(self.password_text, 0, wx.EXPAND|wx.ALL, 5)
        self.sizer.Add(self.lobby_label, 0, wx.ALL, 5)
        self.sizer.Add(self.lobby_dropdown, 0, wx.EXPAND|wx.ALL, 5)
        self.sizer.Add(self.login_button, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(self.sizer)
        # After initializing the panel and sizer, set the window size to 50% of the screen size
        screen_width, screen_height = wx.GetDisplaySize()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        self.SetSize((window_width, window_height))

        # Center the window on the screen
        self.Centre()
        self.Show()

    def on_login(self, event):
        username = self.username_text.GetValue()
        password = self.password_text.GetValue()
        lobby = self.lobby_dropdown.GetStringSelection()

        if username == "aaa" and password == "aaa" and lobby:
            self.Destroy()  # Close login page
            home_title = f"Device Management System - {lobby}"
            HomePage(None, title=home_title, lobby=lobby).Show()
        else:
            wx.MessageBox("Please enter valid credentials and select a lobby name!", "Login Error", wx.OK | wx.ICON_ERROR)

class HomePage(wx.Frame):
    
    def __init__(self, *args, lobby="", **kw):
        super(HomePage, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.register_button = wx.Button(self.panel, label="Register New Device")
        self.issue_button = wx.Button(self.panel, label="Issue Device")
        self.deposit_button = wx.Button(self.panel, label="Deposit Device")
        self.logout_button = wx.Button(self.panel, label="Logout")

        # self.lobby_label = wx.StaticText(self.panel, label=f"Lobby: {lobby}")

        self.lobby_label = lobby

        self.Bind(wx.EVT_BUTTON, self.on_button_click, self.register_button)
        self.Bind(wx.EVT_BUTTON, self.on_button_click, self.issue_button)
        self.Bind(wx.EVT_BUTTON, self.on_button_click, self.deposit_button)
        self.Bind(wx.EVT_BUTTON, self.on_logout, self.logout_button)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.register_button, 0, wx.ALL, 5)
        self.sizer.Add(self.issue_button, 0, wx.ALL, 5)
        self.sizer.Add(self.deposit_button, 0, wx.ALL, 5)

        self.sizer.AddStretchSpacer()  # Add stretchable space to push the logout button to the right
        self.sizer.Add(self.logout_button, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        # After initializing the panel and sizer, set the window size to 50% of the screen size
        screen_width, screen_height = wx.GetDisplaySize()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        self.SetSize((window_width, window_height))

        # Center the window on the screen
        self.Centre()
        self.Show()


    def on_button_click(self, event):
        button_label = event.GetEventObject().GetLabel()
        if button_label == "Register New Device":
            RegisterDeviceForm(self, lobby=self.lobby_label).Show()
        elif button_label == "Issue Device":
            IssueDeviceForm(self, lobby=self.lobby_label).Show()
        elif button_label == "Deposit Device":
            DepositDeviceForm(self, lobby=self.lobby_label).Show()
        else:
            wx.MessageBox(f"Button clicked: {button_label}", "Button Clicked", wx.OK | wx.ICON_INFORMATION)

    def on_logout(self, event):
        self.Destroy()  # Close home page
        LoginPage(None, title='Login Page').Show()

    def on_resize(self, event):
        # Adjust the position of the logout button when the window is resized
        size = self.GetSize()
        self.sizer.Layout()
        self.logout_button.SetPosition((size.width - self.logout_button.GetSize().width - 5, 5))
        event.Skip()

if __name__ == '__main__':
    app = wx.App(False)
    LoginPage(None, title='Login Page')
    app.MainLoop()
