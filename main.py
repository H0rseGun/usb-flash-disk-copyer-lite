import pystray
from PIL import Image, ImageDraw, ImageTk
import sys
import os
import shutil
import time
import threading
import string
import ctypes
import tkinter as tk
from pystray import MenuItem as item

# 退出标志
exit_flag = False


# 检测盘符的函数
def get_drive_list():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter + ":\\")
        bitmask >>= 1
    return drives


def copy_files(source_drive, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for root, dirs, files in os.walk(source_drive):
        for file in files:
            source_file = os.path.join(root, file)
            relative_path = os.path.relpath(source_file, source_drive)
            target_file = os.path.join(target_folder, relative_path)
            target_dir = os.path.dirname(target_file)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            shutil.copy(source_file, target_file)


def check_drives(icon):
    global exit_flag
    known_drives = get_drive_list()
    while not exit_flag:
        current_drives = get_drive_list()
        new_drives = [d for d in current_drives if d not in known_drives]

        for drive in new_drives:
            copy_target = 'C:\\copyfiles\\'
            copy_files(drive, copy_target)

        known_drives = current_drives
        time.sleep(10)


def create_image():
    # 创建一个简单的图标
    image = Image.new('RGB', (64, 64), 'black')
    dc = ImageDraw.Draw(image)
    dc.rectangle([32, 0, 64, 32], fill='red')
    return image



def on_exit(icon, item):
    global exit_flag
    exit_flag = True
    icon.stop()
    os._exit(0)

# 创建托盘图标
def create_tray_icon():
    icon_image = create_image()
    icon = pystray.Icon("USB Flash Disk Copyer", icon_image, "USB Flash Disk Copyer", menu=pystray.Menu(
        item('关于', show_about),
        item('退出', on_exit)
    ))
    return icon

# 显示关于窗口
def show_about(icon, item):
    about_window = tk.Toplevel()
    about_window.title("关于")
    about_window.geometry("400x400")

    about_label = tk.Label(about_window, text="USB Flash Disk Copyer\n版本: 1.14.514 Release\n作者: H0rseGun\n开源地址: https://github.com/H0rseGun/usb-flash-disk-copyer-lite")
    about_label.pack()

if __name__ == "__main__":
    icon = create_tray_icon()
    icon_thread = threading.Thread(target=icon.run)
    drive_thread = threading.Thread(target=check_drives, args=(icon,))

    # 设置守护线程
    drive_thread.daemon = True

    icon_thread.start()
    drive_thread.start()

    # 创建 Tkinter 主循环
    root = tk.Tk()
    root.withdraw()
    root.mainloop()
