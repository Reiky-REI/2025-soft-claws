import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from solid import polygon, rotate, rotate_extrude, translate, union, scad_render_to_file
from pathlib import Path
import ezdxf

# ─────────────指定参数 ──────────────────
s_min        = 12.0      # 最小圈间径向间距 (mm)
s_max        = 66.0     # 最大圈间径向间距 (mm)
L_center     = 200.0    # center 螺旋线长度 (mm)
num_segments = 12       # 将螺旋分成多少段，可按需修改
# ────────────────────────────────────────

# 根据指定的 center 螺旋线长度计算 b, a, θ_end

def Lc(b):
    # 中心螺旋线长度函数 L_c(b)
    # LaTeX:  L_c(b) = \int_0^{2\pi} \sqrt{r(\theta)^2 + \bigl(r'(\theta)\bigr)^2}\,d\theta
    # 经过解析可得：
    # L_c(b) = \sqrt{1 + b^2} 
    #           \,\frac{s_{\max} - s_{\min}}{2b}
    #           \,\frac{e^{2\pi b} + 1}{e^{2\pi b} - 1}
    return np.sqrt(1 + b**2) * (s_max - s_min) / (2 * b) * (np.exp(2*np.pi*b) + 1) / (np.exp(2*np.pi*b) - 1)

# 求解 b 使得 L_c(b) = L_center
# LaTeX:  \text{find } b: L_c(b) - L_{\rm center} = 0
b = brentq(lambda bb: Lc(bb) - L_center, 1e-6, 1.0)

# 计算 a
# LaTeX:  a = \frac{s_{\min}}{e^{2\pi b} - 1}
a = s_min / (np.exp(2*np.pi*b) - 1)

# 计算 θ_end
# LaTeX:  \theta_{\rm end} = \frac{1}{b} \ln\!\bigl(\tfrac{s_{\max}}{s_{\min}}\bigr)
theta_end = np.log(s_max / s_min) / b

print(f"计算结果： a = {a:.4f},  b = {b:.4f}, θ_end = {theta_end:.4f}")

# 将螺旋线分割成等角度小段
# LaTeX:  \theta_i = i\,\Delta\theta,\quad \Delta\theta = \frac{\theta_{\rm end}}{\text{num\_segments}}
theta_seg = np.linspace(0, theta_end, num_segments + 1)

# 计算每个节点的径向坐标
# LaTeX:  r_{\rm edge}(\theta)   = a\,e^{b\theta}
# LaTeX:  r_{\rm center}(\theta) = \tfrac12\bigl(r_{\rm edge}(\theta) + r_{\rm edge}(\theta + 2\pi)\bigr)
r_edge_seg   = a * np.exp(b * theta_seg)
r_center_seg = 0.5 * (r_edge_seg + a * np.exp(b * (theta_seg + 2*np.pi)))

# 极坐标转笛卡尔坐标
# LaTeX:  x(\theta) = r(\theta)\cos\theta,\quad y(\theta) = r(\theta)\sin\theta
x_edge_seg = r_edge_seg * np.cos(theta_seg)
y_edge_seg = r_edge_seg * np.sin(theta_seg)
x_ctr_seg  = r_center_seg * np.cos(theta_seg)
y_ctr_seg  = r_center_seg * np.sin(theta_seg)

# 绘制每个小段为四边形，连接相同 θ 的 edge 和 center 点
plt.figure(figsize=(6,6))
for i in range(num_segments):
    xs = [
        x_edge_seg[i],
        x_edge_seg[i+1],
        x_ctr_seg[i+1],
        x_ctr_seg[i],
        x_edge_seg[i]
    ]
    ys = [
        y_edge_seg[i],
        y_edge_seg[i+1],
        y_ctr_seg[i+1],
        y_ctr_seg[i],
        y_edge_seg[i]
    ]
    plt.plot(xs, ys, '-k')

plt.axis('equal')
plt.xlabel('X (mm)')
plt.ylabel('Y (mm)')
plt.title(f'对数螺旋细分为{num_segments}个四边形')
plt.grid(True)

# 新增：导出 DXF 文件
doc = ezdxf.new(dxfversion='R2010')
msp = doc.modelspace()
for i in range(num_segments):
    pts = [
        (x_edge_seg[i], y_edge_seg[i]),
        (x_edge_seg[i+1], y_edge_seg[i+1]),
        (x_ctr_seg[i+1], y_ctr_seg[i+1]),
        (x_ctr_seg[i], y_ctr_seg[i]),
        (x_edge_seg[i], y_edge_seg[i])
    ]
    msp.add_lwpolyline(pts, close=True)

dxf_output_path = "line.dxf"
doc.saveas(dxf_output_path)
print(f"DXF文件已导出到 {dxf_output_path}")

plt.show()
