import numpy as np
import tkinter as tk
import random
import matplotlib
from matplotlib import ticker

from data_store import KDStore

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def generateRandomTasks(x_max):
    n = random.randint(5, 20)
    return [(random.randint(0, x_max), random.randint(10, 30)) for _ in range(n)]


class Visualize:

    def __init__(self):
        self.number_of_locations = 10
        self.location_gap = 0.5
        self.ylim = 50
        self.xlim = 260
        self.bar_height = (self.ylim / self.number_of_locations) - (2*self.location_gap)
        self.location_distance = self.bar_height + (2*self.location_gap)
        self.visible_x = [0, self.xlim]
        self.visible_y = [0, self.ylim]
        self.gantt = None

    def handlePanningLeft(self):
        pass

    def handlePanningRight(self):
        pass

    def handleZoomIn(self):
        pass

    def handleZoomOut(self):
        pass

    def updateData(self, kd_store, figure_width):
        self.number_of_locations = len(kd_store.parsed_data.info['locationNames'])
        self.bar_height = (self.ylim / self.number_of_locations) - (2*self.location_gap)
        self.location_distance = self.bar_height + (2*self.location_gap)
        self.visible_x = kd_store.parsed_data.info['domain']
        data = kd_store.queryInRange(0, self.number_of_locations - 1, self.visible_x[0], self.visible_x[1], figure_width)
        return data

    def initiate_gantt_draw(self):
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        figure_width = 1500 * px  # in pixel
        figure_height = 600 * px  # in pixel

        fig, gnt = plt.subplots(figsize=(figure_width, figure_height))
        # fig.set_size_inches(12, 6)
        fig.canvas.callbacks.connect('scroll_event', self.mouse_scrolled)
        fig.canvas.callbacks.connect('button_press_event', self.mouse_clicked)
        fig.canvas.callbacks.connect('button_release_event', self.mouse_released)

        gnt.set_xlabel('Time (nanoseconds)')
        gnt.set_ylabel('Thread Location')
        gnt.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

        kd_store = KDStore()
        data = self.updateData(kd_store, figure_width)
        gnt.grid(True)
        # for i in range(self.number_of_locations):
        #     self.data[i] = generateRandomTasks(self.xlim)
        self.gantt = gnt
        self.update_gantt(data, kd_store.parsed_data.info['locationNames'])
        return fig

    def update_gantt(self, data, location_names):
        def construct_location_name(d):
            a = int(d)
            c = 32
            node = a >> c
            thread = (int(d) & 0x0FFFFFFFF)
            aggText = ''
            aggText += str(node) + ' - T'
            aggText += str(thread)
            return aggText

        y_ticks = list(np.arange(self.location_gap + (self.bar_height/2), self.ylim, self.location_distance))
        y_labels = [construct_location_name(location_names[i]) for i in range(self.number_of_locations)]
        self.gantt.set_yticks(y_ticks)
        self.gantt.set_yticklabels(y_labels)

        self.gantt.set_ylim(self.visible_y[0], self.visible_y[1])
        self.gantt.set_xlim(self.visible_x[0], self.visible_x[1])

        def get_bar_position(par, loc):
            return (loc * (par.bar_height + (2*par.location_gap))) + par.location_gap
        color = 'tab:blue'
        for i in range(self.number_of_locations):
            self.gantt.broken_barh(data[i], (get_bar_position(self, i), self.bar_height), facecolors=color)
        self.gantt.figure.canvas.draw()

    def mouse_scrolled(self, event):
        scroll_unit = 1
        if event.button == 'up':
            # print(event.xdata, event.ydata)
            if self.visible_x[0] + (2 * scroll_unit) < self.visible_x[1]:
                self.visible_x[0] = self.visible_x[0] + scroll_unit
                self.visible_x[1] = self.visible_x[1] - scroll_unit
                self.update_gantt()
        elif event.button == 'down':
            self.visible_x[0] = self.visible_x[0] - scroll_unit
            self.visible_x[1] = self.visible_x[1] + scroll_unit
            self.update_gantt()
        else:
            print('Scrolled outside axes bounds but inside plot window')

    def mouse_clicked(self, event):
        if event.inaxes is not None:
            print(event.xdata, event.ydata)
        else:
            print('Clicked outside axes bounds but inside plot window')

    def mouse_released(self, event):
        if event.inaxes is not None:
            print(event.xdata, event.ydata)
        else:
            print('Released outside axes bounds but inside plot window')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gantt")
    # YSIZE = 800
    # root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    vis = Visualize()
    fig = vis.initiate_gantt_draw()
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
