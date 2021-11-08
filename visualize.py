import numpy as np
import tkinter as tk
import random
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def generateRandomTasks(x_max):
    n = random.randint(5, 20)
    return [(random.randint(0, x_max), random.randint(10, 30)) for _ in range(n)]


def handlePanningLeft():
    pass

def handlePanningRight():
    pass

def handleZoomIn():
    pass

def handleZoomOut():
    pass

def gantt_draw():
    color = 'tab:blue'
    number_of_locations = 10
    location_gap = 0.5
    ylim = 50
    xlim = 260
    bar_height = (ylim / number_of_locations) - (2*location_gap)
    location_distance = bar_height + (2*location_gap)

    fig, gnt = plt.subplots()
    fig.set_size_inches(12, 6)

    gnt.set_ylim(0, ylim)
    gnt.set_xlim(0, xlim)

    gnt.set_xlabel('Time (nanoseconds)')
    gnt.set_ylabel('Thread Location')

    y_ticks = list(np.arange(location_gap + (bar_height/2), ylim, location_distance))
    y_labels = [str(i) for i in range(number_of_locations)]
    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_labels)

    gnt.grid(True)

    def getBarPosition(loc):
        return (loc * (bar_height + (2*location_gap))) + location_gap

    for i in range(number_of_locations):
        t1 = generateRandomTasks(xlim)
        gnt.broken_barh(t1, (getBarPosition(i), bar_height), facecolors=color)

    return fig


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gantt")
    # YSIZE = 800
    # root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    fig = gantt_draw()
    # fig = plt.figure(1)
    # plt.ion()
    # t = np.arange(0.0,3.0,0.01)
    # s = np.sin(np.pi*t)
    # plt.plot(t,s)

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
