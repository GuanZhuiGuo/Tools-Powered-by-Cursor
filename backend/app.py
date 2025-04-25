from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import manim
import numpy as np
import tempfile
import os
from pathlib import Path
import subprocess
import sys
import logging
import shutil
import base64
import json

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# 配置CORS允许所有域的请求
CORS(app, resources={r"/*": {"origins": "*"}})

def render_scene(**kwargs):
    """直接使用命令行方式渲染场景，返回图像文件路径和输出目录"""
    tmp_py_file = None
    output_dir = tempfile.mkdtemp()
    logger.debug(f"输出目录: {output_dir}")

    try:
        # 创建临时Python文件
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False, encoding='utf-8') as tmp:
            tmp_py_file = tmp.name
            raw_function_str = kwargs.get('function_str', '0')
            escaped_function_str = raw_function_str.replace('\\', '\\\\').replace("'", "\\'")
            camera_phi = kwargs.get('camera_phi', 75)
            camera_theta = kwargs.get('camera_theta', 30)
            zoom_level = kwargs.get('zoom_level', 0.7)
            
            scene_code = f"""
from manim import *
import numpy as np

class TempScene(ThreeDScene):
    def construct(self):
        try:
            self.set_camera_orientation(phi={camera_phi}*DEGREES, theta={camera_theta}*DEGREES, zoom={zoom_level})
            axes = ThreeDAxes(x_range=[-4, 4, 1], y_range=[-4, 4, 1], z_range=[-1, 1, 0.5])
            self.add(axes)
            function_str = r'{escaped_function_str}'
            
            # 尝试创建3D曲面函数
            try:
                def func(u, v):
                    x = u
                    y = v
                    z = 0  # 默认值
                    t = x  # 对于2D函数，使用x作为时间变量
                    eval_globals = {{"np": np, "sin": np.sin, "cos": np.cos, "pi": np.pi, "x": x, "y": y, "__builtins__": {{}}}}
                    eval_locals = {{"t": t, "u": u, "v": v}}
                    try:
                        z = eval(function_str, eval_globals, eval_locals)
                    except:
                        z = 0
                    return np.array([x, y, z])
                
                surface = ParametricSurface(
                    func,
                    u_range=[-4, 4, 0.2],
                    v_range=[-4, 4, 0.2],
                    color=BLUE_D,
                    resolution=(30, 30)
                )
                self.add(surface)
                
                # 也创建一个2D曲线作为备用
                curve = ParametricFunction(
                    lambda t: axes.c2p(t, 0, eval(function_str, 
                                               {{"np": np, "sin": np.sin, "cos": np.cos, "pi": np.pi, "__builtins__": {{}}}}, 
                                               {{"t": t, "x": t, "y": 0}})),
                    t_range=[-4, 4, 0.05],
                    color=RED
                )
                self.add(curve)
                
            except Exception as e_eval:
                print(f"Surface creation error: {{e_eval}}")
                # 如果3D失败，尝试创建2D曲线
                try:
                    curve = ParametricFunction(
                        lambda t: axes.c2p(t, 0, eval(function_str, 
                                                   {{"np": np, "sin": np.sin, "cos": np.cos, "pi": np.pi, "__builtins__": {{}}}}, 
                                                   {{"t": t}})),
                        t_range=[-4, 4, 0.05],
                        color=BLUE
                    )
                    self.add(curve)
                except Exception as curve_err:
                    print(f"Curve creation error: {{curve_err}}")
                    
            # 添加坐标标签
            x_label = MathTex("x").next_to(axes.x_axis, RIGHT)
            y_label = MathTex("y").next_to(axes.y_axis, UP)
            z_label = MathTex("z").next_to(axes.z_axis, OUT)
            self.add(x_label, y_label, z_label)
                
            equation = MathTex(f"f(x,y) = {raw_function_str}").scale(0.7).to_corner(UP + LEFT)
            self.add(equation)
        except Exception as scene_e:
             print(f"Error in TempScene.construct: {{scene_e}}")
             error_text = Text(f"Scene Error: {{scene_e}}", color=RED)
             self.add(error_text)

"""
            tmp.write(scene_code)
            logger.debug(f"临时场景文件 {tmp_py_file} 内容:\n{scene_code}")

        cmd = [
            sys.executable, '-m', 'manim',
            '-ql', '--format=png', '--output_file=TempScene',
            '--media_dir', output_dir, '--disable_caching',
            '--progress_bar', 'none',
            tmp_py_file, 'TempScene'
        ]
        logger.debug(f"执行命令: {' '.join(cmd)}")
        logger.debug(f"当前工作目录: {os.getcwd()}")
        logger.debug(f"Python可执行文件: {sys.executable}")
        logger.debug(f"环境变量PATH: {os.environ.get('PATH', '')}")
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            logger.debug(f"命令输出 (stdout): {process.stdout}")
            
            if process.stderr:
                logger.error(f"命令错误 (stderr):\n{process.stderr}")
            if process.returncode != 0:
                logger.error(f"Manim渲染失败，返回码: {process.returncode}")
                return None, output_dir
        except Exception as cmd_err:
            logger.exception(f"执行命令时发生错误: {cmd_err}")
            return None, output_dir

        image_path = Path(output_dir) / 'images' / Path(tmp_py_file).stem / 'TempScene.png'
        logger.debug(f"预期图像路径: {image_path}")
        if image_path.exists():
             logger.info(f"找到图像: {image_path}")
             return str(image_path), output_dir
        else:
            logger.warning(f"精确路径未找到: {image_path}，尝试全局搜索 *.png...")
            found_files = list(Path(output_dir).rglob('*.png'))
            if found_files:
                logger.info(f"通过全局搜索找到图像: {found_files[0]}")
                return str(found_files[0]), output_dir
        logger.error(f"在输出目录中未找到PNG图像: {output_dir}")
        return None, output_dir

    except Exception as e:
        logger.exception(f"渲染函数render_scene中发生错误: {str(e)}")
        return None, output_dir
    finally:
        if tmp_py_file and os.path.exists(tmp_py_file):
            try:
                os.unlink(tmp_py_file)
                logger.debug(f"已删除临时文件: {tmp_py_file}")
            except OSError as e:
                 logger.error(f"无法删除临时python文件 {tmp_py_file}: {e}")

