import os
import string
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from tkinter import ttk

from Bin.Error import *


class HyperLinke(tk.Label):
    def __init__(self, window, text: str, background, old_color, new_color, link, font):
        super().__init__(window, font=font, bg=background, cursor="fleur")
        self.text = text
        self.config(text=text, fg=old_color, cursor="hand2")
        self.old = old_color
        self.new = new_color
        self.bind("<Button - 1>", lambda e: self.open_link(link))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(fg=self.new)

    def on_leave(self, event):
        self.config(fg=self.old)

    def open_link(self, link):
        webbrowser.open_new_tab(link)


class FileLinke(tk.Label):
    def __init__(self, window, text: str, background, old_color, new_color, path, font):
        super().__init__(window, font=font, bg=background, cursor="fleur")
        self.text = text
        self.config(text=text, fg=old_color, cursor="hand2")
        self.old = old_color
        self.new = new_color
        self.bind("<Button - 1>", lambda e: self.open_path(path))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(fg=self.new)

    def on_leave(self, event):
        self.config(fg=self.old)

    def open_path(self, path):
        os.startfile(path)


class OriginalWindow(tk.Tk):
    def __init__(self, width: int, height: int, title: str, is_close=True) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.top = False
        super().__init__()
        self.overrideredirect(True)  # 隐藏系统标题栏
        # 获取屏幕宽度和高度
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # 计算窗口在屏幕中心的位置坐标
        x_position = (screen_width - self.width) // 2
        y_position = (screen_height - self.height) // 2
        self.geometry(f"{self.width}x{self.height}+{x_position}+{y_position}")
        self.x = self.winfo_x()
        self.y = self.winfo_y()
        # 自定义标题栏
        self.title_bar = tk.Frame(self, bg='white', height=25)
        self.title_bar.pack(fill='x')

        self.title_bar.bind('<Button-1>', self.get_point)
        self.title_bar.bind('<B1-Motion>', self.window_move)
        self.title_bar.bind("<ButtonRelease-1>", self.recover_window)

        # 关闭按钮
        style = ttk.Style()
        style.configure("TButton", foreground="black", background="white")
        if is_close:
            self.close_button = ttk.Button(self.title_bar, style="TButton", text='×', width=4, command=self.destroy)
        else:
            self.close_button = ttk.Button(self.title_bar, style="TButton", text='×', width=4, command=self.withdraw)
        self.close_button.pack(side='right')

        # 窗口标题
        label = tk.Label(self.title_bar, text='   ' + title, bg="white")
        label.pack(side='left')

    def recover_window(self, event) -> None:
        """恢复窗口"""
        self.attributes('-alpha', 1)

    def window_move(self, event) -> None:
        """窗口移动事件"""
        new_x = (event.x - self.x) + self.winfo_x()
        new_y = (event.y - self.y) + self.winfo_y()
        s = "%sx%s+%s+%s" % (self.width, self.height, new_x, new_y)
        self.geometry(s)
        self.attributes('-alpha', 0.85)

    def get_point(self, event) -> None:
        """获取当前窗口位置并保存"""
        self.x, self.y = event.x, event.y


class Window(OriginalWindow):
    def __init__(self, width: int, height: int, title: str, function, is_close=True) -> None:
        self.top = False
        super().__init__(width, height, title, is_close)
        # 置顶与取消置顶按钮
        self.top_button = ttk.Button(self.title_bar, style="TButton", text='∨', width=4, command=self.top_window)
        self.top_button.pack(side='right')
        # 关于按钮
        self.about_button = ttk.Button(self.title_bar, style="TButton", text='i', width=4, command=function)
        self.about_button.pack(side='right')

    def top_window(self) -> None:
        if self.top:
            self.wm_attributes('-topmost', 0)
            self.top = False
            self.top_button.config(text='∨')
        else:
            self.wm_attributes('-topmost', 1)
            self.top = True
            self.top_button.config(text='∧')


class Notify(OriginalWindow):
    def __init__(self, title: str, text: str) -> None:
        if len(title) >= 20:
            raise TxtError("标题长度不能超过20")
        if len(text) >= 100:
            raise TxtError("内容长度不能超过100")
        super().__init__(500, 300, title)
        tk.Label(self, text=text, wraplength=450).pack()
        ttk.Button(self, text='确定', command=self.destroy).pack(side='bottom', fill=tk.X)
        self.wm_attributes('-topmost', 1)

    def message(self) -> None:
        self.mainloop()
        self.quit()


