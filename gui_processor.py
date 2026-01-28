import os
import cv2
import numpy as np
from PIL import Image
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
# 封装.exe pyinstaller --noconsole --onefile --name "去水印工具_安全版" imgtest/gui_processor.py
class WatermarkRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 批量去水印工具 v2.0")
        self.root.geometry("500x280")
        
        self.label = tk.Label(root, text="请选择包含原图片的文件夹\n(将自动跳过系统敏感目录)", pady=20)
        self.label.pack()

        self.btn_select = tk.Button(root, text="选择文件夹并开始处理", command=self.start_process, bg="#4CAF50", fg="white", padx=20, pady=10)
        self.btn_select.pack()

        self.status_label = tk.Label(root, text="状态: 等待操作", pady=20, fg="blue")
        self.status_label.pack()

    def is_sensitive_path(self, path):
        """排除敏感目录逻辑"""
        path = os.path.normpath(path).lower()
        # 获取系统盘符，通常是 C:
        system_drive = os.environ.get('SystemDrive', 'C:').lower()
        
        # 敏感路径黑名单
        sensitive_folders = [
            system_drive + "\\",               # 磁盘根目录 (如 C:\)
            "c:\\windows",                     # 系统文件夹
            "c:\\program files",               # 程序文件夹
            "c:\\program files (x86)",
            "c:\\users",                       # 用户根目录 (建议选具体子文件夹)
            "c:\\boot",
            "c:\\recovery"
        ]

        # 1. 检查是否直接是黑名单目录
        if path in sensitive_folders:
            return True
        
        # 2. 检查是否在某些系统核心路径下
        for s_path in sensitive_folders:
            if path.startswith(s_path + "\\") and s_path != system_drive + "\\":
                # 如果是 C:\Windows\xxx 等子目录，拦截
                return True
                
        return False

    def start_process(self):
        selected_path = filedialog.askdirectory()
        if not selected_path:
            return

        # 敏感目录检查
        if self.is_sensitive_path(selected_path):
            messagebox.showerror("权限受限", "为了系统安全，请勿选择系统盘根目录、Windows 文件夹或程序安装目录！\n\n请在桌面或非系统盘建立文件夹操作。")
            return

        src_dir = os.path.normpath(selected_path)
        mask_dir = os.path.join(src_dir, "masks")
        out_dir = os.path.join(src_dir, "result")

        self.btn_select.config(state=tk.DISABLED)
        self.status_label.config(text="正在处理中，请勿关闭窗口...")
        self.root.update()

        success_count, fail_count = self.run_workflow(src_dir, mask_dir, out_dir)

        self.btn_select.config(state=tk.NORMAL)
        self.status_label.config(text=f"状态: 处理完毕 (成功:{success_count} 失败:{fail_count})")
        messagebox.showinfo("处理完成", f"任务结束！\n成功: {success_count} 张\n失败: {fail_count} 张")

    def run_workflow(self, src_dir, mask_dir, out_dir):
        # 自动创建与清理
        if os.path.exists(mask_dir):
            shutil.rmtree(mask_dir)
        os.makedirs(mask_dir, exist_ok=True)
        os.makedirs(out_dir, exist_ok=True)

        files = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if not files:
            messagebox.showwarning("提示", "文件夹内没找到图片文件")
            return 0, 0

        # 生成 Mask
        for f in files:
            try:
                img_path = os.path.join(src_dir, f)
                with Image.open(img_path) as img:
                    w, h = img.size
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.rectangle(mask, (int(w*0.83), int(h*0.91)), (int(w*0.99), int(h*0.99)), 255, -1)
                cv2.imwrite(os.path.join(mask_dir, os.path.splitext(f)[0] + ".png"), mask)
            except: continue

        # 调用 IOPaint CLI
        try:
            # 使用 creationflags 隐藏控制台窗口
            subprocess.run(["iopaint", "run", "--model", "lama", "--device", "cpu", 
                            "--image", src_dir, "--mask", mask_dir, "--output", out_dir], 
                            check=True, creationflags=0x08000000) # 0x08000000 是 CREATE_NO_WINDOW
            
            success_count = len(os.listdir(out_dir))
            fail_count = len(files) - success_count
        except:
            success_count, fail_count = 0, len(files)
        finally:
            if os.path.exists(mask_dir):
                shutil.rmtree(mask_dir)

        return success_count, fail_count

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkRemoverGUI(root)
    root.mainloop()