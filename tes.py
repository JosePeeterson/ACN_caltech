
# import numpy as np
# import matplotlib.pyplot as plt
# ax = plt.figure().add_subplot(projection='3d')
# z = [1,2,3,4,5,6]
# x = [1,2,3,4,5,6]
# y = [1,2,3,4,5,6]
# colors= plt.cm.Reds(np.linspace(1,1,6))
# ax.plot(x, y, z, label='minimum values',c='g',markevery=[0],marker='o')
# ax.plot(x, y, z, label='Minimum values',c='g',marker='x')
# ax.set_xlabel('Charging cost obj')
# ax.set_ylabel('Battery deg. obj')
# ax.set_zlabel('Availability obj ')
# ax.set_title('1,3,4,5,')

# ax.legend()
# plt.show()

# import matplotlib as mpl
# from mpl_toolkits.mplot3d import Axes3D
# import numpy as np
# import matplotlib.pyplot as plt

# plt.rcParams['legend.fontsize'] = 10

# fig = plt.figure()
# ax = fig.gca(projection='3d')

# # Prepare arrays x, y, z
# theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
# z = np.linspace(-2, 2, 100)
# r = z**2 + 1
# x = r * np.sin(theta)
# y = r * np.cos(theta)

# l = ax.plot(x, y, z, marker='o', label='parametric curve both ends', markevery=[0,-1])
# l = ax.plot(x+1, y+1, z, 'r', marker='o', label='parametric curve one end', markevery=[0])
# ax.legend()

# plt.show()
# plt.close()


# import pickle
# import matplotlib.pyplot as plt
# ax = plt.plot([1,2,5,10])
# pickle.dump(ax, open("plot.pickle", "wb"))


# import pickle
# import matplotlib.pyplot as plt   
# ax = pickle.load(open("plot.pickle", "rb"))
# plt.show()

import numpy as np
import matplotlib.pyplot as plt   
colors = plt.cm.nipy_spectral(np.linspace(0,1,30))

print(colors)
plt.figure()
x = np.arange(0,10,1)
for i in range(0,30):
    plt.plot(x, i*x, color=colors[i])

plt.show()

soc1 =  [0, 0.6516666666666662, 0, 0, 0, 0, 0, 0.1, 0.1518888888888889, 0, 0.19286396358931368, 0.2199999999999999, 0.249, 0, 0, 0, 0.1, 0, 0.1499999999999999, 0, 0, 0, 0.10867534939790195, 0, 0.1, 0, 0, 0, 0, 0, 0, 0]

char_per =  [0, 0.46666666666667933, 0, 0, 0, 0, 0, 3.0, 1.800000000000015, 0, 2.983333333333351, -0.01666666666665746, 0.1666666666666723, 0, 0, 0, 2.5166666666666684, 0, 3.6000000000000156, 0, 0, 0, 5.649999999999906, 0, 2.2666666666666764, 0, 0, 0, 0, 0, 0, 0]
soc1 =  [0, 0.6516666666666662, 0, 0, 0, 0, 0, 0.1, 0.1518888888888889, 0, 0.19286396358931368, 0.2199999999999999, 0, 0, 0, 0, 0.1, 0, 0.1499999999999999, 0, 0, 0, 0.10867534939790195, 0, 0.1, 0, 0, 0, 0, 0, 0, 0]

SOCdep =  [0, 0.91, 0, 0, 0, 0, 0, 0.14, 0.18, 0, 0.22, 0.22, 0.16, 0, 0, 0, 0.14, 0, 0.15, 0, 0, 0, 0.38, 0, 0.25, 0, 0, 0, 0, 0, 0, 0]  