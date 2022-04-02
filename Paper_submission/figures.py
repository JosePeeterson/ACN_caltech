
import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0,1.3,0.1)
y = 0.1 + 0.5*x

plt.plot(x,y)
plt.xlabel(' Charge processed, C (Ah)')
plt.ylabel('SOC (0 - 1)')
plt.xlim((0,2))
plt.ylim((0,1))

plt.vlines(x=1.2, ymin=0, ymax=0.7, colors='blue', ls=':', lw=2, label='vline_single - full height')
plt.vlines(x=0, ymin=0, ymax=0.1, colors='blue', ls=':', lw=2, label='vline_single - full height')


plt.savefig('soc_char_proc.png',)

plt.show()
























