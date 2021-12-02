import copy
import io
import math
import tkinter

import PIL
import numpy as np
from tkinter import *
import random
import matplotlib
from matplotlib import ticker, animation
from datetime import datetime
from data_store import KDStore
from PIL import Image, ImageTk, ImageDraw

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def generateRandomTasks(x_max):
    n = random.randint(5, 20)
    return [(random.randint(0, x_max), random.randint(10, 30)) for _ in range(n)]

def scale_point_in_range(val, src, dst):
    ret = ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
    if ret < dst[0]:
        ret = dst[0]
    if ret > dst[1]:
        ret = dst[1]
    return ret

class Visualize:

    def __init__(self, r):
        self.root = r
        self.number_of_locations = 10
        self.location_gap = 0.5
        self.canvas_location_gap = 1
        self.ylim = 50
        self.xlim = 260
        self.canvas_x_range = [126, 900]
        self.canvas_y_range = [48, 355]
        self.bar_height = (self.ylim / self.number_of_locations) - (2 * self.location_gap)
        self.canvas_bar_height = 0
        self.location_distance = self.bar_height + (2 * self.location_gap)
        self.visible_x = [0, self.xlim]
        self.visible_y = [0, self.ylim]
        self.gantt = None
        self.scroll_unit = 30000000
        self.kd_store = None
        self.figure_width = 1000  # in pixel
        self.figure_height = 400  # in pixel
        self.clicked_point = None
        self.canvas = Canvas(self.root, width=self.figure_width, height=self.figure_height)
        self.canvas.grid(row=0, column=0)
        self.first_image = None
        self.original_image_object = None
        self.inside_figure = None
        self.itkimage = None

    def handlePanning(self, x_value, y_value):
        if self.clicked_point is not None:
            x_displace = self.clicked_point[0] - x_value
            # print(x_displace, x_value, self.clicked_point[0])
            if x_displace > 0:
                x_displace = min((self.kd_store.parsed_data.info['domain'][1] - self.visible_x[1]), x_displace)
            else:
                x_displace = max((self.kd_store.parsed_data.info['domain'][0] - self.visible_x[0]), x_displace)
            self.visible_x[0] += x_displace
            self.visible_x[1] += x_displace
            # print('visible x', self.visible_x)
            data = self.updateData()
            self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])

    def handleZoomIn(self, x_value, y_value):
        print(x_value, y_value, 'zoom-in')
        vis_mid = ((self.visible_x[0] + self.visible_x[1]) / 2)
        temp_displace = (x_value - vis_mid) / vis_mid * self.scroll_unit

        if self.visible_x[0] + (self.scroll_unit + temp_displace) < self.visible_x[1] - (-temp_displace + self.scroll_unit):
            self.visible_x[0] += (self.scroll_unit + temp_displace)
            self.visible_x[1] -= (-temp_displace + self.scroll_unit)

            data = self.updateData()
            self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])

    def handleZoomOut(self, x_value, y_value):
        vis_mid = ((self.visible_x[0] + self.visible_x[1]) / 2)
        temp_displace = (x_value - vis_mid) / vis_mid * self.scroll_unit

        self.visible_x[0] = max(self.kd_store.parsed_data.info['domain'][0], self.visible_x[0] - (self.scroll_unit + temp_displace))
        self.visible_x[1] = min(self.kd_store.parsed_data.info['domain'][1], self.visible_x[1] + (-temp_displace + self.scroll_unit))

        data = self.updateData()
        self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])

    def updateData(self):
        self.number_of_locations = len(self.kd_store.parsed_data.info['locationNames'])
        self.bar_height = (self.ylim / self.number_of_locations) - (2 * self.location_gap)
        self.canvas_bar_height = ((self.canvas_y_range[1] - self.canvas_y_range[0]) / self.number_of_locations) - (2 * self.canvas_location_gap)
        self.location_distance = self.bar_height + (2 * self.location_gap)
        begin_time = datetime.now().timestamp() * 1000
        data = self.kd_store.queryInRange(0, self.number_of_locations - 1, self.visible_x[0], self.visible_x[1], self.figure_width)
        time_taken = (datetime.now().timestamp() * 1000) - begin_time
        print("data fetch time taken", time_taken, "ms")
        return data

    def initiate_gantt_draw(self):
        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig, gnt = plt.subplots(figsize=(self.figure_width * px, self.figure_height * px))
        # fig.set_size_inches(12, 6)
        fig.canvas.callbacks.connect('scroll_event', self.mouse_scrolled)
        fig.canvas.callbacks.connect('button_press_event', self.mouse_clicked)
        fig.canvas.callbacks.connect('button_release_event', self.mouse_released)
        fig.canvas.callbacks.connect('motion_notify_event', self.mouse_moved)

        self.kd_store = KDStore()
        self.visible_x = copy.deepcopy(self.kd_store.parsed_data.info['domain'])

        data = self.updateData()
        # for i in range(self.number_of_locations):
        #     self.data[i] = generateRandomTasks(self.xlim)
        self.gantt = gnt
        self.inside_figure = fig
        self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'], False)
        return fig

    def _clear(self):
        if self.inside_figure:
            for item in self.inside_figure.canvas.get_tk_widget().find_all():
                self.inside_figure.canvas.get_tk_widget().delete(item)

    def update_gantt(self, data, location_names, is_click=True):
        begin_time = datetime.now().timestamp() * 1000
        def construct_location_name(d):
            a = int(d)
            c = 32
            node = a >> c
            thread = (int(d) & 0x0FFFFFFFF)
            aggText = ''
            aggText += str(node) + ' - T'
            aggText += str(thread)
            return aggText
        self.gantt.clear()
        self.gantt.grid(True)
        self.gantt.set_xlabel('Time (nanoseconds)')
        self.gantt.set_ylabel('Thread Location')
        self.gantt.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

        y_ticks = list(np.arange(self.location_gap + (self.bar_height / 2), self.ylim, self.location_distance))
        y_labels = [construct_location_name(location_names[i]) for i in range(self.number_of_locations)]
        y_labels.reverse()
        self.gantt.set_yticks(y_ticks)
        self.gantt.set_yticklabels(y_labels)

        self.gantt.set_ylim(self.visible_y[0], self.visible_y[1])
        self.gantt.set_xlim(self.visible_x[0], self.visible_x[1])
        self.scroll_unit = (self.visible_x[1] - self.visible_x[0]) / 10

        def get_bar_y_position(par, loc):
            return (loc * (par.canvas_bar_height + (2 * par.canvas_location_gap))) + par.canvas_location_gap + par.canvas_y_range[0]

        def get_bar_position(par, loc):
            return (loc * (par.bar_height + (2 * par.location_gap))) + par.location_gap

        def scale_length_in_x(val, src, dst):
            l = scale_point_in_range(0, src, dst)
            r = scale_point_in_range(val, src, dst)
            return r - l
        color = 'tab:blue'

        if is_click is True:
            self._clear()
        # if is_click is False:
        #     for i in range(self.number_of_locations):
        #         self.gantt.broken_barh(data[i], (get_bar_position(self, i), self.bar_height), facecolors=color)
        self.gantt.figure.canvas.draw()

        img = PIL.Image.frombytes('RGB', self.inside_figure.canvas.get_width_height(), self.inside_figure.canvas.tostring_rgb())
        idraw = ImageDraw.Draw(img)
        for i in range(self.number_of_locations):
            for bar in data[i]:
                idraw.rectangle(((scale_point_in_range(bar[0], self.visible_x, self.canvas_x_range), get_bar_y_position(self, i)),
                                 (scale_point_in_range(bar[1], self.visible_x, self.canvas_x_range),
                                  get_bar_y_position(self, i) + self.canvas_bar_height)),
                                fill="blue")
        # for i in range(1000):
        # idraw.rectangle(((200, 200), (300, 300)), fill="blue")
        # img.show()
        if self.itkimage is not None:
            del self.itkimage
        self.itkimage = ImageTk.PhotoImage(img)
        if self.first_image is None:
            self.first_image = vis.canvas.create_image(0, 0, anchor=NW, image=self.itkimage)
            self.canvas.bind("<MouseWheel>", vis.mouse_scroll_event_wrapper)
            self.canvas.pack()
        else:
            self.canvas.itemconfig(self.first_image, image=self.itkimage)

        time_taken = (datetime.now().timestamp() * 1000) - begin_time
        print("drawing time taken", time_taken, "ms")

    def mouse_scrolled(self, event):
        if event.inaxes is not None and event.button == 'up':
            self.handleZoomIn(event.xdata, event.ydata)
        elif event.inaxes is not None and event.button == 'down':
            self.handleZoomOut(event.xdata, event.ydata)
        else:
            print('Scrolled outside axes bounds but inside plot window')

    def mouse_clicked(self, event):
        if event.inaxes is not None:
            self.clicked_point = [event.xdata, event.ydata]
            # print(event.xdata, event.ydata, 'in clicked')
        else:
            print('Clicked outside axes bounds but inside plot window')

    def mouse_released(self, event):
        if event.inaxes is not None:
            # print(event.xdata, event.ydata, 'in released')
            # if self.clicked_point and self.clicked_point[0] != event.xdata and self.clicked_point[1] != event.ydata:
            #     print("mouse moved")
            # else:
            #     print("clicked in single place")
            self.clicked_point = None
        else:
            print('Released outside axes bounds but inside plot window')

    def mouse_moved(self, event):
        if self.clicked_point is not None:
            # print(event.xdata, event.ydata, 'mouse moved')
            if self.clicked_point[0] != event.xdata and self.clicked_point[1] != event.ydata:
                self.handlePanning(event.xdata, event.ydata)
                self.clicked_point = [event.xdata, event.ydata]
        # if event.inaxes is not None:
        #     print(event.xdata, event.ydata, 'in released')
        #     if self.clicked_point and self.clicked_point[0] != event.xdata and self.clicked_point[1] != event.ydata:
        #         print("mouse moved")
        #     else:
        #         print("clicked in single place")
        #     self.clicked_point = None
        # else:
        #     print('Released outside axes bounds but inside plot window')

    def mouse_scroll_event_wrapper(self, mouseEvent):
        if self.canvas_x_range[0] < mouseEvent.x < self.canvas_x_range[1] and self.canvas_y_range[0] < mouseEvent.y < self.canvas_y_range[1]:
            xdata = scale_point_in_range(mouseEvent.x, self.canvas_x_range, self.visible_x)
            ydata = scale_point_in_range(mouseEvent.y, self.canvas_y_range, self.visible_y)
            if mouseEvent.delta > 0:  # scroll up
                self.handleZoomIn(xdata, ydata)
            else:  # scroll down
                self.handleZoomOut(xdata, ydata)
            # data = self.updateData()
            # self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'], True)
        else:
            print('outside chart')


def fig2img(fig):
    return PIL.Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    # buf = io.BytesIO()
    # fig.savefig(buf)
    # buf.seek(0)
    # img = Image.open(buf)
    # return img



if __name__ == "__main__":
    root = Tk()
    root.title("Gantt")

    vis = Visualize(root)
    fig = vis.initiate_gantt_draw()


    root.mainloop()
