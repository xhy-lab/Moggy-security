import bz2
import hashlib
import os
import re
import secrets
import string
import threading
import time
import winreg

import pefile
import psutil
from plyer import notification


class FileError(Exception):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return ""


class Scan:
    def __init__(self, path: str, language: dict, language_pattern: int) -> None:
        self.sha256path = path
        with open(self.sha256path, "r", encoding='utf8') as f:
            self.sha256 = f.read().split("\n")
            self.sha256 = set(self.sha256)
        self.language = language
        self.language_pattern = language_pattern
        self.api_scan = {
            "CreateProcess": 40,
            "WriteProcessMemory": 50,
            "VirtualProtect": 40,
            "LoadLibrary": 30,
            "RegSetValueEx": 30,
            "CreateRemoteThread": 50,
            "DeleteFile": 30,
            "SetWindowsHookEx": 35,
            "OpenProcessToken": 38,
            "LookupPrivilegeValue": 36,
            "WriteFile": 28,
            "SetFileAttributes": 25,
            "SetPriorityClass": 35,
            "OpenProcess": 40,
            "SetCursorPos": 20,
            "CallNextHookEx": 30,
            "ExitWindowsEx": 45,
            "SetWindowsHookExW": 40,
            "UnhookWindowsHookEx": 30
        }
        self.suspicious_apis = {

            "间谍软件": ["SendInput", "SetWindowsHookEx"],
            "勒索病毒": ["CryptAcquireContext", "CryptReleaseContext", "CryptEncrypt", "CryptDecrypt"],
            "破坏型病毒": ["RegQueryValueEx", "RegSetValueEx", "CreateFile", "WriteFile", "CloseHandle",
                           "MoveFile", "MoveFileEx", "WSAStartup", "WSACleanup", "RegOpenKeyEx", "RegSetValueEx"],
        }
        threading.Thread(target=self.__check_sha256_file, daemon=True).start()

    def __check_sha256_file(self) -> None:
        while 1:
            with open(self.sha256path, "r", encoding='utf8') as f:
                self.sha256 = f.read().split("\n")
                self.sha256 = set(self.sha256)
            time.sleep(0.1)

    def __get_file_sha256(self, file_path) -> str:
        if self.__if_file_if_legal(file_path) is False:
            return "no"

        buffer_size = 1024 * 1024 * 1  # 设置缓冲区大小为1MB，可根据实际情况调整
        binary_data = b""
        a = 0
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(buffer_size)
                if not chunk:
                    break
                binary_data += chunk
                a += 1

        return hashlib.sha256(binary_data).hexdigest()

    def __if_file_if_legal(self, file_path: str) -> bool:
        """
        :param file_path: 检查文件是否可读
        :return: True or False
        """
        try:
            with open(file_path, 'rb') as f:
                f.read()
            return True
        except FileNotFoundError:
            # 文件不存在
            return False
        except PermissionError:
            # 文件无法进行读取
            return False
        except IsADirectoryError:
            # 路径指向为文件
            return False
        except OSError:
            # 系统错误
            return False

    def scan_file(self, file_path: str) -> list or str:
        file_sha256 = self.__get_file_sha256(file_path)
        if file_sha256 == "no":
            return ["pass", ""]
        if file_sha256 in self.sha256:
            return [True, file_sha256]
        else:
            # result = self.heuristic_scan(file_path)
            # if result[0] is True:
            #     return [True, result[1]]
            return [False, ""]

    def is_path_in_folder(self, path, folder):
        try:
            path = os.path.abspath(path)
            folder = os.path.abspath(folder)
        except:
            return False
        return os.path.commonpath([path]) == os.path.commonpath([folder])

    def heuristic_scan(self, file_path):
        if self.is_path_in_folder(file_path, "C:/Windows/System32"):
            print("系统文件跳过")
            return False, None, None
        try:
            file_num = 0
            with pefile.PE(file_path) as pe:
                # 检查文件是否包含导入表
                if pe.DIRECTORY_ENTRY_IMPORT is not None:
                    for entry in pe.DIRECTORY_ENTRY_IMPORT:
                        for imp in entry.imports:
                            for api in self.api_scan:
                                if imp.name is not None and imp.name.decode() == api:
                                    print(api)
                                    file_num += self.api_scan[api]
            if file_num > 100:
                return True, file_num, "delete"

            return False, file_num, None
        except Exception as e:
            return False, None, None


