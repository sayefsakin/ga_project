from tkinter import *

#----------------------------------------------------------------------

class MainWindow():

    #----------------

    def __init__(self, main):

        # canvas for image
        self.canvas = Canvas(main, width=60, height=60)
        self.canvas.grid(row=0, column=0)

        # images
        self.my_images = []
        self.my_images.append(PhotoImage(file="data/ball1.gif"))
        self.my_images.append(PhotoImage(file="data/ball2.gif"))
        self.my_images.append(PhotoImage(file="data/ball3.gif"))
        self.my_image_number = 0

        # set first image on canvas
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.my_images[self.my_image_number])

        # button to change image
        self.button = Button(main, text="Change", command=self.onButton)
        self.button.grid(row=1, column=0)

    #----------------

    def onButton(self):

        # next image
        self.my_image_number += 1

        # return to first image
        if self.my_image_number == len(self.my_images):
            self.my_image_number = 0

        # change image
        self.canvas.itemconfig(self.image_on_canvas, image=self.my_images[self.my_image_number])

#----------------------------------------------------------------------

root = Tk()
MainWindow(root)
root.mainloop()



#
# import copy
# import io
#
# import PIL
# import numpy as np
# from tkinter import *
# import random
# import matplotlib
# from matplotlib import ticker, animation
# from datetime import datetime
# from data_store import KDStore
# from PIL import Image, ImageTk, ImageDraw
#
# matplotlib.use('TkAgg')
#
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
#
# def generateRandomTasks(x_max):
#     n = random.randint(5, 20)
#     return [(random.randint(0, x_max), random.randint(10, 30)) for _ in range(n)]
#
#
# class Visualize:
#
#     def __init__(self, r):
#         self.root = r
#         self.number_of_locations = 10
#         self.location_gap = 0.5
#         self.ylim = 50
#         self.xlim = 260
#         self.bar_height = (self.ylim / self.number_of_locations) - (2 * self.location_gap)
#         self.location_distance = self.bar_height + (2 * self.location_gap)
#         self.visible_x = [0, self.xlim]
#         self.visible_y = [0, self.ylim]
#         self.gantt = None
#         self.scroll_unit = 30000000
#         self.kd_store = None
#         self.figure_width = 1000  # in pixel
#         self.figure_height = 400  # in pixel
#         self.clicked_point = None
#         self.canvas = Canvas(self.root, width=self.figure_width, height=self.figure_height)
#         self.orig_image = None
#         self.canvas.bind("<Button-1>", self.find_intersections_wrapper)
#
#     def handlePanning(self, x_value, y_value):
#         if self.clicked_point is not None:
#             x_displace = self.clicked_point[0] - x_value
#             print(x_displace, x_value, self.clicked_point[0])
#             if x_displace > 0:
#                 x_displace = min((self.kd_store.parsed_data.info['domain'][1] - self.visible_x[1]), x_displace)
#             else:
#                 x_displace = max((self.kd_store.parsed_data.info['domain'][0] - self.visible_x[0]), x_displace)
#             self.visible_x[0] += x_displace
#             self.visible_x[1] += x_displace
#             print('visible x', self.visible_x)
#             data = self.updateData()
#             self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])
#
#     def handleZoomIn(self, x_value, y_value):
#         print(x_value, y_value, 'zoom-in')
#         # dont do the vertical zoom now
#         if self.visible_x[0] + (2 * self.scroll_unit) < self.visible_x[1]:
#             self.visible_x[0] = self.visible_x[0] + self.scroll_unit
#             self.visible_x[1] = self.visible_x[1] - self.scroll_unit
#
#             x_displace = x_value - ((self.visible_x[0] + self.visible_x[1]) / 2)
#             if x_displace > 0:
#                 x_displace = min((self.kd_store.parsed_data.info['domain'][1] - self.visible_x[1]), x_displace)
#             else:
#                 x_displace = max((self.kd_store.parsed_data.info['domain'][0] - self.visible_x[0]), x_displace)
#             self.visible_x[0] += x_displace
#             self.visible_x[1] += x_displace
#
#             data = self.updateData()
#             self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])
#
#     def handleZoomOut(self, x_value, y_value):
#         print(x_value, y_value, 'zoom-out', self.kd_store.parsed_data.info['domain'][0])
#         # if (self.visible_x[0] - self.scroll_unit) >= self.kd_store.parsed_data.info['domain'][0] and \
#         #         (self.visible_x[1] + self.scroll_unit) <= self.kd_store.parsed_data.info['domain'][1]:
#         t_x = [self.visible_x[0] - self.scroll_unit, self.visible_x[1] + self.scroll_unit]
#
#         x_displace = x_value - ((t_x[0] + t_x[1]) / 2)
#         if x_displace > 0:
#             x_displace = min((self.kd_store.parsed_data.info['domain'][1] - t_x[1]), x_displace)
#         else:
#             x_displace = max((self.kd_store.parsed_data.info['domain'][0] - t_x[0]), x_displace)
#         t_x[0] += x_displace
#         t_x[1] += x_displace
#
#         if t_x[0] >= self.kd_store.parsed_data.info['domain'][0] and t_x[1] <= self.kd_store.parsed_data.info['domain'][1]:
#             self.visible_x[0] = t_x[0]
#             self.visible_x[1] = t_x[1]
#
#         data = self.updateData()
#         self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])
#
#     def updateData(self):
#         self.number_of_locations = len(self.kd_store.parsed_data.info['locationNames'])
#         self.bar_height = (self.ylim / self.number_of_locations) - (2 * self.location_gap)
#         self.location_distance = self.bar_height + (2 * self.location_gap)
#         begin_time = datetime.now().timestamp() * 1000
#         data = self.kd_store.queryInRange(0, self.number_of_locations - 1, self.visible_x[0], self.visible_x[1], self.figure_width)
#         time_taken = (datetime.now().timestamp() * 1000) - begin_time
#         print("data fetch time taken", time_taken, "ms")
#         return data
#
#     def initiate_gantt_draw(self):
#         px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
#         fig, gnt = plt.subplots(figsize=(self.figure_width * px, self.figure_height * px))
#         # fig.set_size_inches(12, 6)
#         fig.canvas.callbacks.connect('scroll_event', self.mouse_scrolled)
#         fig.canvas.callbacks.connect('button_press_event', self.mouse_clicked)
#         fig.canvas.callbacks.connect('button_release_event', self.mouse_released)
#         fig.canvas.callbacks.connect('motion_notify_event', self.mouse_moved)
#
#
#
#         self.kd_store = KDStore()
#         self.visible_x = copy.deepcopy(self.kd_store.parsed_data.info['domain'])
#
#         data = self.updateData()
#         # for i in range(self.number_of_locations):
#         #     self.data[i] = generateRandomTasks(self.xlim)
#         self.gantt = gnt
#         self.update_gantt(data, self.kd_store.parsed_data.info['locationNames'])
#         return fig
#
#     def update_gantt(self, data, location_names):
#         begin_time = datetime.now().timestamp() * 1000
#         def construct_location_name(d):
#             a = int(d)
#             c = 32
#             node = a >> c
#             thread = (int(d) & 0x0FFFFFFFF)
#             aggText = ''
#             aggText += str(node) + ' - T'
#             aggText += str(thread)
#             return aggText
#         self.gantt.clear()
#         self.gantt.grid(True)
#         self.gantt.set_xlabel('Time (nanoseconds)')
#         self.gantt.set_ylabel('Thread Location')
#         self.gantt.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
#
#         y_ticks = list(np.arange(self.location_gap + (self.bar_height / 2), self.ylim, self.location_distance))
#         y_labels = [construct_location_name(location_names[i]) for i in range(self.number_of_locations)]
#         self.gantt.set_yticks(y_ticks)
#         self.gantt.set_yticklabels(y_labels)
#
#         self.gantt.set_ylim(self.visible_y[0], self.visible_y[1])
#         self.gantt.set_xlim(self.visible_x[0], self.visible_x[1])
#
#         def get_bar_position(par, loc):
#             return (loc * (par.bar_height + (2 * par.location_gap))) + par.location_gap
#
#         color = 'tab:blue'
#
#         for i in range(self.number_of_locations):
#             self.gantt.broken_barh(data[i], (get_bar_position(self, i), self.bar_height), facecolors=color)
#         self.gantt.figure.canvas.draw()
#
#
#
#
#
#         img = PIL.Image.frombytes('RGB', self.gantt.figure.canvas.get_width_height(), self.gantt.figure.canvas.tostring_rgb())
#
#         draw = ImageDraw.Draw(img)
#         # draw.rectangle(((0, 00), (100, 100)), fill="black")
#         # img.show()
#         #
#         #Convert To photoimage
#         tkimage = ImageTk.PhotoImage(img)
#         # if self.orig_image is not None:
#         #     self.canvas.itemconfig(self.orig_image, image=tkimage)
#
#         # #Create a canvas
#         # canvas = Canvas(self.root, width=self.figure_width, height=self.figure_height)
#         self.orig_image = self.canvas.create_image(0, 0, anchor=NW, image=tkimage)
#         self.canvas.pack()
#         #
#         #
#         # self.root.mainloop()
#
#
#
#
#
#
#         time_taken = (datetime.now().timestamp() * 1000) - begin_time
#         print("drawing time taken", time_taken, "ms")
#
#     def mouse_scrolled(self, event):
#         if event.inaxes is not None and event.button == 'up':
#             self.handleZoomIn(event.xdata, event.ydata)
#         elif event.inaxes is not None and event.button == 'down':
#             self.handleZoomOut(event.xdata, event.ydata)
#         else:
#             print('Scrolled outside axes bounds but inside plot window')
#
#     def mouse_clicked(self, event):
#         if event.inaxes is not None:
#             self.clicked_point = [event.xdata, event.ydata]
#             print(event.xdata, event.ydata, 'in clicked')
#         else:
#             print('Clicked outside axes bounds but inside plot window')
#
#     def mouse_released(self, event):
#         if event.inaxes is not None:
#             print(event.xdata, event.ydata, 'in released')
#             if self.clicked_point and self.clicked_point[0] != event.xdata and self.clicked_point[1] != event.ydata:
#                 print("mouse moved")
#             else:
#                 print("clicked in single place")
#             self.clicked_point = None
#         else:
#             print('Released outside axes bounds but inside plot window')
#
#     def mouse_moved(self, event):
#         if self.clicked_point is not None:
#             print(event.xdata, event.ydata, 'mouse moved')
#             if self.clicked_point[0] != event.xdata and self.clicked_point[1] != event.ydata:
#                 self.handlePanning(event.xdata, event.ydata)
#                 self.clicked_point = [event.xdata, event.ydata]
#         # if event.inaxes is not None:
#         #     print(event.xdata, event.ydata, 'in released')
#         #     if self.clicked_point and self.clicked_point[0] != event.xdata and self.clicked_point[1] != event.ydata:
#         #         print("mouse moved")
#         #     else:
#         #         print("clicked in single place")
#         #     self.clicked_point = None
#         # else:
#         #     print('Released outside axes bounds but inside plot window')
#
#     def setOrigImage(self, oi):
#         self.orig_image = oi
#
#     def find_intersections_wrapper(self, clickEvent):
#         print('on click event happened')
#         img = PIL.Image.frombytes('RGB', self.gantt.figure.canvas.get_width_height(), self.gantt.figure.canvas.tostring_rgb())
#
        # draw = ImageDraw.Draw(img)
        # draw.rectangle(((0, 00), (100, 100)), fill="black")
        # # img.show()
