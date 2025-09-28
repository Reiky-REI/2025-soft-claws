# 2025-soft-claws｜机械触手（对数螺旋分段生成与 3D 打印）

基于对数螺旋的几何与解析公式，自动生成可分段的机械“软爪/触手”几何：
- 2D：按角度等分生成四边形片段，并导出 DXF；
- 3D：按段旋转挤出生成体，并在每段布置走线孔，导出 OpenSCAD 文件用于 3D 打印。

![preview](./_2025-May-29_01-58-35AM-000_CustomizedView16397410250.jpg)

---

## 功能概览
- 按给定最小/最大圈间距与中心轨迹长度，解析求解对数螺旋参数 a、b、终止角 θ_end；
- 将区间 [0, θ_end] 等分，计算边缘与中心螺旋坐标，拼接为四边形分段；
- 绘制示意图并导出 `line.dxf`（每段为闭合折线）；
- 生成带“走线孔”的 3D 分段模型至 `spiral_robot_3d_with_holes_fixed.scad`，可在 OpenSCAD 渲染后导出 STL；
- 提供示例打印件（.3mf）以便快速复现。

---

## 数学与算法（简要）
对数螺旋：\( r(\theta) = a\,e^{b\theta} \)

- 中心曲线长度（单圈 0→2π）：
  $$ L_c(b) = \\sqrt{1+b^2}\\,\\cdot\\,\\frac{s_{\\max}-s_{\\min}}{2b}\\,\\cdot\\,\\frac{e^{2\\pi b}+1}{e^{2\\pi b}-1} $$
- 由 \( L_c(b)=L_{center} \) 用 Brent 法数值求解 b；
- 参数 a：
  $$ a = \\frac{s_{\\min}}{e^{2\\pi b}-1} $$
- 终止角：
  $$ \\theta_{end} = \\frac{1}{b}\\ln\\!\\bigl(\\tfrac{s_{\\max}}{s_{\\min}}\\bigr) $$
- 边缘与中心半径：
  $$ r_{edge}(\\theta)=a\\,e^{b\\theta},\\quad r_{center}(\\theta)=\\tfrac12\\bigl(r_{edge}(\\theta)+r_{edge}(\\theta+2\\pi)\\bigr) $$
- 极坐标转直角：\( x=r\\cos\\theta,\\; y=r\\sin\\theta \)

完整推导与代码片段见 `公式.md`。

---

## 环境与依赖
- Python 3.9+
- 依赖包：
  - numpy
  - scipy
  - matplotlib（用于 2D 可视化）
  - ezdxf（导出 DXF）
  - SolidPython（包名 `solidpython`，脚本有导入，便于后续扩展）

Windows PowerShell 下的最小安装示例：
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install numpy scipy matplotlib ezdxf solidpython
```

---

## 快速开始

### 1) 生成 2D 分段 + DXF（`line.py`）
- 脚本位置：`line.py`
- 输出：
  - 窗口展示分段四边形示意；
  - 在仓库根目录导出 `line.dxf`。

运行：
```powershell
python .\line.py
```
运行结束后，控制台会打印求解得到的 \(a, b, \\theta_{end}\\)，并提示 DXF 导出路径。

参数（可在文件顶部修改）：
- `s_min, s_max`：相邻两圈的最小/最大径向间距（mm）；
- `L_center`：中心曲线的目标长度（mm）；
- `num_segments`：划分段数（影响四边形数量）。

### 2) 生成 3D 打印用 SCAD（`line_3Dprinter.py`）
- 脚本位置：`line_3Dprinter.py`
- 输出：在仓库根目录生成 `spiral_robot_3d_with_holes_fixed.scad`

运行：
```powershell
python .\line_3Dprinter.py
```
然后在 OpenSCAD 中打开生成的 `.scad` 文件：
- 预览（F5）→ 渲染（F6）；
- 导出 STL → 切片打印。

关键参数：
- `s_min, s_max, L_center, num_segments`：同上；
- `segment_thickness_ratio`：段厚度（相对该段宽度的比例）；
- `segment_rotation_angle`：每段旋转挤出角度（deg），影响柔顺性/行程；
- `hole_radius`：走线孔半径（mm）；
- `hole_offset_ratio`：走线孔圆环中心到局部原点的比例（相对段宽度）。

---

## 目录结构（重要文件）
- `line.py`：2D 分段与 DXF 导出脚本（含可视化）。
- `line_3Dprinter.py`：3D 分段体与走线孔的 OpenSCAD 代码生成器。
- `spiral_robot_3d_with_holes_fixed.scad`：已生成的示例 SCAD。
- `spiral_segments_axis.scad`：另一份 SCAD 片段（可作为参考/对比）。
- `line.dxf` / `line_*.dxf`：DXF 输出（运行后生成）。
- `打印/`：现成的 .3mf 打印文件集合（各零部件）。
- `公式.md`：数学推导与实现说明。
- `LICENSE`：许可协议。

---

## 提交历史（简要）
- `84332eb` — finish
- `1468e32` — Initial commit

---

## 常见问题
- 运行时报缺包：请确认已激活虚拟环境并安装依赖（见“环境与依赖”）。
- OpenSCAD 打开后预览空白：检查 `segment_rotation_angle` 是否为正，或增大 `$fn` 提升细分；确保多边形点顺序闭合且无自交。
- DXF 在 CAD 中显示比例异常：DXF 默认单位为“无单位”，请在导入时手动指定 mm。

---

## 许可
本项目遵循 `LICENSE` 所述的开源许可。使用与分发请遵守相关条款。

---

## 参考与致谢
- SciPy（Brent 法求根）
- NumPy / Matplotlib
- ezdxf
- OpenSCAD / SolidPython

---

## 后续可做
- 导出 STL 的一键脚本化（调用 OpenSCAD CLI）。
- 生成参数化的 BOM 与装配示意。
- 添加 `requirements.txt` 与 GitHub Actions 以便自动化构建与检查。
