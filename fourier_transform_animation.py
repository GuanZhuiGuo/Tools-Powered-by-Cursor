from manim import *
import numpy as np

# 配置Manim
config.disable_caching = False  # 启用缓存以提高性能
config.media_width = "1280px"  # 降低分辨率以提高渲染速度
config.frame_rate = 30  # 降低帧率以减少计算量
config.tex_template = TexTemplate()
config.tex_template.add_to_preamble(r"\usepackage{ctex}")


class FourierTransform3DScene(ThreeDScene):
    def construct(self):
        # 设置相机初始位置
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES, zoom=0.7)
        
        # 创建3D坐标系 - 减少数字标签的数量
        axes = ThreeDAxes(
            x_range=[-4, 4, 2],  # 增加步长，减少标签数量
            y_range=[-1, 1, 0.5],
            z_range=[0, 2, 1],   # 增加步长，减少标签数量
            x_length=8,
            y_length=4,
            z_length=4,
            axis_config={"include_tip": True, "include_numbers": True}
        )
        
        # 添加坐标轴标签（使用LaTeX）
        x_label = MathTex(r"t").next_to(axes.x_axis.get_end(), RIGHT)  # 简化标签
        y_label = MathTex(r"x(t)").next_to(axes.y_axis.get_end(), UP)
        z_label = MathTex(r"f").next_to(axes.z_axis.get_end(), OUT)    # 简化标签
        labels = VGroup(x_label, y_label, z_label)
        
        # 创建时域信号函数
        def time_func(t):
            return 0.5 * np.sin(2 * PI * 0.5 * t) + 0.3 * np.sin(2 * PI * 1 * t)
        
        # 添加时域信号方程（使用LaTeX）
        time_equation = MathTex(
            r"x(t) = 0.5\sin(2\pi \cdot 0.5t) + 0.3\sin(2\pi t)"  # 简化公式
        ).scale(0.8).to_corner(UL)
        
        # 创建时域信号曲线 - 减少采样点
        time_curve = ParametricFunction(
            lambda t: np.array([t, time_func(t), 0]),
            t_range=[-4, 4, 0.05],  # 增加采样间隔，减少点数
            color=BLUE
        )
        
        # 创建频谱的点和连线
        freq_points = VGroup(
            Dot3D(np.array([0, 0.5, 0.5]), color=RED),
            Dot3D(np.array([0, 0.3, 1]), color=RED)
        )
        
        # 频谱线
        freq_lines = VGroup(
            Line3D(start=np.array([0, 0, 0.5]), end=np.array([0, 0.5, 0.5]), color=RED),
            Line3D(start=np.array([0, 0, 1]), end=np.array([0, 0.3, 1]), color=RED)
        )
        
        # 动画部分
        self.play(
            Create(axes),
            Write(labels),
            Write(time_equation),
            run_time=2
        )
        
        self.play(Create(time_curve))
        
        # 创建时域上的点集 - 减少点的数量
        moving_dots = []
        n_dots = 20  # 减少点的数量
        for i in range(n_dots):
            t = -4 + 8 * i / (n_dots - 1)
            dot = Dot3D(np.array([t, time_func(t), 0]), color=YELLOW)
            moving_dots.append(dot)
        
        self.play(*[FadeIn(dot) for dot in moving_dots])
        
        # 显示傅里叶变换方程
        fourier_equation = MathTex(
            r"X(f) = \int x(t)e^{-j2\pi ft}dt"  # 简化公式
        ).scale(0.8).to_corner(UR)
        
        self.play(Write(fourier_equation))
        
        # 更改视角
        self.move_camera(phi=60 * DEGREES, theta=60 * DEGREES, run_time=2)
        
        # 傅里叶变换动画
        self.play(
            TransformFromCopy(VGroup(*moving_dots), freq_points),
            run_time=2
        )
        
        self.play(Create(freq_lines))
        
        # 添加频率标签
        freq_labels = VGroup(
            MathTex(r"0.5", color=RED).scale(0.7).move_to(np.array([1, 0.5, 0.5])),
            MathTex(r"1.0", color=RED).scale(0.7).move_to(np.array([1, 0.3, 1]))
        )
        
        self.play(Write(freq_labels))
        
        # 相机动画
        self.move_camera(phi=40 * DEGREES, theta=-30 * DEGREES, run_time=2)
        self.move_camera(phi=70 * DEGREES, theta=30 * DEGREES, zoom=0.8, run_time=2)
        
        self.wait(1)  # 减少等待时间


# 为了向后兼容，保留原始类名
FourierTransformScene = FourierTransform3DScene


if __name__ == "__main__":
    # 高质量渲染配置
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    
    # 使用以下命令运行：
    # manim -pqh fourier_transform_animation.py FourierTransform3DScene
    pass 