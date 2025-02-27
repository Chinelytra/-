import winreg
import json
import os
import sys
import ctypes
from tkinter import Tk, Button, Label
from tkinter.messagebox import showinfo

def hide_console():
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)

class ProxySwitch:
    def show_error(self, message):
        root = Tk()
        root.withdraw()
        Label(root, text=message).pack()
        root.after(3000, root.destroy)
        root.mainloop()
    
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def __init__(self):
        hide_console()
        self.config = {
            "proxy_server": "127.0.0.1:2334",
            "bypass_list": "localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*;<local>"
        }
        
        try:
            if not self.is_admin():
                ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas", 
                    sys.executable, 
                    f'"{os.path.abspath(sys.argv[0])}"', 
                    os.path.dirname(sys.argv[0]), 
                    1
                )
                sys.exit(0)
            else:
                self.init_gui()
        except Exception as e:
            self.show_error(f"启动失败: {str(e)}")
            sys.exit(1)
    def show_error(self, message):
        try:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            Label(root, text=message, padx=20, pady=10).pack()
            root.after(3000, root.destroy)
            root.mainloop()
        except:
            pass
    def init_gui(self):
        self.root = Tk()
        self.root.title("代理设置")
        self.root.geometry("180x120")
        
        # 设置窗口样式
        self.root.configure(bg='#F0F4F8')  # 修改为淡蓝灰色
        self.root.attributes('-alpha', 0.95)
        
        # 创建主框架
        self.main_frame = Label(self.root, bg='#F0F4F8')  # 修改为淡蓝灰色
        self.main_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # 状态标签
        self.status_label = Label(
            self.main_frame,
            text="当前状态：未知",
            font=('Microsoft YaHei UI', 10, 'bold'),
            bg='#F0F4F8'  # 修改为淡蓝灰色
        )
        self.status_label.pack(pady=15)
        
        # 切换按钮
        self.toggle_button = Button(
            self.main_frame,
            text="切换代理",
            font=('Microsoft YaHei UI', 9, 'bold'),
            width=10,
            relief='raised',  # 改回凸起样式
            bg='#4A90E2',
            fg='white',
            activebackground='#357ABD',
            activeforeground='white',  # 添加按下时的文字颜色
            cursor='hand2'
        )
        self.toggle_button.config(command=self.toggle_proxy)
        self.toggle_button.pack(pady=10)
        
        # 添加拖动功能
        self.main_frame.bind('<Button-1>', self.start_move)
        self.main_frame.bind('<B1-Motion>', self.do_move)
        self.status_label.bind('<Button-1>', self.start_move)
        self.status_label.bind('<B1-Motion>', self.do_move)
        
        # 窗口置顶
        self.root.attributes('-topmost', True)
        
        self.update_status()
    def start_resize(self, event):
        self.root.start_x = event.x
        self.root.start_y = event.y

    def do_resize(self, event):
        # 计算新的窗口大小
        new_width = max(180, self.root.winfo_width() + (event.x - self.root.start_x))
        new_height = max(120, self.root.winfo_height() + (event.y - self.root.start_y))
        self.root.geometry(f"{new_width}x{new_height}")

    def move_to_bottom_right(self):
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算窗口位置
        window_width = 180
        window_height = 120
        x = screen_width - window_width - 20  # 距离右边缘20像素
        y = screen_height - window_height - 40  # 距离底部40像素
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    def update_status(self):
        status = "已开启" if self.get_proxy_status() else "已关闭"
        self.status_label.config(
            text=f"当前状态：{status}",
            fg='#006400' if status == "已开启" else '#FF0000'  # 深绿色和红色
        )
    def set_proxy(self, enable=True):
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
                                    0, winreg.KEY_WRITE)
            
            winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
            if enable:
                winreg.SetValueEx(reg_key, "ProxyServer", 0, winreg.REG_SZ, self.config["proxy_server"])
                winreg.SetValueEx(reg_key, "ProxyOverride", 0, winreg.REG_SZ, self.config["bypass_list"])
            
            winreg.CloseKey(reg_key)
            os.system('ipconfig /flushdns >nul 2>&1')
        except Exception:
            self.show_error("设置代理失败")
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    def get_proxy_status(self):
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
                                    0, winreg.KEY_READ)
            proxy_enable = winreg.QueryValueEx(reg_key, "ProxyEnable")[0]
            winreg.CloseKey(reg_key)
            return bool(proxy_enable)
        except:
            return False
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    def toggle_proxy(self):
        current_status = self.get_proxy_status()
        self.set_proxy(not current_status)
        self.update_status()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProxySwitch()
    app.run()