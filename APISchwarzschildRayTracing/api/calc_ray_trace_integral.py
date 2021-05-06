# https://colab.research.google.com/drive/14ngIoAYnXPfBXpThX7jxMALhWRq5826I?authuser=1#scrollTo=RLuJYQJw9GpK

import numpy as np
from scipy.special import ellipkinc as ei

Dcrit = np.sqrt(27)
abstol = 1.0e-12  # Tolerance for D=Dcrit


# Given the impact parameter (D) and mass (M), find the real roots of
# the cubic f(u) = 2Mu^3 - u^2 + 1/D^2
def roots_fu(D, M):
    # Compute discriminant and coffecients of the depressed cubic
    discrim = D * D - 27 * M * M
    p, q = -1 / 12 / M / M, (0.5 / D / D - 1 / 108 / M / M) / M
    ofs = 1 / 6 / M  # Offset to add to roots of depressed cubic

    if discrim < 0:  # Just one real root
        rr = np.zeros(1)
        delta = np.sqrt((4 * p * p * p + 27 * q * q) / 3) / 6
        aa = np.cbrt(-q / 2 + delta)
        bb = np.cbrt(-q / 2 - delta)
        rr[0] = aa + bb + ofs
    elif discrim == 0:  # Multiple real roots
        rr = np.zeros(2)
        rr[0], rr[1] = -ofs, 2 * ofs
    else:  # Three real roots
        rr = np.zeros(3)
        p3 = np.sqrt(-p / 3)
        theta = np.arccos(1.5 * q / p / p3) / 3
        r1 = 2 * p3 * np.cos(theta)
        r2 = 2 * p3 * np.cos(theta - 2 * np.pi / 3)
        r3 = 2 * p3 * np.cos(theta - 4 * np.pi / 3)
        rr = np.sort([r1, r2, r3]) + ofs  # Sort roots in ascending order, add offset

    return rr

