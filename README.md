# 交互式Manim动画生成系统

这是一个基于Web的交互式Manim动画生成系统，允许用户通过Web界面实时预览和调整数学动画。

## 功能特点

- 实时预览Manim动画
- 可视化控制相机角度和缩放
- 动态输入数学函数
- 基于Web的用户界面
- 实时渲染预览

## 安装步骤

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 安装Node.js依赖：
```bash
cd frontend
npm install
```

## 运行系统

1. 启动后端服务器：
```bash
cd backend
python app.py
```

2. 启动前端开发服务器：
```bash
cd frontend
npm start
```

3. 在浏览器中访问 http://localhost:3000

## 使用说明

1. 在函数输入框中输入数学函数（使用numpy语法）
2. 使用滑块调整相机角度（φ和θ）
3. 使用滑块调整缩放级别
4. 点击"生成预览"按钮查看结果

## 注意事项

- 确保已安装Python 3.7+
- 确保已安装Node.js 14+
- 需要安装LaTeX以支持数学公式渲染
- 建议使用现代浏览器（Chrome、Firefox等） 