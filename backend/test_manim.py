from manim import *
import os
import sys
import tempfile
import subprocess

print(f"当前Python: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")

# 尝试通过API创建场景
print("尝试通过API创建场景...")
try:
    class SimpleScene(Scene):
        def construct(self):
            circle = Circle()
            self.add(circle)
    
    # 不直接渲染，只检查是否能创建场景对象
    scene = SimpleScene()
    print("场景创建成功")
except Exception as e:
    print(f"场景创建失败: {e}")

# 尝试通过命令行运行manim
print("\n尝试通过命令行运行manim...")
try:
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False, encoding='utf-8') as tmp:
        tmp_py_file = tmp.name
        tmp.write("""
from manim import *

class CircleScene(Scene):
    def construct(self):
        circle = Circle()
        self.add(circle)
""")
    
    tmp_dir = tempfile.mkdtemp()
    cmd = [
        sys.executable, '-m', 'manim',
        '-ql', '--format=png',
        '--media_dir', tmp_dir,
        '--progress_bar', 'none',
        tmp_py_file, 'CircleScene'
    ]
    print(f"执行命令: {' '.join(cmd)}")
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    print(f"命令返回码: {process.returncode}")
    print(f"命令输出: {process.stdout}")
    
    if process.stderr:
        print(f"命令错误: {process.stderr}")
    
    # 检查是否生成了图像
    import glob
    images = glob.glob(f"{tmp_dir}/**/*.png", recursive=True)
    if images:
        print(f"找到图像: {images[0]}")
    else:
        print("未找到图像")
    
except Exception as e:
    print(f"命令行测试失败: {e}")

print("\n完成测试") 