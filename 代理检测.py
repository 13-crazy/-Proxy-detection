import pystray
from PIL import Image, ImageDraw
import winreg
import requests
import threading
import sys
import os
import shutil


def create_image(color):
    # 创建指定颜色的图片
    image = Image.new('RGB', (64, 64), color)
    return image


def check_proxy():
    # 检查当前系统代理设置
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            return proxy_enable == 1
    except Exception as e:
        print(f"检查代理失败: {e}")
        return False


def toggle_proxy(icon, item):
    # 切换代理设置
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0,
                            winreg.KEY_SET_VALUE) as key:
            current_state = check_proxy()
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0 if current_state else 1)

        update_icon(icon)
    except Exception as e:
        print(f"切换代理失败: {e}")


def update_icon(icon):
    is_proxy = check_proxy()
    icon.icon = create_image("yellow" if is_proxy else "green")

    # 更新菜单项文本
    menu_items = [
        pystray.MenuItem('启用/关闭代理', lambda i, s: toggle_proxy(i, s)),
        pystray.MenuItem('退出', lambda i: stop_program(i))
    ]

    icon.menu = pystray.Menu(*menu_items)


def stop_program(icon):
    icon.stop()
    sys.exit()


def is_proxy_working():
    try:
        # 使用一个可靠的外部服务进行代理检测
        response = requests.get('https://api.ipify.org', timeout=5,
                                proxies={'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'})
        return response.status_code == 200
    except:
        return False


# def setup_startup():
#     # 设置开机自启动
#     try:
#         with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
#                             winreg.KEY_SET_VALUE) as key:
#             winreg.SetValueEx(key, "ProxyMonitor", 0, winreg.REG_SZ, f'"{sys.executable}" "{sys.argv[0]}"')
#     except Exception as e:
#         print(f"设置开机自启动失败: {e}")


def setup_startup():
    # 获取当前用户的启动文件夹路径
    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")

    # 创建快捷方式的目标路径
    shortcut_path = os.path.join(startup_folder, "ProxyMonitor.lnk")

    try:
        # 获取当前脚本或可执行文件的完整路径
        executable_path = sys.argv[0]

        # 如果是 PyInstaller 打包后的环境，使用以下路径
        if getattr(sys, 'frozen', False):
            executable_path = sys.executable

        # 创建快捷方式（如果不存在）
        if not os.path.exists(shortcut_path):
            import pythoncom
            from win32com.client import Dispatch

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = executable_path
            shortcut.WorkingDirectory = os.path.dirname(executable_path)
            shortcut.save()
    except Exception as e:
        print(f"设置开机自启动失败: {e}")


def main():
    # 创建初始图标
    icon = pystray.Icon("proxy_monitor")
    icon.title = "代理监控"

    # 设置初始图像
    icon.icon = create_image("green")

    # 设置菜单
    menu_items = [
        pystray.MenuItem('启用/关闭代理', lambda i, s: toggle_proxy(i, s)),
        pystray.MenuItem('退出', lambda i: stop_program(i))
    ]
    icon.menu = pystray.Menu(*menu_items)

    # 设置开机自启动
    setup_startup()

    # 启动时更新一次图标
    update_icon(icon)

    # 运行图标
    icon.run()


if __name__ == "__main__":
    main()


# pyinstaller --onefile --noconsole 代理检测.py