def if_D_gt_Dcrit_get_ray(D, r0, theta0, delta0, rstop, npoints):
  # inout = 1 for outward rays at (r0,theta0), and -1 for inward rays
  # updn = 1 for rays above the radial direction, -1 for those below
  inout, updn = np.sign(np.cos(delta0)), np.sign(np.sin(delta0))

  # If ray is entirely tangential then we're at periastron
  if (np.cos(delta0) == 0):
    inout = 1
    b2 = 1 / r0
    Q = np.sqrt((r0 - 2.) * (r0 + 6.))
    b3, b1 = (r0 - 2. - Q) / 4 / r0, (r0 - 2. + Q) / 4 / r0
  else:
    b3, b2, b1 = roots_fu(D, 1)

  periastron = 1 / b2
  m = (b2 - b3) / (b1 - b3)
  CC = np.sqrt(2 / (b1 - b3))

  if (inout == 1):  # outward rays
    rr = np.linspace(r0, rstop, npoints)
    uu = 1 / rr
    phi = np.arcsin(np.sqrt((b2 - uu) / (b1 - uu) / m))
    Fi = updn * CC * ei(phi, m)

  if (inout == -1):  # inward rays
    rf = np.abs(rstop)
    if (rf < periastron):
      print('periastron=', periastron, ' whereas magnitude of rstop=', rf)
      print('rstop cannot be smaller than periastron. bailing...')
      return 0
    elif (rstop > periastron):  # r0 and rstop on the same side of periastron
      rr = np.linspace(r0, rf, npoints)
      uu = 1 / rr
      phi = np.arcsin(np.sqrt((b2 - uu) / (b1 - uu) / m))
      Fi = -updn * CC * ei(phi, m)
    elif (rstop < -periastron) and (r0 == rf):
      if (npoints % 2 == 0):
        rr_in = np.linspace(r0, periastron, int(npoints / 2), endpoint=False)
        uu_in = 1 / rr_in
        phi_in = np.arcsin(np.sqrt((b2 - uu_in) / (b1 - uu_in) / m))
        Fi_in = -updn * CC * ei(phi_in, m)
        # Put both sides of the ray together
        rr = np.concatenate((rr_in, rr_in[::-1]))
        Fi = np.concatenate((Fi_in, -Fi_in[::-1]))
      else:
        rr_in = np.linspace(r0, periastron, int((npoints - 1) / 2))
        uu_in = 1 / rr_in
        phi_in = np.arcsin(np.sqrt((b2 - uu_in) / (b1 - uu_in) / m))
        Fi_in = -updn * CC * ei(phi_in, m)
        # Put both sides of the ray together
        rr = np.concatenate((rr_in, [periastron], rr_in[::-1]))
        Fi = np.concatenate((Fi_in, [0], -Fi_in[::-1]))
    elif (rstop < -periastron) and (r0 != rf):
      # Otherwise, when r0 != rf, the radial excusrion of the ray is
      # from r0 in to periastron and then out to rf
      # r_excur = (r0-periastron) + (rf-periastron)
      r_excur = r0 + rf - 2 * periastron
      # Out of the total path, the part between min(rf,r0) and periastron
      # is symmetric
      r_in = np.amin([r0, rf])
      # So if we want npoints during the entire excursion, the number of
      # points between r_in and periastron should be
      # n_in = npoints*(2*(r_in-periastron)/r_excur)
      # However this excursion of r_in->periastron->r_in is symmetric. So
      # we really need only half as many points to cover this range.
      n_in = int(npoints * (r_in - periastron) / r_excur)
      # We reserve one point for periastron location, and reserve
      # the remaining points are outside r_in and inside r_out = max(r0,rf)
      n_out = npoints - 2 * n_in - 1
      r_out = np.amax([r0, rf])
      # Now first construct the ray between r_out and r_in in n_out points
      rr_out = np.linspace(r_out, r_in, n_out, endpoint=False)
      uu_out = 1 / rr_out
      phi_out = np.arcsin(np.sqrt((b2 - uu_out) / (b1 - uu_out) / m))
      Fi_out = -updn * CC * ei(phi_out, m)
      # And then construct the ray from r_in to almost periastron
      rr_in = np.linspace(r_in, periastron, n_in, endpoint=False)
      uu_in = 1 / rr_in
      phi_in = np.arcsin(np.sqrt((b2 - uu_in) / (b1 - uu_in) / m))
      Fi_in = -updn * CC * ei(phi_in, m)
      # Add everything together to make the final ray
      if (r0 > rf):
        rr = np.concatenate((rr_out, rr_in, [periastron], rr_in[::-1]))
        Fi = np.concatenate((Fi_out, Fi_in, [0], -Fi_in[::-1]))
      else:
        rr = np.concatenate((rr_in, [periastron], rr_in[::-1], rr_out[::-1]))
        Fi = np.concatenate((Fi_in, [0], -Fi_in[::-1], -Fi_out[::-1]))
    else:
      print('this should not happen! bailing.')
      return 0

  # Rotate so that the polar angle of the starting point matches
  theta_offset = Fi[0] - theta0
  Fi = Fi - theta_offset
  return rr, Fi


def if_D_lt_Dcrit_get_ray(D, r0, theta0, delta0, rstop, npoints):
  # inout = 1 for outward rays at (r0,theta0), and -1 for inward rays
  # updn = 1 for rays above the radial direction, -1 for those below
  inout, updn = np.sign(np.cos(delta0)), np.sign(np.sin(delta0))

  # Get the only real root of f(u)
  beta = roots_fu(D, 1)

  # Following Abr & Stegun (7th ed.), pg. 597, sec. 17.4.70 and 17.4.71
  pp_beta = beta * (3 * beta - 1)  # p'(u) at beta
  ppp_beta = 6 * beta - 1  # p"(u) at beta
  lambda2 = np.sqrt(pp_beta)
  m = 0.5 - 0.125 * ppp_beta / lambda2

  # Set up the radial and inverse radial arrays
  rr = np.linspace(r0, rstop, npoints)
  uu = 1 / rr

  u_s = 1 / r0

  phi_s = np.arccos((lambda2 - u_s + beta) / (lambda2 + u_s - beta))
  Fs = ei(phi_s, m)

  phi = np.arccos((lambda2 - uu + beta) / (lambda2 + uu - beta))
  Fr = ei(phi, m)
  theta = (Fs - Fr) / np.sqrt(2 * lambda2)

  theta = inout * updn * theta + theta0

  return rr, theta


