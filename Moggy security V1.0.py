import hashlib
import queue
import sys
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import configparser
import ctypes
import multiprocessing
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
import pystray
from PIL import ImageTk, Image
from pystray import MenuItem, Menu
import os
from typing import Union
from os import PathLike
import Bin.Engine as Engine
import Bin.Language as Lan
import Bin.Window as Window


def error(type, value, traceback):
    messagebox.showerror("错误", type.__name__ + ": " + str(value))


# 替换系统默认的异常处理函数
sys.excepthook = error

protect_state = {}


def shorten_path(path: Union[str, PathLike[str]], max_length: int = 30) -> str:
    """
    缩短路径，保留盘符和文件名，中间的文件夹路径用 '...' 替换。

    :param path: 原始路径，类型为 str 或 os.PathLike[str]
    :param max_length: 路径的最大长度，默认为 30
    :return: 缩短后的路径
    """
    # 如果路径长度小于等于最大长度，直接返回
    if len(str(path)) <= max_length:
        return str(path)

    # 分离盘符、文件夹路径和文件名
    drive, tail = os.path.splitdrive(str(path))
    dirname, filename = os.path.split(tail)

    # 如果文件名本身已经超过最大长度，直接返回文件名
    if len(filename) >= max_length:
        return filename

    # 计算剩余可用长度
    remaining_length = max_length - len(drive) - len(filename) - len("……") - len(os.sep)

    # 如果剩余长度不足以显示任何文件夹路径，直接返回盘符和文件名
    if remaining_length <= 0:
        return os.path.join(drive, "\\...", filename)

    # 缩短文件夹路径
    shortened_dir = "..."
    for part in dirname.split(os.sep):
        if len(shortened_dir) + len(part) + len(os.sep) <= remaining_length:
            shortened_dir = os.path.join(shortened_dir, part)
        else:
            break

    # 拼接最终路径
    shortened_path = os.path.join(drive, "\\", shortened_dir, filename)
    return shortened_path


class Control:
    def __init__(self, path: str, language: dict, language_pattern: int) -> None:
        self.protect_path = "E:\\"
        self.protect_regedit_DWORD = {""}
        self.path = path
        self.language = language
        self.language_pattern = language_pattern

        self.observer = None

    def file_start(self, qu):
        file_defense = FileDefense(self.path, self.language, self.language_pattern, qu)
        self.observer = Observer()
        self.observer.schedule(file_defense, self.protect_path, recursive=True)
        self.observer.start()

    def file_stop(self):
        self.observer.stop()
        self.observer.join()


class FileDefense(FileSystemEventHandler):
    def __init__(self, path: str, language: dict, language_pattern: int, qu) -> None:
        self.scan = Engine.Scan(path, language, language_pattern)
        self.os_sys = Engine.OsOperation()
        # self.notify = Window.FileClearWindow(600, 400)
        self.qu = qu

    def on_created(self, event) -> None:
        if not event.is_directory:
            try:
                result = self.scan.scan_file(event.src_path)
                print(result)
                if result[0] is True:
                    self.os_sys.clear_file(event.src_path)
                    current_time = datetime.now()
                    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    self.qu.put(
                        [time_string, "文件主动防御", shorten_path(event.src_path) + "创建，引擎返回" + result[1],
                         "已执行清除"])
            except Exception:
                pass