@app.route('/generate_preview', methods=['POST', 'OPTIONS'])
def generate_preview():
    if request.method == 'OPTIONS':
        logger.debug("收到OPTIONS预检请求")
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    logger.debug(f"收到POST请求: {request.headers}")
    logger.debug(f"请求数据 (raw): {request.data}")
    image_path = None
    output_dir_to_clean = None

    try:
        if not request.is_json:
            logger.error("请求不是JSON格式")
            return jsonify({"error": "请求必须是JSON格式"}), 400
        data = request.get_json()
        if data is None:
            logger.error("无法解析JSON数据")
            return jsonify({"error": "无法解析JSON数据"}), 400
        logger.debug(f"解析后的JSON数据: {data}")

        function_str = data.get('function', '0.5 * np.sin(2 * np.pi * t)')
        allowed_chars = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ._+-*/() npisctxy")
        filtered_function_str = "".join(c for c in function_str if c in allowed_chars)
        if not filtered_function_str:
            logger.warning("函数字符串过滤后为空，使用默认值 '0'")
            filtered_function_str = '0'
            
        camera_phi = data.get('camera_phi', 75)
        camera_theta = data.get('camera_theta', 30)
        zoom_level = data.get('zoom_level', 0.7)
        
        logger.info(f"生成预览: 函数='{filtered_function_str}', phi={camera_phi}, theta={camera_theta}, zoom={zoom_level}")

        image_path, output_dir_to_clean = render_scene(
            function_str=filtered_function_str,
            camera_phi=camera_phi,
            camera_theta=camera_theta,
            zoom_level=zoom_level
        )

        if image_path:
            logger.info(f"准备发送图像: {image_path}")
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            response_data = {"status": "success", "image_data": "data:image/png;base64," + encoded_string}
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            logger.error("未能生成或找到图像")
            # 可以考虑返回包含错误信息的JSON
            error_msg = "Manim 未能生成图像。请检查后端日志获取详细信息。"
            # 尝试从日志中提取最后几行错误？（比较复杂）
            return jsonify({"error": error_msg}), 500

    except json.JSONDecodeError as json_err:
        logger.error(f"JSON解码错误: {json_err}")
        return jsonify({"error": f"无效的JSON请求: {json_err}"}), 400
    except Exception as e:
        logger.exception(f"处理请求时发生错误: {str(e)}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500
    finally:
        if output_dir_to_clean and os.path.exists(output_dir_to_clean) and os.path.isdir(output_dir_to_clean):
            try:
                if os.path.basename(output_dir_to_clean).startswith('tmp'):
                    shutil.rmtree(output_dir_to_clean)
                    logger.debug(f"已清理临时目录: {output_dir_to_clean}")
                else:
                    logger.warning(f"跳过清理非预期目录: {output_dir_to_clean}")
            except Exception as e:
                logger.error(f"清理临时目录时出错 {output_dir_to_clean}: {e}")
        elif output_dir_to_clean:
            logger.warning(f"尝试清理的目录不存在或不是目录: {output_dir_to_clean}")

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') 