# Eq. (231) from Chandrasekhar (1983).
def u_Dcrit(theta, theta0):
  tmp = np.tanh((theta - theta0) / 2)
  return 0.5 * tmp * tmp - 1 / 6


vec_u_Dcrit = np.vectorize(u_Dcrit)


def if_D_eq_Dcrit_get_ray(r0, theta0, delta0, rstop_nturns, npoints):
  # inout = 1 for outward rays at (r0,theta0), and -1 for inward rays
  # updn = 1 for rays above the radial direction, -1 for those below
  inout, updn = np.sign(np.cos(delta0)), np.sign(np.sin(delta0))

  # What should theta_0 in Chandrasekhar's eq. (231) be so that the ray goes
  # through the point (1/r0, 0) in polar coordinates
  theta_0 = -2 * np.arctanh(np.sqrt(2 * (1 / r0 + 1 / 6)))

  if inout == +1:
    umin = 1 / rstop_nturns
    # What is the polar angle of this ray (i.e. the one going thru (1/r0,0) in
    # polar coordinates) at umin
    theta_umin = theta_0 + 2 * np.arctanh(np.sqrt(2 * (umin + 1 / 6)))
    theta_vec = np.linspace(0, theta_umin, npoints)
    u_vec = vec_u_Dcrit(theta_vec, theta_0)
  elif inout == -1:
    num_turns = rstop_nturns
    theta_vec = np.linspace(0, num_turns * 2 * np.pi, npoints)
    u_vec = vec_u_Dcrit(theta_vec, theta_0)
  else:
    print('undefined direction in D_eq_Dcrit case. bailing.')
    return 0

  # Add offset the angles to rotate such the the ray passes through
  # (r0,theta0), and flip (if needed) to match the direction correctly
  return 1 / u_vec, theta0 - inout * updn * theta_vec


def schwarzschild_get_ray(r0, theta0, delta0, rstop, npoints):
  # Get the impact parameter
  D = r0 * np.abs(np.sin(delta0)) / np.sqrt(1 - 2 / r0)
  D_Dcrit_minus1 = D / Dcrit - 1

  if (D_Dcrit_minus1 > abstol):
    rr, theta = if_D_gt_Dcrit_get_ray(D, r0, theta0, delta0, rstop, npoints)
  elif (D_Dcrit_minus1 < -abstol):
    rr, theta = if_D_lt_Dcrit_get_ray(D, r0, theta0, delta0, rstop, npoints)
  else:
    rr, theta = if_D_eq_Dcrit_get_ray(r0, theta0, delta0, rstop, npoints)

  return rr, theta


# Test
r0, theta0 = 6, np.deg2rad(70)
npts = 500

delta0 = np.deg2rad(-43)
r_vec1, th_vec1 = schwarzschild_get_ray(r0, theta0, delta0, r0 + 3, npts)
r_vec2, th_vec2 = schwarzschild_get_ray(r0, theta0, delta0 + np.pi, r0 - r0 + 2, npts)

delta0 = np.deg2rad(-45)
r_vec3, th_vec3 = schwarzschild_get_ray(r0, theta0, delta0, r0 + 3, npts)
r_vec4, th_vec4 = schwarzschild_get_ray(r0, theta0, delta0 + np.pi, r0 - r0 + 2, npts)

delta0 = np.deg2rad(-47)
r_vec5, th_vec5 = schwarzschild_get_ray(r0, theta0, delta0, r0 + 3, npts)
r_vec6, th_vec6 = schwarzschild_get_ray(r0, theta0, delta0 + np.pi, -r0 - 3, npts)

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 12))
plt.axes(projection='polar')
plt.polar(th_vec1, r_vec1, 'r-')
plt.polar(th_vec2, r_vec2, 'r-')

plt.polar(th_vec3, r_vec3, 'g-')
plt.polar(th_vec4, r_vec4, 'g-')

plt.polar(th_vec5, r_vec5, 'b-')
plt.polar(th_vec6, r_vec6, 'b-')

plt.polar(theta0, r0, 'go')  # Starting point in green
plt.fill_between(np.linspace(0.0, 2 * np.pi, 100), 2 * np.ones(100), color='k')
plt.show()