class OsOperation:
    def __init__(self) -> None:
        self.sys_os = os

    def generate_secure_random_string(self, length) -> str:
        hex_digits = string.hexdigits
        secure_random_string = ''.join(secrets.choice(hex_digits) for _ in range(length))
        return secure_random_string

    def sleep_file(self, file: str) -> None:
        while 1:
            try:
                with open(file, 'rb') as f:
                    data = f.read()
                break
            except PermissionError:
                time.sleep(0.1)

    def __clear_file(self, old_path) -> None:
        try:
            self.sleep_file(old_path)
            with open(old_path, 'rb') as f:
                data = f.read()
            name = self.generate_secure_random_string(32)
            with open("./Bin/Isolation/Inf", 'a') as f:
                f.write(name + ":" + old_path + "\n")
            compressed_data = bz2.compress(data)
            with open("./Bin/Isolation/" + name, 'wb') as f:
                f.write(compressed_data)
            self.sys_os.remove(old_path)
        except:
            pass

    def clear_file(self, old_path) -> None:
        threading.Thread(target=self.__clear_file, args=(old_path,)).start()


class ImpactHijackingProtection:
    def __init__(self, language: dict, language_pattern: int) -> None:
        # HKEY_LOCAL_MACHINE\
        self.path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"
        self.value_name = "Debugger"
        self.language = language
        self.language_pattern = language_pattern
        self.stop_event = threading.Event()

    def start(self) -> None:
        self.stop_event = threading.Event()
        threading.Thread(target=self.__start).start()

    def __start(self) -> None:
        while not self.stop_event.is_set():
            time.sleep(0.5)
            threading.Thread(target=self.query).start()

    def stop(self) -> None:
        self.stop_event.set()

    def query(self) -> None:
        all_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.path, 0, winreg.KEY_ALL_ACCESS)
        # 查询子项
        subkeys = []
        try:
            i = 0
            while True:
                subkey = winreg.EnumKey(all_key, i)
                subkeys.append(subkey)
                i += 1
        except WindowsError:
            pass
        notify_str = ""
        # 打印所有子项
        for subkey in subkeys:
            try:
                path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" + "\\" + subkey
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
                value, value_type = winreg.QueryValueEx(key, self.value_name)
                if str(value_type) == "1":
                    try:
                        winreg.DeleteKey(all_key, subkey)
                        notify_str += subkey + " "
                    except Exception as e:
                        print("发生了错误", e)
            except (FileNotFoundError, PermissionError):
                pass

        # 关闭注册表项
        winreg.CloseKey(all_key)
        if len(notify_str) != 0:
            notification.notify(
                title=self.language["regedit_protect"][self.language_pattern],
                message=self.language["regedit_protect_text1"][self.language_pattern] + "\n" + notify_str + "\n" +
                        self.language["regedit_protect_text2"][self.language_pattern],
                timeout=3  # 通知显示的时长，单位为秒
            )


