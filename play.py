# Importing PyQuil Libraries
from pyquil import Program
from pyquil.gates import *
from pyquil.quil import DefGate
from pyquil.api import WavefunctionSimulator
from pyquil.parameters import Parameter, quil_sin, quil_cos, quil_exp
from pyquil.latex import to_latex
from math import pi, log2, sqrt
import itertools
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()

# Parameteriztion
t1 = [x for x in np.linspace(-1,1,30)]      # Player 1 t1
t2 = [x for x in np.linspace(-1,1,30)]      # Player 2 t2
gm = [x for x in np.linspace(0,np.pi/2, 4)]  # Game Gamma

# Program Init
l = 0
ans = []
ansk = []
ansl = []
ansm = []

def f(x, y):
    return x*len(t1)+y

def evol(p, theta1, phi1, theta2, phi2):
    u_3_1 = np.array([[np.exp(phi1)*np.cos(theta1/2), np.sin(theta1/2)],
                    [np.sin(-theta1/2), np.exp(-phi1)*np.cos(theta1/2)]])
    u_3_2 = np.array([[np.exp(phi2)*np.cos(theta2/2), np.sin(theta2/2)],
                    [np.sin(-theta2/2), np.exp(-phi2)*np.cos(theta2/2)]])
    u_3 = np.kron(u_3_1,u_3_2)
    # Get the Quil definition for the new gate
    u_3_definition = DefGate('U3', u_3)
    p += u_3_definition 
    # Get the gate constructor
    U3 = u_3_definition.get_constructor()
    return U3

for i in gm:
    result_a = []
    result_b = []
    result_c = []
    result_d = []
    result_e = []
    for j in t1:  # A
        for k in t2:  # B

            # U constructor
            X_0 = np.array([[1, 0, 0, -1], [0, 1, 1, 0], [0, 1, 1, 0], [-1, 0, 0, 1]])
            X_1 = np.array([[1, 0, 0, 1], [0, 1, -1, 0], [0, -1, 1, 0], [1, 0, 0, 1]])
            u1 = 0.5*np.exp(complex(0, -i)/2)*X_0 + 0.5*np.exp(complex(0, i)/2)*X_1
            u2 = np.matrix.getH(u1)
            # Get the Quil definition for the new gate
            u_1_definition = DefGate("U1", u1)
            u_2_definition = DefGate("U2", u2)
            # Get the gate constructor
            U1 = u_1_definition.get_constructor()
            U2 = u_2_definition.get_constructor()

            p = Program()
            wf1 = WavefunctionSimulator()
            p += u_1_definition
            p += U1(0, 1)

            result_c.append(wf1.wavefunction(p))
            if j < 0 and k < 0:
                Ue = evol(p, 0, complex(0, -j*np.pi/2), 0, complex(0, -k*np.pi/2))
                p += Ue(0, 1)
            elif j < 0 and k >= 0:
                Ue = evol(p, 0, complex(0, -j*np.pi/2), k*np.pi, 0)
                p += Ue(0, 1)
            elif j >=0 and k < 0:
                Ue = evol(p, j*np.pi, 0, 0, complex(0, -k*np.pi/2))
                p += Ue(0, 1)
            else:
                Ue = evol(p, j*np.pi, 0, k*np.pi, 0)
                p += Ue(0, 1)

            result_e.append(wf1.wavefunction(p))

            p += u_2_definition
            p += U2(0, 1)
            wavefunction = wf1.wavefunction(p)
            result_d.append(wf1.wavefunction(p))

            outcome = wavefunction.get_outcome_probs()
            ans1 = 3*outcome['00'] + 0*outcome['01'] + \
                5*outcome['10'] + 1*outcome['11']
            ans2 = 3*outcome['00'] + 5*outcome['01'] + \
                0*outcome['10'] + 1*outcome['11']
            result_a.append(ans1)
            result_b.append(ans2)

            p = None
            wf1 = None
            wavefunction = None


    x = np.linspace(-1, 1, len(t1))  # [x for x in range(0,50)]
    y = np.linspace(-1, 1, len(t2))  # [x for x in range(0,50)]
    X, Y = np.meshgrid(x, y)
    F = f(X, Y)
    G = f(X, Y)

    for i in range(0, len(F)):
        for j in range(0, len(G)):
            a = i*len(F)+j
            b = i*len(G)+j
            F[i][j] = float(result_a[a])
            G[i][j] = float(result_b[b])
        
    l += 1
    ans.append(result_a)
    ansk.append(result_c)
    ansl.append(result_d)
    ansm.append(result_e)

    #ax = plt.subplot(4, 4, l)
    ax = fig.add_subplot(2, 2, l, projection='3d')
    #ax.title(label="'Correlation Factor = '+ str(i)")
    ax.set_xlabel(r'$U_A$', fontsize=15)
    ax.set_ylabel(r'$U_B$',  fontsize=15)
    ax.set_zlabel(r"$\$_{A}$", rotation=180, fontsize=15)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax.set_xticklabels(
        [r"$Q$", "", r"$C$", "", r"$D$"], fontsize=10)
    ax.set_yticks([-1, -0.5, 0, 0.5, 1])
    ax.set_yticklabels(
        [r"$Q$", "", r"$C$", "", r"$D$"], fontsize=10)
    ax.set_zticks([1, 2, 3, 4, 5])
    ax.set_zticklabels(
        [r"$1$", r"$2$", r"$3$", r"$4$", r"$5$"], fontsize=10)
    ax.grid(False)
    ax.plot_surface(X, Y, F, cmap='plasma',
                    linewidth=0.75, edgecolors='black')
    
plt.show()