class IfNotify(OriginalWindow):
    def __init__(self, title: str, text: str, yes_txt="是", no_txt="否") -> None:
        super().__init__(500, 300, title)
        self.yes_txt = yes_txt
        self.no_txt = no_txt
        self.title = title
        self.text = text
        if len(self.title) >= 20:
            raise TxtError("标题长度不能超过20")
        if len(self.text) >= 100:
            raise TxtError("内容长度不能超过100")
        self.return_txt = None
        self.wm_attributes('-topmost', 1)

    def message(self) -> None:
        def yes():
            self.return_txt = True
            self.destroy()
            self.quit()

        def no():
            self.return_txt = False
            self.destroy()
            self.quit()

        tk.Label(self, text=self.text, wraplength=450).pack()
        ttk.Button(self, text=self.yes_txt, command=yes).place(x=10, y=260, width=230, height=30)
        ttk.Button(self, text=self.no_txt, command=no).place(x=260, y=260, width=230, height=30)
        self.mainloop()
        return self.return_txt



class FileClearWindow(OriginalWindow):
    def __init__(self, width: int, height: int, is_close=True) -> None:
        super().__init__(width, height, "主动防御-文件防御", is_close)
        self.text = tk.Text(self, width=width - 20, height=height - 30)
        self.text.place(x=10, y=10)

    def show_text(self, text: str) -> None:
        # self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, text)
        self.update()
        self.mainloop()


class ProcessInterceptionPrompt(tk.Tk):
    def __init__(self, name, cmd, path, type, describe, sys_class):
        def yes():
            sys_class.clear_file(path)
            self.withdraw()

        def no():
            self.withdraw()

        super().__init__()
        self.width = 600
        self.height = 400
        self.x = self.winfo_screenwidth() // 2 - self.width // 2
        self.y = self.winfo_screenheight() // 2 - self.height // 2
        self.configure(bg="white")
        self.wm_attributes('-topmost', 1)
        self.geometry("%dx%d+%d+%d" % (self.width, self.height, self.x, self.y))
        self.overrideredirect(True)
        self.title_type = tk.Label(self, text="进程防御", font=("仿宋", 22), fg="black", background="white")
        self.title_type.place(x=10, y=10)
        self.title_text = tk.Label(self, text="有危险程序正在启动，建议阻止", font=("仿宋", 18), fg="red",
                                   background="white")
        self.title_text.place(x=10, y=60)
        self.name = tk.Label(self, text="进程名称：%s" % name, font=("仿宋", 16), fg="black", background="white")
        self.name.place(x=10, y=110)
        self.cmd = tk.Label(self, text="启动命令：%s" % cmd, font=("仿宋", 16), fg="black",
                            background="white")
        self.cmd.place(x=10, y=140)
        self.file_path = FileLinke(self, "文件路径：%s" % path, "white", "black", "red",
                                   os.path.dirname(path),
                                   tkfont.Font(family="仿宋", size=16))
        self.file_path.place(x=10, y=170)
        self.file_type = tk.Label(self, text="威胁类型：%s" % type, font=("仿宋", 16), fg="black", background="white")
        self.file_type.place(x=10, y=210)
        self.file_describe = tk.Label(self, text="威胁描述：%s" % describe, font=("仿宋", 16), fg="black",
                                      background="white")
        self.file_describe.place(x=10, y=240)
        ttk.Button(self, text="清除", command=yes).place(x=10, y=280)
        ttk.Button(self, text="忽略", command=no).place(x=100, y=280)
        self.bind('<Button-1>', self.get_point)
        self.bind('<B1-Motion>', self.window_move)
        self.bind("<ButtonRelease-1>", self.recover_window)
        self.mainloop()

    def recover_window(self, event) -> None:
        """恢复窗口"""
        self.attributes('-alpha', 1)

    def window_move(self, event) -> None:
        """窗口移动事件"""
        new_x = (event.x - self.x) + self.winfo_x()
        new_y = (event.y - self.y) + self.winfo_y()
        s = "%sx%s+%s+%s" % (self.width, self.height, new_x, new_y)
        self.geometry(s)
        self.attributes('-alpha', 0.85)

    def get_point(self, event) -> None:
        """获取当前窗口位置并保存"""
        self.x, self.y = event.x, event.y
