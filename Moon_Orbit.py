import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import tkinter as tk
from tkinter import ttk, messagebox
import platform

# ==========================================
# --- 核心修复：跨平台中文字体设置 ---
# ==========================================
def configure_chinese_font():
    """
    尝试自动配置跨平台的中文字体显示。
    Matplotlib 会依次尝试列表中的字体，直到找到可用的为止。
    """
    system_name = platform.system()
    
    # 常用中文字体列表，涵盖 Windows, macOS, Linux
    font_list = [
        'Microsoft YaHei',    # Windows 微软雅黑
        'SimHei',             # Windows 中易黑体
        'Arial Unicode MS',   # macOS/Windows 通用
        'PingFang HK',        # macOS 苹方
        'Heiti TC',           # macOS 黑体
        'WenQuanYi Micro Hei',# Linux 文泉驿微米黑
        'Droid Sans Fallback',# Linux/Android
        'sans-serif'          # 最后作为保底
    ]
    
    # 将这些字体添加到 Matplotlib 的首选字体序列中
    plt.rcParams['font.sans-serif'] = font_list + plt.rcParams['font.sans-serif']
    
    # 解决负号 '-' 显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 可选：打印当前使用的首选字体帮助调试（在控制台查看）
    # print(f"当前系统: {system_name}, Matplotlib 首选字体序列: {plt.rcParams['font.sans-serif'][:3]}...")

# 在程序启动时立即执行字体配置
configure_chinese_font()
# ==========================================


def calculate_and_plot(entries):
    try:
        # 从输入框获取值
        vals = {name: float(entry.get()) for name, entry in entries.items()}
        
        AU = vals['AU']
        EM_DIST = vals['EM_DIST']
        YEAR_DAYS = vals['YEAR']
        MONTH_DAYS = vals['MONTH']
        SCALE = vals['SCALE']
        
        # --- 计算逻辑 ---
        # 增加点数以获得更平滑的曲线
        t = np.linspace(0, YEAR_DAYS, 10000) 
        omega_e = 2 * np.pi / YEAR_DAYS
        omega_m = 2 * np.pi / MONTH_DAYS

        # 地球坐标
        xe = AU * np.cos(omega_e * t)
        ye = AU * np.sin(omega_e * t)

        # 月球绝对坐标 (包含视觉缩放)
        xm = xe + (EM_DIST * SCALE) * np.cos(omega_m * t)
        ym = ye + (EM_DIST * SCALE) * np.sin(omega_m * t)

        # --- 绘图 ---
        # 使用面向对象的方式创建图表，控制更精确
        fig, ax = plt.subplots(figsize=(10, 10))
        
        ax.plot(0, 0, 'ro', markersize=12, label='太阳 (Sun)')
        ax.plot(xe, ye, 'b--', alpha=0.4, linewidth=1, label='地球公转轨道')
        # 月球轨迹使用更细的线
        ax.plot(xm, ym, 'g-', linewidth=0.8, alpha=0.9, label=f'月球运行轨迹 (缩放: {int(SCALE)}x)')
        
        ax.set_aspect('equal')
        # 确保标题和标签使用中文
        ax.set_title(f"太阳参考系下的月球运动轨迹 (模拟: {YEAR_DAYS}天)", fontsize=14, pad=20)
        ax.set_xlabel("距离 (km)", fontsize=12)
        ax.set_ylabel("距离 (km)", fontsize=12)
        
        # 设置图例字体大小，防止过大
        ax.legend(loc='upper right', fontsize=10)
        
        ax.grid(True, linestyle=':', alpha=0.6)
        
        # 调整布局防止文字被遮挡
        plt.tight_layout() 
        plt.show()

    except ValueError:
        messagebox.showerror("输入错误", "请确保所有输入项都是有效的数字！")

def create_gui():
    root = tk.Tk()
    root.title("天体轨道模拟器 - 参数设置")
    
    # 设置窗口最小尺寸
    root.minsize(400, 350)
    
    main_frame = ttk.Frame(root, padding="25 25 25 25")
    main_frame.pack(expand=True, fill=tk.BOTH)

    # 定义配置项
    config_items = [
        ("日地平均距离 (km):", "AU", "149600000"),
        ("地月平均距离 (km):", "EM_DIST", "384400"),
        ("地球公转周期 (天):", "YEAR", "365.25"),
        ("月球公转周期 (天):", "MONTH", "27.32"),
        ("月球轨迹放大倍数:", "SCALE", "50")
    ]

    entries = {}

    # 增加标题样式
    heading_style = ttk.Style()
    heading_style.configure("Heading.TLabel", font=('Helvetica', 12, 'bold'))
    ttk.Label(main_frame, text="轨道参数配置", style="Heading.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # 循环创建标签和输入框
    for i, (label_text, key, default) in enumerate(config_items):
        row_idx = i + 1
        ttk.Label(main_frame, text=label_text, font=('Helvetica', 10)).grid(row=row_idx, column=0, sticky=tk.W, pady=8)
        entry = ttk.Entry(main_frame, width=18, font=('Helvetica', 10))
        entry.insert(0, default)
        entry.grid(row=row_idx, column=1, sticky=tk.E, pady=8, padx=(15, 0))
        entries[key] = entry

    # 按钮样式
    btn_style = ttk.Style()
    btn_style.configure("Action.TButton", font=('Helvetica', 11, 'bold'), padding=10)
    
    btn_plot = ttk.Button(
        main_frame, 
        text="生成高精度轨迹图", 
        style="Action.TButton",
        command=lambda: calculate_and_plot(entries),
        cursor="hand2"
    )
    btn_plot.grid(row=len(config_items)+2, column=0, columnspan=2, pady=(30, 10), sticky=tk.EW)

    # 提示信息
    ttk.Label(main_frame, text="* 提示：将放大倍数设为 1 可查看真实比例（几乎与地球轨道重合）", 
              font=('Helvetica', 9, 'italic'), foreground="gray").grid(row=len(config_items)+3, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    create_gui()