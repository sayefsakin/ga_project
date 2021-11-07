import numpy as np
import tkinter as tk

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def gantt_draw():
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()

    # Setting Y-axis limits
    gnt.set_ylim(0, 50)

    # Setting X-axis limits
    gnt.set_xlim(0, 160)

    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('seconds since start')
    gnt.set_ylabel('Processor')

    # Setting ticks on y-axis
    gnt.set_yticks([15, 25, 35])
    # Labelling tickes of y-axis
    gnt.set_yticklabels(['1', '2', '3'])

    # Setting graph attribute
    gnt.grid(True)

    # Declaring a bar in schedule
    gnt.broken_barh([(40, 50)], (30, 9), facecolors =('tab:orange'))

    # Declaring multiple bars in at same level and same width
    gnt.broken_barh([(110, 10), (150, 10)], (10, 9), facecolors ='tab:blue')

    gnt.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9), facecolors =('tab:red'))
    return fig

if __name__ == "__main__":
    root = tk.Tk()

    fig = gantt_draw()
    # fig = plt.figure(1)
    plt.ion()
    t = np.arange(0.0,3.0,0.01)
    s = np.sin(np.pi*t)
    plt.plot(t,s)

    canvas = FigureCanvasTkAgg(fig, master=root)
    plot_widget = canvas.get_tk_widget()

    # def update():
    #     s = np.cos(np.pi*t)
    #     plt.plot(t,s)
    #     #d[0].set_ydata(s)
    #     fig.canvas.draw()

    plot_widget.grid(row=0, column=0)
    # tk.Button(root,text="Update",command=update).grid(row=1, column=0)
    root.mainloop()