# noinspection PyBroadException
class Main:
    def __init__(self) -> None:
        """
        初始化主程序
        """
        self.combo_box = None
        self.scan_path = None
        self.scam_all_num = 0
        self.scam_all = []
        self.safety_num = 0
        self.danger_num = 0
        self.pass_num = 0
        self.timeing = 0
        self.loop_file = 0
        self.loop = 0
        self.danger_dict = {}
        self.language_values = ["English", "简体中文", "繁體中文"]
        self.if_exit_system = False
        self.language = Lan.language
        # 配置文件读取
        self.OsOperation = Engine.OsOperation()
        self.config = configparser.ConfigParser()
        self.config.read('./Bin/config.ini')
        self.version = self.config.get('Settings', 'version')
        self.language_pattern = int(self.config.get('Settings', 'language_pattern'))
        if self.config.get("Settings", "file_protect") == "1":
            protect_state["file"] = True
        configuration_time = self.config.get('Settings', 'date').split(',')
        self.scan_engine = Engine.Scan("./Bin/Data/FileFeatureSha256", self.language, self.language_pattern)
        self.Control = Control("./Bin/Data/FileFeatureSha256", self.language, self.language_pattern)
        self.image_hijacking = Engine.ImpactHijackingProtection(self.language, self.language_pattern)
        self.ProcessProtection = Engine.ProcessProtection("./Bin/Data/FileFeatureSha256", self.language,
                                                          self.language_pattern, Window)
        self.ScriptProtection = Engine.ScriptProtection("./Bin/Data/FileFeatureSha256", self.language,
                                                        self.language_pattern, Window)
        t = time.localtime()
        year = t.tm_year - int(configuration_time[0])
        month = t.tm_mon - int(configuration_time[1])
        day = t.tm_mday - int(configuration_time[2])
        # 计算天数差
        day_number = year * 365 + month * 30 + day
        if day_number < 0:
            Window.Notify(self.language["error"][self.language_pattern],
                          self.language["error_text_1"][self.language_pattern]).message()
            exit()

        # style = ttk.Style()
        # style.theme_use('clam')
        self.window = Window.Window(900, 500, self.language["name"][self.language_pattern], self.more, False)
        style = ttk.Style(self.window)
        # style.theme_use('xpnative')
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        style.configure('lefttab.TNotebook', tabposition='wn', padding=(10, 10))
        self.notebook = ttk.Notebook(self.window, style='lefttab.TNotebook')
        # 统一文字定义
        self.font_fs_10 = tkfont.Font(family="仿宋", size=10)
        self.font_fs_12 = tkfont.Font(family="仿宋", size=12)
        self.font_fs_15 = tkfont.Font(family="仿宋", size=15)
        self.font_fs_20 = tkfont.Font(family="仿宋", size=20)
        self.font_fs_25 = tkfont.Font(family="仿宋", size=25)
        self.font_fs_30 = tkfont.Font(family="仿宋", size=30)
        # 首页Start
        self.home = tk.Frame(self.notebook, bg="white")
        # 首页图片
        image1 = Image.open(r"./Image/home.png")
        resized_image1 = image1.resize((50, 50))
        self.home_img = ImageTk.PhotoImage(resized_image1)
        self.notebook.add(self.home, image=self.home_img)
        # 首页图标
        image1 = Image.open(r"./Image/software icon.png")
        resized_image1 = image1.resize((50, 50))
        self.home_img1 = ImageTk.PhotoImage(resized_image1)
        tk.Label(self.home, image=str(self.home_img1), bg="white").place(x=10, y=70)
        # 首页欢迎文字
        tk.Label(self.home, text=self.language["home_text_1"][self.language_pattern], font=self.font_fs_25,
                 bg="white").place(x=10, y=10)
        # 首页文字
        tk.Label(self.home, text=self.language["home_text_2"][self.language_pattern], font=self.font_fs_20,
                 bg="white").place(x=70, y=80)
        if self.language_pattern == 0:
            if day_number == 1:
                tk.Label(self.home, text=str(day_number) + " " + self.language["home_text_4"][self.language_pattern],
                         font=self.font_fs_20, bg="white").place(x=10, y=150)
            else:
                tk.Label(self.home, text=str(day_number) + " " + self.language["home_text_5"][self.language_pattern],
                         font=self.font_fs_20, bg="white").place(x=10, y=150)
        else:
            tk.Label(self.home,
                     text=self.language["home_text_3"][self.language_pattern] + str(day_number) + self.language["day"][
                         self.language_pattern], font=self.font_fs_20, bg="white").place(x=10, y=150)
        # 首页End
        # 扫描界面Start
        self.scan = tk.Frame(self.notebook, bg="white")
        # 扫描界面图片
        image1 = Image.open(r"./Image/scan.png")
        resized_image1 = image1.resize((50, 50))
        self.scan_img = ImageTk.PhotoImage(resized_image1)
        self.notebook.add(self.scan, image=self.scan_img)
        # 扫描界面文字
        tk.Label(self.scan, text=self.language["scan_text_1"][self.language_pattern], font=self.font_fs_25,
                 bg="white").place(x=10, y=10)
        # 路径
        self.path = tk.Entry(self.scan, bg="white", state="disabled")
        self.path.place(x=300, y=20, width=400, height=30)

        self.browse = ttk.Button(self.scan, text=self.language["browse"][self.language_pattern],
                                 command=self.browse_path)
        self.browse.place(x=700, y=20, width=100, height=30)

        # 扫描情况
        self.file_sum = tk.Label(self.scan, text=self.language["scan_text_2"][self.language_pattern] + "0",
                                 font=self.font_fs_10,
                                 bg="white")
        self.file_sum.place(x=10, y=60)
        self.threat = tk.Label(self.scan, text=self.language["scan_text_3"][self.language_pattern] + "0",
                               font=self.font_fs_10,
                               bg="white", fg="green")
        self.threat.place(x=10, y=90)
        self.danger = tk.Label(self.scan, text=self.language["scan_text_4"][self.language_pattern] + "0",
                               font=self.font_fs_10,
                               bg="white", fg="red")
        self.danger.place(x=10, y=120)
        self.pass_file = tk.Label(self.scan, text=self.language["scan_text_5"][self.language_pattern] + "0",
                                  font=self.font_fs_10,
                                  bg="white", fg="grey")
        self.pass_file.place(x=10, y=150)
        self.state = tk.Label(self.scan,
                              text=self.language["state"][self.language_pattern] + self.language["state_not_start"][
                                  self.language_pattern],
                              font=self.font_fs_10,
                              bg="white")
        self.state.place(x=10, y=180)
        # 耗时
        self.time = tk.Label(self.scan, text=self.language["time_con"][self.language_pattern] + "0s",
                             font=self.font_fs_10,
                             bg="white")
        self.time.place(x=350, y=60)
        # 速度
        self.speed = tk.Label(self.scan, text=self.language["speed"][self.language_pattern] + "0/s",
                              font=self.font_fs_10,
                              bg="white")
        self.speed.place(x=350, y=90)
        # 开始扫描
        self.start = ttk.Button(self.scan, text=self.language["start"][self.language_pattern], command=self.start_scan)
        self.start.config(state="disabled")
        self.start.place(x=10, y=220, width=100, height=30)
        # 清除威胁
        self.clear = ttk.Button(self.scan, text=self.language["clear"][self.language_pattern],
                                command=self.start_clear_threat)
        self.clear.config(state="disabled")
        self.clear.place(x=10, y=260, width=100, height=30)
        # 结果表格
        self.result = ttk.Treeview(self.scan, columns=("path", "type", "level", "result"), show="headings")
        self.result.heading("path", text=self.language["path"][self.language_pattern])
        self.result.heading("type", text=self.language["type"][self.language_pattern])
        self.result.heading("level", text=self.language["level"][self.language_pattern])
        self.result.heading("result", text=self.language["result"][self.language_pattern])
        self.result.column("path", width=300)
        self.result.column("type", width=80)
        self.result.column("level", width=20)
        self.result.column("result", width=30)
        self.result.place(x=140, y=210, width=640, height=220)
        self.result.bind("<Motion>", lambda event: "break")
        # 滚动条
        self.scroll = ttk.Scrollbar(self.scan, orient="vertical", command=self.result.yview)
        self.scroll.place(x=780, y=210, height=220)
        self.result.configure(yscrollcommand=self.scroll.set)
        # 进度条
        self.progress = ttk.Progressbar(self.scan, orient="horizontal", length=680, mode="determinate")
        self.progress.place(x=350, y=130, width=400, height=10)
        # 扫描情况End
        self.notebook.pack(expand=True, fill='both')
        # 扫描进度文本
        self.scan_text = tk.Label(self.scan, text="", font=self.font_fs_10, bg="white")
        self.scan_text.place(x=350, y=155)
        # 防护界面
        self.protect = tk.Frame(self.notebook, bg="white")
        # 防护界面图片
        image1 = Image.open(r"./Image/protection.png")
        resized_image1 = image1.resize((50, 50))
        self.protect_img = ImageTk.PhotoImage(resized_image1)
        self.notebook.add(self.protect, image=self.protect_img)
        self.qu = queue.Queue()
        threading.Thread(target=self.protect_record_add, args=(self.qu,)).start()
        # 防护界面标题
        tk.Label(self.protect, text=self.language["protect_title"][self.language_pattern], font=self.font_fs_25,
                 bg="white").place(x=10, y=10)
        # 防护界面文字
        tk.Label(self.protect, text=self.language["protect_text"][self.language_pattern], font=self.font_fs_15,
                 bg="white").place(x=10, y=60)

        # 主动防御文字
        tk.Label(self.protect, text=self.language["protect_text_1"][self.language_pattern], font=self.font_fs_20,
                 bg="white").place(x=10, y=100)

        # 文件主动防御开关
        tk.Label(self.protect, text=self.language["file_defense"][self.language_pattern], font=self.font_fs_15,
                 bg="white").place(x=10, y=150)
        self.file_defense = ttk.Button(self.protect, text="", command=self.switch_file_defense, style="Switch.TButton")
        self.file_defense.place(x=200, y=150)
        self.switch_file_defense(114514)
        # 文件主动防御描述
        tk.Label(self.protect, text=self.language["file_defense_text"][self.language_pattern], font=self.font_fs_12,
                 bg="white").place(x=10, y=180)

        # 注册表主动防御开关
        tk.Label(self.protect, text=self.language["registry_defense"][self.language_pattern], font=self.font_fs_15,
                 bg="white").place(x=320, y=150)
        self.registry_defense = ttk.Button(self.protect, text="", command=self.switch_regedit_defense,
                                           style="Switch.TButton")
        self.registry_defense.place(x=510, y=150)
        self.switch_regedit_defense(114514)
        # 注册表主动防御描述
        tk.Label(self.protect, text=self.language["registry_defense_text"][self.language_pattern], font=self.font_fs_12,
                 bg="white").place(x=320, y=180)

        # 进程主动防御开关
        tk.Label(self.protect, text=self.language["process_defense"][self.language_pattern], font=self.font_fs_15,
                 bg="white").place(x=10, y=220)
        self.process_defense = ttk.Button(self.protect, text="", command=self.switch_process_defense,
                                          style="Switch.TButton")
        self.process_defense.place(x=200, y=220)
        self.switch_process_defense(114514)
        # 进程主动防御描述
        tk.Label(self.protect, text=self.language["process_defense_text"][self.language_pattern], font=self.font_fs_12,
                 bg="white").place(x=10, y=250)

        # 脚本主动防御开关
        tk.Label(self.protect, text=self.language["script_defense"][self.language_pattern], font=self.font_fs_15,
                 bg="white").place(x=320, y=220)
        self.script_defense = ttk.Button(self.protect, text="", command=self.switch_script_defense,
                                         style="Switch.TButton")
        self.script_defense.place(x=510, y=220)
        self.switch_script_defense(114514)
        # 脚本主动防御描述
        tk.Label(self.protect, text=self.language["script_defense_text2"][self.language_pattern], font=self.font_fs_12,
                 bg="white").place(x=320, y=250)
        # 主动防御运行日志
        tk.Label(self.protect, text=self.language["protect_record"][self.language_pattern], font=self.font_fs_15,
                 bg="white").place(x=10, y=290)
        self.protect_record = ttk.Treeview(self.protect, columns=("time", "type", "describe", "result"),
                                           show="headings")
        self.protect_record.heading("time", text=self.language["time"][self.language_pattern])
        self.protect_record.heading("type", text=self.language["type"][self.language_pattern])
        self.protect_record.heading("describe", text=self.language["describe"][self.language_pattern])
        self.protect_record.heading("result", text=self.language["result"][self.language_pattern])
        self.protect_record.column("time", width=100)
        self.protect_record.column("type", width=40)
        self.protect_record.column("describe", width=300)
        self.protect_record.column("result", width=50)
        self.protect_record.place(x=15, y=320, width=700, height=110)
        self.protect_record.bind("<Motion>", lambda event: "break")

        # 托盘
        menu = Menu(MenuItem('', action=lambda: self.window.deiconify(), default=True, visible=False),
                    MenuItem(self.language["exit"][self.language_pattern], action=lambda: print(1)))

        image = Image.open(r"./Image/software icon.png")
        self.icon = pystray.Icon("text", image, "", menu)
        self.window.protocol('WM_DELETE_WINDOW', lambda: self.window.withdraw())
        # self.icon.run()
        self.icon_t = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_t.start()
        self.window.mainloop()

    def protect_record_add(self, qu: queue.Queue) -> None:
        while True:
            data = qu.get()  # 从队列中获取数据
            if data == "114514":  # 检查是否收到结束信号
                break

            self.protect_record.insert("", tk.END, values=data)

    def switch_file_defense(self, main=None) -> None:
        """
        切换文件主动防御
        :return: None
        """
        if main is None:
            if protect_state["file"]:
                self.file_defense.config(text=self.language["Closed"][self.language_pattern] + "×")
                self.Control.file_stop()
                protect_state["file"] = False
            else:
                self.file_defense.config(text=self.language["Open"][self.language_pattern] + "√")
                self.Control.file_start(self.qu)
                protect_state["file"] = True
        else:
            self.file_defense.config(text=self.language["Open"][self.language_pattern] + "√")
            self.Control.file_start(self.qu)
            protect_state["file"] = True

    def switch_regedit_defense(self, main=None) -> None:
        """
        切换注册表主动防御
        :return: None
        """
        if main is None:
            if protect_state["registry"]:
                self.registry_defense.config(text=self.language["Closed"][self.language_pattern] + "×")
                self.image_hijacking.stop()
                protect_state["registry"] = False
            else:
                self.registry_defense.config(text=self.language["Open"][self.language_pattern] + "√")
                self.image_hijacking.start()
                protect_state["registry"] = True
        else:
            self.registry_defense.config(text=self.language["Open"][self.language_pattern] + "√")
            self.image_hijacking.start()
            protect_state["registry"] = True

    def switch_process_defense(self, main=None) -> None:
        """
        切换进程主动防御
        :return: None
        """
        if main is None:
            if protect_state["process"]:
                self.process_defense.config(text=self.language["Closed"][self.language_pattern] + "×")
                self.ProcessProtection.stop()
                protect_state["process"] = False
            else:
                self.process_defense.config(text=self.language["Open"][self.language_pattern] + "√")
                self.ProcessProtection.start()
                protect_state["process"] = True
        else:
            self.process_defense.config(text=self.language["Open"][self.language_pattern] + "√")
            self.ProcessProtection.start()
            protect_state["process"] = True

    def switch_script_defense(self, main=None) -> None:
        """
        切换进程主动防御
        :return: None
        """
        if main is None:
            if protect_state["script"]:
                self.script_defense.config(text=self.language["Closed"][self.language_pattern] + "×")
                self.ScriptProtection.stop()
                protect_state["script"] = False
            else:
                self.script_defense.config(text=self.language["Open"][self.language_pattern] + "√")
                self.ScriptProtection.start()
                protect_state["script"] = True
        else:
            self.script_defense.config(text=self.language["Open"][self.language_pattern] + "√")
            self.ScriptProtection.start()
            protect_state["script"] = True

    def start_clear_threat(self) -> None:
        """
        开始清除威胁
        :return: None
        """
        self.create_threads(self.clear_threat)

    def clear_threat(self) -> None:
        """
        清除威胁
        :return: None
        """
        self.clear.config(state="disabled")
        self.start.config(state="disabled")
        self.browse.config(state="disabled")
        self.state.config(text=self.language["clear_ing"][self.language_pattern])
        self.progress["max"] = len(self.danger_dict)
        self.progress["value"] = 0
        for file_path, result in self.danger_dict.items():
            if result[1] == "clear":
                self.OsOperation.clear_file(file_path)
            for row in self.result.get_children():
                item_data = self.result.item(row, "values")
                if len(item_data) > 0 and item_data[0] == file_path:
                    self.result.delete(row)
                    break  # 如果找到并删除了一行，就退出循环
            self.progress["value"] += 1
            self.scan_text.config(text=file_path)
            self.scan_text.update()

        self.scan_text.config(text="")
        self.danger_dict = {}
        self.state.config(text=self.language["clear_finish"][self.language_pattern])
        self.start.config(state="normal")
        self.browse.config(state="normal")

    def start_scan(self) -> None:
        self.create_threads(self.scan_folder, self.scam_all)

    def scan_folder(self, path: list) -> None:
        """
        扫描文件夹
        :param path: 路径
        :return: None
        """
        self.state.config(text=self.language["state_ing"][self.language_pattern] + "，请不要进行移动窗口")
        self.browse.config(state="disabled")
        self.start.config(state="disabled")
        self.progress["value"] = 0
        self.progress["max"] = len(path)
        start_time = time.perf_counter()
        self.loop_file = 0
        self.loop = 0
        for file_path in path:
            start_time1 = time.perf_counter()
            path = Path(file_path)
            parts = list(path.parts)  # 获取路径的各个组成部分，返回一个元组，转换为列表方便操作
            if len(parts) > 4:
                start_parts = parts[:3]
                end_parts = parts[-1:]
                new_parts = start_parts + ["..."] + end_parts
                new_path = Path(*new_parts)  # 通过解包构建新的路径对象
            else:
                new_path = file_path

            self.scan_text.config(text=new_path)
            result = self.scan_engine.scan_file(file_path)
            if result[0] == "pass":
                self.pass_num += 1
                self.pass_file.config(text=self.language["scan_text_5"][self.language_pattern] + str(self.pass_num))
            elif result[0] is True:
                self.danger_num += 1
                self.danger.config(text=self.language["scan_text_4"][self.language_pattern] + str(self.danger_num))
                self.result.insert("", "end",
                                   values=(file_path, result[1], 100, self.language["del"][self.language_pattern]))
                self.danger_dict[file_path] = [file_path, "clear"]
                self.result.yview_moveto(1)
            else:
                self.safety_num += 1
                self.threat.config(text=self.language["scan_text_3"][self.language_pattern] + str(self.safety_num))
            self.progress["value"] += 1
            end_time = time.perf_counter()
            self.timeing = round(end_time - start_time, 2)
            self.loop += round(end_time - start_time1, 2)
            if self.loop >= 1.00:
                self.speed.config(text=self.language["speed"][self.language_pattern] + str(self.loop_file) + "/s")
                self.loop_file = 0
                self.loop = 0
            self.loop_file += 1
            self.time.config(text=self.language["time_con"][self.language_pattern] + str(self.timeing) + "s")
        self.scam_all = []
        self.browse.config(state="normal")
        self.state.config(text=self.language["state_finish"][self.language_pattern])
        self.clear.config(state="normal")
        self.scan_text.config(text="")

    def browse_path(self) -> None:
        path = filedialog.askdirectory()
        if path != "":
            self.path.config(state="normal")
            self.path.delete(0, "end")
            self.path.insert(0, path)
            self.path.config(state="disabled")
            self.scan_path = path
            self.create_threads(self.calculation_file, self.scan_path)

    def create_threads(self, function, *args) -> None:
        thread = threading.Thread(target=function, args=args)
        thread.start()

    def __init_data(self) -> None:
        self.progress["value"] = 0
        self.progress["max"] = 0
        self.scam_all_num = 0
        self.safety_num = 0
        self.danger_num = 0
        self.pass_num = 0
        self.timeing = 0
        self.scam_all = []
        self.loop_file = 0
        self.loop = 0
        self.danger_dict = {}
        self.pass_file.config(text=self.language["scan_text_5"][self.language_pattern] + str(self.pass_num))
        self.danger.config(text=self.language["scan_text_4"][self.language_pattern] + str(self.danger_num))
        self.threat.config(text=self.language["scan_text_3"][self.language_pattern] + str(self.safety_num))
        self.time.config(text=self.language["time_con"][self.language_pattern] + "0s")
        self.speed.config(text=self.language["speed"][self.language_pattern] + "0/s")

    def create_multiprocessing(self, function, *args) -> None:
        process = multiprocessing.Process(target=function, args=args)
        process.start()

    def more(self) -> None:
        root = Window.OriginalWindow(500, 300, self.language["about"][self.language_pattern])
        tk.Label(root, text=self.language["about_text_1"][self.language_pattern], font=self.font_fs_20).place(x=10,
                                                                                                              y=40)
        tk.Label(root, text=self.language["about_text_2"][self.language_pattern] + self.version,
                 font=self.font_fs_20).place(x=10, y=70)
        tk.Label(root, text=self.language["about_text_3"][self.language_pattern] + "一条闲不住的咸鱼",
                 font=self.font_fs_20).place(x=10, y=100)
        Window.HyperLinke(window=root, background="#F0F0F0", font=self.font_fs_20,
                          link="https://space.bilibili.com/1265667148", old_color="black", new_color="blue",
                          text=self.language["about_text_4"][self.language_pattern]).place(x=10, y=130)
        # 修改语言
        self.combo_box = ttk.Combobox(root, background="#F0F0F0")
        self.combo_box.config(background='#F0F0F0')
        # 添加黑名单
        self.black_list = ttk.Button(root, text=self.language["black_list"][self.language_pattern],
                                     command=self.add_black)
        self.black_list.place(x=10, y=170)
        # 设置下拉框的可选值列表
        self.combo_box['values'] = self.language_values
        self.combo_box['state'] = 'readonly'
        self.combo_box.set(self.language_values[self.language_pattern])
        self.combo_box.pack()
        self.combo_box.bind("<<ComboboxSelected>>", self.change_language)
        root.mainloop()

    def add_black(self) -> None:
        path = filedialog.askopenfilename()
        if path:
            try:
                with open(path, "rb") as f:
                    sha256 = hashlib.sha256(f.read()).hexdigest()
                with open('./Bin/Data/FileFeatureSha256', 'a') as f:
                    f.write(sha256 + '\n')
                Window.Notify(self.language["hint"][self.language_pattern],
                              self.language["hint_text_2"][self.language_pattern]).message()
            except Exception as e:
                messagebox.showerror(self.language["error"][self.language_pattern], str(e))

    def change_language(self, event) -> None:
        new_value = self.language_values.index(self.combo_box.get())
        text = f"[Settings]\nlanguage_pattern = {new_value}\nversion = 1.0\ndate = 2024,11,22\nfile_protect = 1\nprocess_protect = 0"
        with open('./Bin/config.ini', 'w') as c:
            c.write(text)
        Window.Notify(self.language["hint"][self.language_pattern],
                      self.language["hint_text_1"][self.language_pattern]).message()

    def calculation_file(self, path: str) -> None:
        self.__init_data()
        self.browse.config(state="disabled")
        self.start.config(state="disabled")
        self.file_sum.config(
            text=self.language["scan_text_2"][self.language_pattern] + "0")
        self.state.config(
            text=self.language["state"][self.language_pattern] + self.language["state_calculation_file"][
                self.language_pattern])
        num = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file).replace("/", "\\")
                self.scam_all.append(file_path)
                num += 1
                self.file_sum.config(text=self.language["scan_text_2"][self.language_pattern] + str(num))
        self.scam_all_num = num
        self.state.config(
            text=self.language["state"][self.language_pattern] + self.language["state_calculation_finish"][
                self.language_pattern])
        self.file_sum.config(text=self.language["scan_text_2"][self.language_pattern] + str(self.scam_all_num))
        self.browse.config(state="normal")
        self.start.config(state="normal")

    def try_run_function(self, function, *args) -> None:
        try:
            function(args)
        except:
            return


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


