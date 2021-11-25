import xt_pdenew_matrix as matrix
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt
from matplotlib import cm

"""
利用坐标变换，在极坐标下求解原方程解为u = x^2+y^2-1的拉普拉斯方程，即-delta u = -4
"""

sin = np.sin
cos = np.cos
pi = np.pi

# 请注意r/s单位不是国际单位，应换算成弧度每秒，而一转的弧度是2*pi，故需要乘2*pi
ww = 50.0/60*2*pi  # ----------------------------------------晶片的角速度
wp = 100/60*2*pi  # ----------------------------------------抛光垫的角速度
angle1 = 0.02 * pi / 180  # ---------------------------转角
angle2 = 0.018 * pi / 180  # ---------------------------倾角
d = 0.15  # ---------------------------晶片和抛光垫的旋转中心距
r0 = 5.0*1e-2
p0 = 101000.0
hpiv = 8.0*1e-5  # ----------------------------------------晶片中心高度
viscosity = 0.00214  # ---------------------------抛光液粘度
rho = 1800.0

xx = r0 / hpiv
aa = 6 * viscosity * wp / p0 * xx ** 2
dd = d / r0
ee = ww / wp

nr = 64
n_theta = 64
r = np.linspace(0, 1, nr)
hr = 1 / (nr - 1)
theta = np.linspace(0, 2 * pi, n_theta)
h_theta = 2 * pi / (n_theta - 1)
r_in = r[0:-1]  # 去掉尾
theta_in = theta[0:-1]  # 去掉尾
n_in = (r_in.size - 1) * theta_in.size + 1
D0 = np.zeros(n_in - 1)
D1 = np.zeros(n_in - 1)
Dn = np.zeros(n_in - 1)
D_1 = np.zeros(n_in - 1)
D_n = np.zeros(n_in - 1)
f = np.zeros(n_in)
b = np.zeros(n_in)
A = np.zeros((n_in - 1, n_in - 1))
B = np.zeros((n_in, n_in))
data = np.zeros((theta.size, r.size))
print(data.shape)


def h_function(ri, tj):
    return 1 - xx * r_in[ri] * sin(angle1) * cos(theta_in[tj]) - xx * r_in[ri] \
           * sin(angle2) * sin(theta_in[tj])


def hhh(ri, tj):
    return h_function(ri, tj) ** 3


def dh_r(tj):
    return -(xx * sin(angle1) * cos(theta_in[tj]) + xx * sin(angle2) * sin(theta_in[tj]))


def dh_theta(ri, tj):
    return xx * r_in[ri] * sin(angle1) * sin(theta_in[tj]) - xx * r_in[ri] \
           * sin(angle2) * cos(theta_in[tj])


def dhhh_r(ri, tj):
    return 3 * h_function(ri, tj) ** 2 * dh_r(tj)


def dhhh_theta(ri, tj):
    return 3 * h_function(ri, tj) ** 2 * dh_theta(ri, tj)


def c1(ri, tj):
    return 0.5 * hhh(ri, tj) * hr + r_in[ri] * (hhh(ri, tj) + 0.5 * hr * dhhh_r(ri, tj))


def c2(ri, tj):
    return 2 * r_in[ri] * hhh(ri, tj)


def c3(ri, tj):
    return -0.5 * hhh(ri, tj) * hr + r_in[ri] * (hhh(ri, tj) - 0.5 * hr * dhhh_r(ri, tj))


def c4(ri, tj):
    return hhh(ri, tj) + 0.5 * h_theta * dhhh_theta(ri, tj)


def c5(ri, tj):
    return 2 * hhh(ri, tj)


def c6(ri, tj):
    return hhh(ri, tj) - 0.5 * h_theta * dhhh_theta(ri, tj)


def f1(ri, tj):
    return aa * dd * sin(theta_in[tj]) * r_in[ri] * dh_r(tj)


def f2(ri, tj):
    return aa * (dd * cos(theta_in[tj]) + r_in[ri] + r_in[ri] * ee) * dh_theta(ri, tj)


def lixinf1(ri, tj):
    return 6 * rho * r0 ** 2 / p0 * r_in[ri] ** 2 * h_function(ri, tj) ** 2 \
           * wp ** 2 * dh_r(tj)


def lixinf2(ri, tj):
    return 12 * rho * r0 ** 2 / p0 * r_in[ri] * dd * h_function(ri, tj) ** 2 \
           * cos(theta_in[tj]) * wp ** 2 * dh_r(tj)


def lixinf3(ri, tj):
    return 6 * rho * r0 ** 2 / p0 * dd ** 2 * h_function(ri, tj) ** 2 \
           * cos(theta_in[tj]) ** 2 * wp ** 2 * dh_r(tj)


def lixinf4(ri, tj):
    return -3 * rho * r0 ** 2 / p0 * r_in[ri] ** 2 * h_function(ri, tj) ** 2\
           * ww ** 2 * dh_r(tj)


def lixinf5(ri, tj):
    return -6 * rho * r0 ** 2 / p0 * dd * h_function(ri, tj) ** 2 \
           * sin(theta_in[tj]) * wp ** 2 * dh_theta(ri, tj)


def lixinf6(ri, tj):
    return -3 * rho * r0 ** 2 / p0 / r_in[ri] * dd ** 2 * h_function(ri, tj) ** 2 \
           * sin(2 * theta_in[tj]) * wp ** 2 * dh_theta(ri, tj)


def lixinf7(ri, tj):
    return 4 * rho * r0 ** 2 / p0 * r_in[ri] * hhh(ri, tj) * wp ** 2


def lixinf8(ri, tj):
    return -2 * rho * r0 ** 2 / p0 * r_in[ri] * hhh(ri, tj) * ww ** 2


def lixinf9(ri, tj):
    return 2 * rho * r0 ** 2 / p0 * dd * hhh(ri, tj) * cos(theta_in[tj]) * wp ** 2


def lixinf10(ri, tj):
    return -2 * rho * r0 ** 2 / (p0 * r_in[ri]) * wp ** 2 * hhh(ri, tj) \
           * dd ** 2 * cos(2 * theta_in[tj])


def lixinf(ri, tj):
    return lixinf1(ri, tj) + lixinf2(ri, tj) + lixinf3(ri, tj) + lixinf4(ri, tj)\
           + lixinf5(ri, tj) + lixinf6(ri, tj) + lixinf7(ri, tj) + lixinf8(ri, tj) \
           + lixinf9(ri, tj) + lixinf10(ri, tj)


print(lixinf(50, 10))