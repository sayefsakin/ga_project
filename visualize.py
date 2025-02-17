import copy
import io
import math
import tkinter
from tkinter.tix import Balloon

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
        self.old_text = None

    def handlePanning(self, x_value, pre_x):
        x_displace = pre_x - x_value
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
        # print(x_value, y_value, 'zoom-in')
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

        self.kd_store = KDStore()
        self.visible_x = copy.deepcopy(self.kd_store.parsed_data.info['domain'])

        data = self.updateData()
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

        self.gantt.figure.canvas.draw()

        img = PIL.Image.frombytes('RGB', self.inside_figure.canvas.get_width_height(), self.inside_figure.canvas.tostring_rgb())
        idraw = ImageDraw.Draw(img)
        for i in range(self.number_of_locations):
            for bar in data[i]:
                idraw.rectangle(((scale_point_in_range(bar[0], self.visible_x, self.canvas_x_range), get_bar_y_position(self, i)),
                                 (scale_point_in_range(bar[1], self.visible_x, self.canvas_x_range),
                                  get_bar_y_position(self, i) + self.canvas_bar_height)),
                                fill=bar[2])

        if self.itkimage is not None:
            del self.itkimage
        self.itkimage = ImageTk.PhotoImage(img)
        if self.first_image is None:
            self.first_image = vis.canvas.create_image(0, 0, anchor=NW, image=self.itkimage)
            self.canvas.bind("<MouseWheel>", vis.mouse_scroll_event_wrapper)
            self.canvas.bind("<B1-Motion>", vis.mouse_move_event_wrapper)
            self.canvas.bind("<ButtonRelease-1>", vis.mouse_release_event_wrapper)
            self.canvas.bind("<Button-1>", vis.mouse_click_event_wrapper)
            self.canvas.pack()
        else:
            self.canvas.itemconfig(self.first_image, image=self.itkimage)

        time_taken = (datetime.now().timestamp() * 1000) - begin_time
        print("drawing time taken", time_taken, "ms")

    def mouse_scroll_event_wrapper(self, mouseEvent):
        if self.old_text:
            self.canvas.delete(self.old_text)
        if self.canvas_x_range[0] < mouseEvent.x < self.canvas_x_range[1] and self.canvas_y_range[0] < mouseEvent.y < self.canvas_y_range[1]:
            xdata = scale_point_in_range(mouseEvent.x, self.canvas_x_range, self.visible_x)
            ydata = scale_point_in_range(mouseEvent.y, self.canvas_y_range, self.visible_y)
            if mouseEvent.delta > 0:  # scroll up
                self.handleZoomIn(xdata, ydata)
            else:  # scroll down
                self.handleZoomOut(xdata, ydata)
        else:
            print('outside chart')

    def mouse_move_event_wrapper(self, mouseEvent):
        if self.old_text:
            self.canvas.delete(self.old_text)
        if self.canvas_x_range[0] < mouseEvent.x < self.canvas_x_range[1] and self.canvas_y_range[0] < mouseEvent.y < self.canvas_y_range[1]:
            if self.clicked_point is not None:
                if self.clicked_point[0] != mouseEvent.x or self.clicked_point[1] != mouseEvent.y:
                    xdata = scale_point_in_range(mouseEvent.x, self.canvas_x_range, self.visible_x)
                    ydata = scale_point_in_range(mouseEvent.y, self.canvas_y_range, self.visible_y)
                    pre_x = scale_point_in_range(self.clicked_point[0], self.canvas_x_range, self.visible_x)
                    self.handlePanning(xdata, pre_x)
            self.clicked_point = [mouseEvent.x, mouseEvent.y]
        else:
            print('outside chart')

    def mouse_release_event_wrapper(self, mouseEvent):
        if self.canvas_x_range[0] < mouseEvent.x < self.canvas_x_range[1] and self.canvas_y_range[0] < mouseEvent.y < self.canvas_y_range[1]:
            self.clicked_point = None
        else:
            print('outside chart')

    def mouse_click_event_wrapper(self, mouseEvent):
        if self.canvas_x_range[0] < mouseEvent.x < self.canvas_x_range[1] and self.canvas_y_range[0] < mouseEvent.y < self.canvas_y_range[1]:

            def get_location_from_ydata(par, y_pos):
                return int((y_pos - par.canvas_location_gap - par.canvas_y_range[0]) / (par.canvas_bar_height + (2 * par.canvas_location_gap)))
            xdata = scale_point_in_range(mouseEvent.x, self.canvas_x_range, self.visible_x)
            loc_index = get_location_from_ydata(self, mouseEvent.y)
            loc = self.kd_store.parsed_data.info['locationNames'][loc_index]
            st_index = self.kd_store.parsed_data.sortedEventsByLocation[loc].bisect((xdata,))
            if self.old_text:
                self.canvas.delete(self.old_text)
            if self.kd_store.parsed_data.sortedEventsByLocation[loc][st_index-1][1]['Timestamp'] < xdata < self.kd_store.parsed_data.sortedEventsByLocation[loc][st_index][1]['Timestamp']\
                    and self.kd_store.parsed_data.sortedEventsByLocation[loc][st_index-1][1]['Event'] == 'ENTER':
                self.old_text = self.canvas.create_text(mouseEvent.x, mouseEvent.y, fill="black", font="Times 12",
                                                        text=self.kd_store.parsed_data.sortedEventsByLocation[loc][st_index][1]['Primitive'])
        else:
            print('outside chart')

if __name__ == "__main__":
    root = Tk()
    root.title("Gantt")

    vis = Visualize(root)
    fig = vis.initiate_gantt_draw()


    root.mainloop()
