// 文件：LogarithmicSpiral.scad
// 生成边缘螺旋线和中心螺旋线的基础版本

// ── 参数区 ─────────────────────────────
pi = 3.141592653589793;      // 圆周率
start_theta = 0;             // 起始角度(弧度)
end_theta = 8 * pi;          // 结束角度(4圈)
total_length = 400;          // 总长度(mm)
tip_width = 400;              // 末端中心螺旋线直径(mm)
tolerance = 0.01;            // 数值计算容差
angular_resolution = 1;      // 角度步进(度)

// ── 核心计算模块 ──────────────────────
/* 螺旋线长度计算函数
   参数：b-螺旋率, theta_range-角度范围
   返回：螺旋线长度 */
function spiral_length(b, theta_range) = 
    (sqrt(1 + pow(b,2))/b) * (exp(b*theta_range) - 1);

/* 二分法求解b参数
   参数：target_length-目标长度, theta_range-角度范围
   返回：满足长度条件的b值 */
function find_b(target_length, theta_range) = 
    _bisect_b(0.001, 1, 30, target_length, theta_range);

function _bisect_b(low, high, iter, target, theta_range) = 
    iter <= 0 ? (low+high)/2 :
    let(
        mid = (low+high)/2,
        current = spiral_length(mid, theta_range)
    )
    abs(current - target) < tolerance ? mid :
    current < target ? 
        _bisect_b(mid, high, iter-1, target, theta_range) :
        _bisect_b(low, mid, iter-1, target, theta_range);

/* 计算a参数
   参数：b-螺旋率, end_angle-终止角度, tip_dia-末端直径
   返回：a缩放系数 */
function compute_a(b, end_angle, tip_dia) = 
    tip_dia / (exp(b*end_angle) + exp(b*(end_angle + 2*pi)));

// ── 螺旋线生成模块 ────────────────────
/* 边缘螺旋线方程
   参数：a,b-螺旋参数, theta-当前角度
   返回：[x,y]坐标 */
function edge_spiral(a, b, theta) = 
    a * exp(b*theta) * [cos(theta), sin(theta)];

/* 中心螺旋线方程
   参数：a,b-螺旋参数, theta-当前角度
   返回：[x,y]坐标 */
function center_spiral(a, b, theta) = 
    (edge_spiral(a,b,theta) + edge_spiral(a,b,theta + 2*pi)) / 2;

// ── 可视化模块 ───────────────────────
module draw_spiral_points(points, thickness=1) {
    for(i=[0:len(points)-2]){
        hull(){
            translate(points[i]) circle(thickness/2);
            translate(points[i+1]) circle(thickness/2);
        }
    }
}

// ── 主执行模块 ───────────────────────
theta_range = end_theta - start_theta;

// 计算螺旋参数
b_value = find_b(total_length, theta_range);
a_value = compute_a(b_value, end_theta, tip_width);

// 生成点集
edge_points = [
    for(theta = [start_theta : deg2rad(angular_resolution) : end_theta])
    edge_spiral(a_value, b_value, theta)
];

center_points = [
    for(theta = [start_theta : deg2rad(angular_resolution) : end_theta])
    center_spiral(a_value, b_value, theta)
];

// 绘制结果
color("royalblue") draw_spiral_points(edge_points, 1.5);
color("gold") draw_spiral_points(center_points, 1.0);

// 输出参数
echo("计算参数：", a=a_value, b=b_value);
echo("验证长度：", 
    target=total_length, 
    actual=spiral_length(b_value, theta_range)
);