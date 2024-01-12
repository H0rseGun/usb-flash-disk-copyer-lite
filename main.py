import pystray
from PIL import Image, ImageDraw
import os
import shutil
import time
import threading
import string
import ctypes
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


# 创建托盘图标
def create_tray_icon():
    icon_image = create_image()
    icon = pystray.Icon("USB Flash Disk Copyer", icon_image, "USB Flash Disk Copyer", menu=pystray.Menu(
        item('退出', on_exit)
    ))
    return icon

if __name__ == "__main__":
    icon = create_tray_icon()
    icon_thread = threading.Thread(target=icon.run)
    drive_thread = threading.Thread(target=check_drives, args=(icon,))

    # 设置守护线程
    drive_thread.daemon = True

    icon_thread.start()
    drive_thread.start()