if __name__ == '__main__':
    # 自定义全局异常处理函数
    if is_admin():
        Main()
    else:
        # 以管理员权限重新运行程序
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

#
#                                _ooOoo_
#                               o8888888o
#                               88" . "88
#                               (| -_- |)
#                               O\  =  /O
#                            ____/`---'\____
#                          .'  \\|     |//  `.
#                         /  \\|||  :  |||//  \
#                        /  _||||| -:- |||||-  \
#                        |   | \\\  -  /// |   |
#                        | \_|  ''\---/''  |   |
#                        \  .-\__  `-`  ___/-. /
#                      ___`. .'  /--.--\  `. . __
#                   ."" '<  `.___\_<|>_/___.'  >'"".
#                  | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#                  \  \ `-.   \_ __\ /__ _/   .-` /  /
#             ======`-.____`-.___\_____/___.-`____.-'======
#                                `=---='
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                        佛祖保佑        永无BUG
#               佛曰:
#                      写字楼里写字间，写字间里程序员；
#                      程序人员写程序，又拿程序换酒钱。
#                      酒醒只在网上坐，酒醉还来网下眠；
#                      酒醉酒醒日复日，网上网下年复年。
#                      但愿老死电脑间，不愿鞠躬老板前；
#                      奔驰宝马贵者趣，公交自行程序员。
#                      别人笑我忒疯癫，我笑自己命太贱；
#                      不见满街漂亮妹，哪个归得程序员？
