# sim_energy_system_cap.py
#
# Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s
#  Simulation for capcitor based energy system
# 
# Parameters:
# sa_m2: Solar cell surface area-------- (m^2)
# eff: Solar cell efficiency
# voc: Solar array open current voltage- (Volts)
# c_f: Capacitance---------------------- (farads)
# r_esr: Solar panel series resistance-- (Ohms)
# q0_c: Initial charge------------------ (Coulombs)
# p_on_w: Power------------------------- (Watts)
# v_thresh: Voltage threshold----------- (Volts)
# dt_s: Time step----------------------- (s)
# dur_s: Duration----------------------- (s) 
#  ...
# Output:
#  Write time,voltage pair into a CSV file
#
# Written by Ryo Jumadiao
# Other contributors: None
#
# Optional license statement, e.g., See the LICENSE file for the license.

# import Python modules
# e.g., import math # math module
import sys # argv
import math  # math module
import csv  # csv module

# "constants"
Ir_w_m2 = 1336.1

# initialize script arguments
sa_m2 = float('nan')
eff = float('nan')
voc = float('nan')
c_f = float('nan')
r_esr = float('nan')
q0_c = float('nan')
p_on_w = float('nan')
v_thresh = float('nan')
dt_s = float('nan')
dur_s = float('nan')

# parse script arguments
if len(sys.argv) == 11:
    sa_m2 = float(sys.argv[1])
    eff = float(sys.argv[2])
    voc = float(sys.argv[3])
    c_f = float(sys.argv[4])
    r_esr = float(sys.argv[5])
    q0_c = float(sys.argv[6])
    p_on_w = float(sys.argv[7])
    v_thresh = float(sys.argv[8])
    dt_s = float(sys.argv[9])
    dur_s = float(sys.argv[10])

else:
    print(\
        'Usage: ' \
        'python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s'\
    )
    exit()

#Helper Functions

def calc_solar_current(Ir_w_m2, sa_m2, eff, voc):
    return (Ir_w_m2 * sa_m2 * eff) / voc

def calc_node_discr(q_c, c_f, i_a, esr_ohm, power_w):
    return (q_c / c_f + i_a * esr_ohm) ** 2 - 4 * power_w * esr_ohm

def calc_node_voltage(disc, q_c, c_f, i_a, esr_ohm):
    return (q_c / c_f + i_a * esr_ohm + math.sqrt(disc)) / 2


# write script below this line
isc_a = calc_solar_current(irrad, sa_m2, eff, voc)
i1_a = isc_a
qt_c = q0_c
p_mode_w = p_on_w
t_s = 0.0

node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)

log = [[t_s, node_v]]

if voc <= node_v and i1_a != 0.0:
    i1_a = 0.0

if node_v < v_thresh:
    p_mode_w = 0.0

while log[-1][0] < dur_s:
    i3_a = p_mode_w / node_v 
    qt_c += (i1_a - i3_a) * dt_s
    
    if qt_c < 0.0:
        qt_c = 0.0
    
    if p_mode_w == 0.0 and node_v >= voc:
        p_mode_w = p_on_w
    
    i1_a = isc_a if 0 <= node_v < voc else 0.0
    
    node_discr = node_discrim(qt_c, c_f, i1_a, r_esr, p_mode_w)
    if node_discr < 0.0:
        p_mode_w = 0.0
        node_discr = node_discrim(qt_c, c_f, i1_a, r_esr, p_mode_w)
        
    node_v = node_voltage(qt_c, c_f, i1_a, r_esr, node_discr)
    if node_v < v_thresh:
        p_mode_w = 0.0
    
    if voc <= node_v and i1_a != 0.0:
        i1_a = 0.0
        
    log.append([t_s,node_v])
    t_s += dt_s
    
with open('./log.csv',mode='w',newline='') as outfile:
  csvwriter = csv.writer(outfile)
  csvwriter.writerow(\
   ['t_s','volts']\
  )
  for e in log:
    csvwriter.writerow(e)