#
#         #Convert To photoimage
#         tkimage = ImageTk.PhotoImage(img)
#         if self.orig_image is not None:
#             self.canvas.itemconfig(self.orig_image, image=tkimage)
#         # self.canvas.after(1, self.find_intersections_wrapper)
#         self.root.mainloop()
#
#
# def fig2img(fig):
#     return PIL.Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
#     # buf = io.BytesIO()
#     # fig.savefig(buf)
#     # buf.seek(0)
#     # img = Image.open(buf)
#     # return img
#
#
#
#
# if __name__ == "__main__":
#     root = Tk()
#     root.title("Gantt")
#     # YSIZE = 800
#     # root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")
#
#     vis = Visualize(root)
#     fig = vis.initiate_gantt_draw()
#     # fig = plt.figure(1)
#     # plt.ion()
#     # t = np.arange(0.0,3.0,0.01)
#     # s = np.sin(np.pi*t)
#     # plt.plot(t,s)
#
#     # canvas = FigureCanvasTkAgg(fig, master=root)
#     # plot_widget = canvas.get_tk_widget()
#     #
#     #
#     # plot_widget.grid(row=0, column=0)
#     # tk.Button(root,text="Update",command=update).grid(row=1, column=0)
#
#
#     # #Convert To photoimage
#     # img = fig2img(fig)
#     # tkimage = ImageTk.PhotoImage(img)
#     # #Create a canvas
#     #
#     # orig_image = vis.canvas.create_image(0, 0, anchor=NW, image=tkimage)
#     # vis.canvas.pack()
#     # vis.setOrigImage(orig_image)
#     vis.root.mainloop()