class ScriptProtection:
    def __init__(self, path: str, language: dict, language_pattern: int, window) -> None:
        self.Scan = Scan(path, language, language_pattern)
        self.language = language
        self.language_pattern = language_pattern
        self.Window = window
        self.OsOperation = OsOperation()
        self.previous_processes = set(psutil.process_iter())
        self.stop_event = threading.Event()

    def get_process_info(self, pid):
        try:
            return psutil.Process(pid).cmdline()
        except psutil.NoSuchProcess:
            print("指定的进程不存在。")

    def start(self):
        self.stop_event = threading.Event()
        threading.Thread(target=self.__start, daemon=True).start()

    def stop(self):
        self.stop_event.set()

    def __start(self):
        while not self.stop_event.is_set():
            time.sleep(0.05)
            current_processes = set(psutil.process_iter())
            new_processes = current_processes - self.previous_processes
            for process in new_processes:
                try:
                    # 获取进程信息
                    if process.name() == "cmd.exe":
                        # 示例用法
                        a = self.get_process_info(process.pid)
                        if len(a) > 1 and a[1] == "/c" and os.path.exists(a[2]):
                            process.suspend()
                            dangerous_commands = [
                                r"del ",  # 删除文件命令
                                r"rd ",  # 删除目录命令
                                r"format ",  # 格式化磁盘命令
                                r"reg ",  # 操作注册表命令（可能修改关键配置）
                                r"net user ",  # 修改用户相关设置命令
                                r"takeown ",  # 获取文件或目录所有权命令（可能被恶意使用）
                                r"taskkill ",  # 终止进程命令
                            ]
                            cnp = 0
                            with open(a[2], 'r', encoding='utf-8') as file:
                                content = file.read()
                                for command in dangerous_commands:
                                    if re.search(command, content, re.IGNORECASE):
                                        cnp = 1
                                        notification.notify(
                                            title=self.language["script_defense"][self.language_pattern],
                                            message=self.language["script_defense_text"][self.language_pattern] + a[2],
                                            timeout=3
                                        )
                                        process.kill()
                                        break
                            if cnp == 0:
                                process.resume()
                    elif process.name() == "taskkill.exe":
                        process.kill()
                        notification.notify(
                            title=self.language["script_defense"][self.language_pattern],
                            message=self.language["script_defense_text1"][self.language_pattern],
                            timeout=3
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            self.previous_processes = current_processes


class ProcessProtection:
    def __init__(self, path: str, language: dict, language_pattern: int, window) -> None:
        self.Scan = Scan(path, language, language_pattern)
        self.language = language
        self.language_pattern = language_pattern
        self.Window = window
        self.OsOperation = OsOperation()
        self.previous_processes = set(psutil.process_iter())
        self.stop_event = threading.Event()

    def start(self):
        self.stop_event = threading.Event()
        threading.Thread(target=self.__start, daemon=True).start()

    def stop(self):
        self.stop_event.set()

    def __scan_file(self, proc: psutil.Process):
        try:
            process_path = proc.exe()
            print("父进程%s启动了子进程%s" % (str(proc.parent().name()), proc.name()))
            result = self.Scan.scan_file(process_path)
            if result[0] == "pass":
                return
            elif result[0] is True:
                process_name = proc.name()
                if process_name in ["taskkill.exe", "cmd.exe"]:
                    return
                process_cmd = self.get_process_startup_args(proc.pid)
                if len(process_cmd) <= 1:
                    process_cmd = ""
                else:
                    process_cmd = process_cmd[1:]
                proc.kill()
                threading.Thread(target=self.Window.ProcessInterceptionPrompt,
                                 args=(process_name, process_cmd, process_path,
                                       result[1], "威胁电脑安全", self.OsOperation)).start()
            else:
                try:
                    proc.resume()
                except Exception:
                    pass
        except Exception:
            pass

    def __start(self):
        while not self.stop_event.is_set():
            time.sleep(0.05)
            current_processes = set(psutil.process_iter())
            new_processes = current_processes - self.previous_processes
            for process in new_processes:
                try:
                    process.suspend()
                    threading.Thread(target=self.__scan_file, args=(process,)).start()
                except Exception:
                    continue
            self.previous_processes = current_processes

    def get_process_startup_args(self, pid: int):
        try:
            process = psutil.Process(pid)
            cmdline = process.cmdline()
            return cmdline
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None


class RegeditStartupItem:
    def __init__(self, language: dict, language_pattern: int) -> None:
        self.path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        self.value_name = "MoggySecurity"
        self.language = language
        self.language_pattern = language_pattern
        self.stop_event = threading.Event()
        all_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.path, 0, winreg.KEY_ALL_ACCESS)
        # 查询子项
        self.subkeys = []
        try:
            i = 0
            while True:
                subkey = winreg.EnumKey(all_key, i)
                self.subkeys.append(subkey)
                i += 1
        except WindowsError:
            pass

    def __start(self):
        ...


if __name__ == "__main__":
    a = Scan(r"D:\project\Moggy security V1.0\Bin\Data\FileFeatureSha256", {}, 0)
    # print(a.heuristic_scan(r"D:\病毒样本\《吔屎啦，梁非凡》病毒安装程序.exe"))
    file_path = r"D:\病毒样本\《吔屎啦，梁非凡》病毒安装程序.exe"
    with pefile.PE(file_path) as pe:
        # 检查文件是否包含导入表
        if pe.DIRECTORY_ENTRY_IMPORT is not None:
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                for imp in entry.imports:
                    try:
                        print(imp.name.decode())
                    except AttributeError:
                        continue
