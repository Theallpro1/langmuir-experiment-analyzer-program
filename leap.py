import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import os
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import numpy as np
import sys
from matplotlib import pyplot as plt
import data_manipulator
import platform
import math

ctk.set_appearance_mode("Dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

plt.style.use("default")

# Optional starting directory
try:
	starting_dir = sys.argv[1]
except:
	starting_dir = "~"


# fit using np.where not working if the datapoints dont align with integer voltages
# When adding a product of an original graph it is possible to add multiples. Fix this.
# vspace
# xi: = probe radius/ debye length
# formula for debye using epsilong * KT/ne^2
# when doing manipulations improve the name of the new file

class App(ctk.CTk):
	def __init__(self):
		super().__init__()

		# Set up the basic window things
		self.WIDTH = 1400
		self.HEIGHT = 5000
		self.title("Langmuir Experiment Analyzer Program")
		self.geometry("%ix%i" % (self.WIDTH, self.HEIGHT))
		if platform.system() == "Darwin":
			self.img = tk.Image("photo", file="icon.png")
			self.tk.call('wm', 'iconphoto', self._w, self.img)
		self.data_analyzer = data_manipulator.data_manipulator()

		option_file = open("options.txt", "r")
		self.options = [l.split("\t")[1][:-1] for l in option_file.readlines()]
		option_file.close()

		# This list holds the filenames of the graphs that are displayed, along with their data
		self.currently_displayed = {}
		self.selector_display = {}
		self.lin_log = 0
		if self.options[2] == "False":
			self.data_type_old = False
		else:
			self.data_type_old = True
		if self.options[1] == "\\t":
			self.xy_split = "\t"
		else:
			self.xy_split = self.options[1]
		self.next_index = 0
		self.select_all = tk.IntVar()
		self.legend_visibility = False
		self.cursor_visibility = [tk.IntVar(value=0), tk.IntVar(value=0)]
		self.fit_bound = [tk.IntVar(value=0), tk.IntVar(value=0)]
		self.cursor_positions = []
		self.graph_indexes = {"cursor1" : 0, "cursor2" : 1}
		self.temperature = tk.StringVar(value = "---")
		self.floating_potential = tk.DoubleVar()

		# Frames
		self.left_frame = ctk.CTkFrame()
		self.right_frame = ctk.CTkFrame()

		self.graph_frame = ctk.CTkFrame(master = self.left_frame) 	# Holds the graph
		self.adding_frame = ctk.CTkFrame(master = self.left_frame)	# Holds the controls for adding and removing files from the graph.


		self.control_frame = ctk.CTkFrame(master = self.right_frame)# Holds the controls for manipulating the graphs.
		self.middle_frame = ctk.CTkFrame(master = self.right_frame)
		self.selector_frame = ctk.CTkFrame(master = self.middle_frame)
		self.select_all_frame = ctk.CTkFrame(master = self.selector_frame)

		self.options_frame = ctk.CTkFrame(master = self.control_frame)
		self.math_frame = ctk.CTkFrame(master = self.control_frame)
		self.useless_frame  = ctk.CTkFrame(master = self.control_frame)

		self.cursor_frame = ctk.CTkFrame(master = self.options_frame)



		""" RESULTS FRAMES """
		self.results_frame = ctk.CTkFrame(master = self.middle_frame)
		self.temperature_frame = ctk.CTkFrame(master = self.results_frame)
		self.temperature_button = ctk.CTkButton(master = self.temperature_frame,
			command = self.temp_fit,
			text = "kTe:",
			height = 30,
			width = 30)
		self.temperature_label = ctk.CTkLabel(master = self.temperature_frame,
			textvar = self.temperature)
		self.floating_frame = ctk.CTkFrame(master = self.results_frame)
		self.floating_potential_button = ctk.CTkButton(master = self.floating_frame,
			command = self.floating,
			text = "Vf:",
			height = 30,
			width = 30)
		self.floating_label = ctk.CTkLabel(master = self.floating_frame,
			textvar = self.floating_potential)
		self.probe_area_frame = ctk.CTkFrame(master = self.results_frame)
		self.probe_area_input = ctk.CTkEntry(master = self.probe_area_frame,
			width = 120,
			height = 25,
			corner_radius = 10)
		self.probe_area_label = ctk.CTkLabel(master = self.probe_area_frame,
			text = "Ap (cm^2):")

		# The figure that will contain the plot and adding the plot
		self.fig = Figure(figsize = (int(self.options[0]),int(self.options[0])), dpi = 100)
		self.plot1 = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.graph_frame)
		self.canvas.get_tk_widget().pack()

		self.toolbar = NavigationToolbar2Tk(self.canvas, self.useless_frame)
		self.toolbar.update()
		self.cursor1 = self.plot1.axvline(x=self.fit_bound[0].get(),linestyle = "None")
		self.cursor2 = self.plot1.axvline(x=self.fit_bound[1].get(),linestyle = "None")
		self.canvas.draw()

		""" ADDING FRAME """

		self.explorer_button = ctk.CTkButton(master = self.adding_frame,
			command = self.file_browser,
			text = "explorer")
		self.deletion_button = ctk.CTkButton(master = self.adding_frame,
			command = self.delete_file,
	                text = "Delete")
		self.save_button = ctk.CTkButton(master = self.adding_frame,
			command = self.save_data,
			text = "save")
		self.zoom_button = ctk.CTkButton(master = self.adding_frame,
			command = self.fig.canvas.toolbar.zoom,
			text = "zoom")
		self.pan_button = ctk.CTkButton(master = self.adding_frame,
			command = self.fig.canvas.toolbar.pan,
			text = "pan")



		self.plus_button = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(1,1),
			text = ">",
			width = 5)
		self.plus_button_l = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(10,1),
			text = ">>",
			width = 5)
		self.minus_button = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(1,1),
			text = "<",
			width = 5)
		self.minus_button_l = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(10,1),
			text = "<<",
			width = 5)
		self.plus_button_2 = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(1,2),
			text = ">",
			width = 5)
		self.plus_button_l_2 = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(10,2),
			text = ">>",
			width = 5)
		self.minus_button_2 = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(1,2),
			text = "<",
			width = 5)
		self.minus_button_l_2 = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(10,2),
			text = "<<",
			width = 5)

		self.rescale_button = ctk.CTkButton(master = self.options_frame,
			command = self.rescale,
			text = "Rescale")
		self.derivative_button = ctk.CTkButton(master = self.math_frame,
			command = self.derivative,
			text = "f'")
		self.scale_button = ctk.CTkButton(master = self.options_frame,
			command = self.toggle_graph_scale,
			text = "lin/log")
		self.legend_button = ctk.CTkButton(master = self.options_frame,
			command = self.toggle_legend,
			text = "legend")
		self.box_button = ctk.CTkButton(master = self.math_frame,
			command = self.box_average,
			text = "box average")
		self.select_all_button = ctk.CTkCheckBox(master = self.select_all_frame,
			command = self.all,
			variable = self.select_all,
			text = "")
		self.average_button = ctk.CTkButton(master = self.math_frame,
			command = self.average,
			text = "average")
		self.square_button = ctk.CTkButton(master = self.math_frame,
			command = self.square,
			text = "f^2")
		self.basic_isat_button = ctk.CTkButton(master = self.math_frame,
			command = self.basic_isat,
			text = "basic isat")
		self.savgol_button = ctk.CTkButton(master = self.math_frame,
			command = self.savgol,
			text = "savgol filter")
		self.eedf_button = ctk.CTkButton(master = self.math_frame,
			command = self.eedf,
			text = "EEDF",
			fg_color="red")
		self.plasma_potential_button = ctk.CTkButton(master= self.math_frame,
			command = self.plasma_potential,
			text = "plasma potential")
		self.absolute_button = ctk.CTkButton(master = self.math_frame,
			command = self.absolute_v,
			text = "|f|")
		self.natural_log_button = ctk.CTkButton(master = self.math_frame,
			command = self.natural,
			text = "ln")
		self.oml_button = ctk.CTkButton(master = self.math_frame,
			command = self.oml,
			text = "oml")

		self.fit_counter = ctk.CTkLabel(master = self.cursor_frame, textvar = self.fit_bound[0])
		self.fit_counter_2 = ctk.CTkLabel(master = self.cursor_frame, textvar = self.fit_bound[1])
		self.cursor_show_button = ctk.CTkCheckBox(master = self.cursor_frame,
			command = lambda: self.hide_cursor(1),
			variable = self.cursor_visibility[0],
			text = "")
		self.cursor_show_button_2 = ctk.CTkCheckBox(master = self.cursor_frame,
			command = lambda: self.hide_cursor(2),
			variable = self.cursor_visibility[1],
			text = "")

		self.select_all_label = ctk.CTkLabel(master = self.select_all_frame, text = "Select All:")

		# Put the widgets on the screen
		self.redraw_widgets()

	def redraw_widgets(self):
		self.grid_columnconfigure(0,weight=1)
		self.grid_columnconfigure(1,weight=1)
		self.grid_rowconfigure(0,weight=1)

		self.left_frame.grid(row=0, column = 0, sticky="nsew")
		self.right_frame.grid(row=0, column = 1, sticky="nsew")

		self.left_frame.grid_rowconfigure(0, weight = 4)
		self.left_frame.grid_rowconfigure(1, weight = 1)
		self.left_frame.grid_columnconfigure(0, weight = 1)

		self.graph_frame.grid(row=0, column = 0, sticky = "nsew")
		self.adding_frame.grid(row=1, column = 0, sticky = "nsew")

		self.explorer_button.grid(row=0, column=0, sticky = "nsew")
		self.deletion_button.grid(row=0, column=1, sticky = "nsew")
		self.save_button.grid(row=0, column=2, sticky = "nsew")
		self.zoom_button.grid(row=0, column=3, sticky = "nsew")
		self.pan_button.grid(row=0, column=4, sticky = "nsew")

		self.right_frame.grid_columnconfigure(0, weight=1)
		self.right_frame.grid_columnconfigure(1, weight=1)
		self.right_frame.grid_rowconfigure(0, weight=1)
		self.middle_frame.grid(row=0, column=0, sticky = "nsew")
		self.selector_frame.grid(row=0, column=0, sticky = "nsew")
		self.results_frame.grid(row=1, column=0, sticky = "nsew")
		self.control_frame.grid(row=0, column=1, sticky = "nswe")

		self.control_frame.grid_columnconfigure(0, weight=1)
		self.control_frame.grid_rowconfigure(0, weight=1)
		self.control_frame.grid_rowconfigure(1, weight=2)

		self.options_frame.grid(row=0, column=0)
		self.math_frame.grid(row=1, column=0)

		self.select_all_frame.pack()
		self.select_all_label.grid(row=0, column=0)
		self.select_all_button.grid(row=0, column=1)

		self.temperature_frame.pack()
		self.temperature_button.grid(row = 0, column = 0)
		self.temperature_label.grid(row = 0, column = 1)
		self.floating_frame.pack()
		self.floating_potential_button.grid(row = 0, column = 0)
		self.floating_label.grid(row = 0, column = 1)
		self.probe_area_frame.pack()
		self.probe_area_label.grid(row = 0, column = 0)
		self.probe_area_input.grid(row = 0, column = 1)

		self.scale_button.pack()
		self.legend_button.pack()
		self.rescale_button.pack()

		self.derivative_button.pack()
		self.box_button.pack()
		self.average_button.pack()
		self.basic_isat_button.pack()
		self.savgol_button.pack()
		self.eedf_button.pack()
		self.plasma_potential_button.pack()
		self.absolute_button.pack()
		self.natural_log_button.pack()
		self.square_button.pack()
		self.oml_button.pack()

		self.cursor_frame.pack()
		self.minus_button_l.grid(row=0,column=0)
		self.minus_button.grid(row=0,column=1)
		self.plus_button.grid(row=0,column=3)
		self.plus_button_l.grid(row=0,column=4)
		self.fit_counter.grid(row=0,column=2)
		self.cursor_show_button.grid(row=0,column=5)
		self.minus_button_l_2.grid(row=1,column=0)
		self.minus_button_2.grid(row=1,column=1)
		self.plus_button_2.grid(row=1,column=3)
		self.plus_button_l_2.grid(row=1,column=4)
		self.fit_counter_2.grid(row=1,column=2)
		self.cursor_show_button_2.grid(row=1,column=5)

	def square(self):
		fname = self.get_selected()[0]
		sq = np.square(self.currently_displayed[fname][1])
		self.add_graph(fname + "_sav", self.currently_displayed[fname][0], sq)

	def hide_cursor(self, n):
		if n == 1:
			if self.cursor1.get_linestyle() == "None":
				self.cursor1.set_linestyle("solid")
			else:
				self.cursor1.set_linestyle("None")
		elif n == 2:
			if self.cursor2.get_linestyle() == "None":
				self.cursor2.set_linestyle("solid")
			else:
				self.cursor2.set_linestyle("None")

		self.canvas.draw()

	def absolute_v(self):
		fname = self.get_selected()[0]
		a = self.data_analyzer.absolute_val(self.currently_displayed[fname])[1]
		self.add_graph(fname + "_sav", self.currently_displayed[fname][0], a)

	def save_data(self):
		fname = self.get_selected()[0]
		data = self.currently_displayed[fname]
		data_to_write = ""
		for i in range(len(data[0])):
			data_to_write += str(data[0][i])
			data_to_write += self.xy_split
			data_to_write += str(data[1][i])
			data_to_write += "\n"

		data_to_write = data_to_write[:-1]
		f = open(fname + "_new_write", "w")
		f.write(data_to_write)
		f.close()

	def plasma_potential(self):
		fname = self.get_selected()[0]
		asdfasdf = self.data_analyzer.plasma_potential(self.currently_displayed[fname])
		print(asdfasdf)
		return asdfasdf

	def eedf(self):
		fname = self.get_selected()[0]
		print(self.currently_displayed[fname])
		vp = float(input("V_p?: "))
		ee = self.data_analyzer.druyvesteyn(self.currently_displayed[fname],vp)
		self.add_graph(fname + "_ee", self.currently_displayed[fname][0], ee)

	def savgol(self):
		fname = self.get_selected()[0]
		smoothed = self.data_analyzer.savgol_smoothing(self.currently_displayed[fname])
		self.add_graph(fname + "_sav", self.currently_displayed[fname][0], smoothed)


	# Get rid of the try except
	def basic_isat(self):
		fname = self.get_selected()[0]
		data_t = self.currently_displayed[fname]
		isat,electron_current = self.data_analyzer.ion_saturation_basic(data_t,np.where(data_t[0] == self.fit_bound[0].get())[0][0],np.where(data_t[0] == self.fit_bound[1].get())[0][0])
		self.add_graph(fname + "_isat", self.currently_displayed[fname][0], isat)
		self.add_graph(fname + "_ecurr", self.currently_displayed[fname][0], electron_current)

	def oml(self):
		print("oml")

	def file_browser(self):
		#try:
			fnames = tk.filedialog.askopenfilenames(initialdir = starting_dir, title = "Select a File", filetypes = [("csv files", "*.csv"),("data files", "*.txt"),  ("all files","*.*")])
			for fname in fnames:
				if fname not in self.selector_display.keys():
					[x,y] = self.get_data(fname)
					self.add_graph(fname, x, y)
					print("!")
		#except:
		#	pass

	def floating(self):
		fname = self.get_selected()[0]
		fp = self.data_analyzer.floating_potential(self.currently_displayed[fname])
		self.floating_potential.set(fp[0])

	def all(self):
		v = self.select_all.get()
		for key in self.selector_display:
			self.selector_display[key][1].set(v)

	def toggle_legend(self):
		if self.legend_visibility == False:
			self.legend_visibility = True
			self.plot1.legend(self.currently_displayed.keys())
		elif self.legend_visibility == True:
			self.legend_visibility = False
			self.plot1.get_legend().remove()
		self.canvas.draw()

	def toggle_graph_scale(self):
		if self.lin_log == 0:
			self.lin_log = 1
			self.plot1.set_yscale("log")
		elif self.lin_log == 1:
			self.lin_log = 0
			self.plot1.set_yscale("linear")
		self.canvas.draw()

	def rescale(self):
		xs = []
		ys = []
		for v1 in self.currently_displayed:
			xs.extend(list(self.currently_displayed[v1][0]))
			ys.extend(list(self.currently_displayed[v1][1]))

		minxs = float(min(xs))
		minys = float(min(ys))
		maxxs = float(max(xs))
		maxys = float(max(ys))
		print(minxs, maxxs, minys, maxys)

		self.plot1.set_xlim(minxs,maxxs)
		self.plot1.set_ylim(minys,maxys)
		self.canvas.draw()

	def get_selected(self):
		selected = []
		for key in self.selector_display:
			if self.selector_display[key][0].winfo_children()[1].get() == 1:
				selected.append(key)
		return selected

	def box_average(self):
		for fname in self.get_selected():
			try:
				data = self.data_analyzer.box_average(self.currently_displayed[fname])
				prelim_fname = fname.split("/")[-1].split(".")[0] + "_box." + fname.split("/")[-1].split(".")[1]
				if prelim_fname not in list(self.graph_indexes.keys()):
					self.add_graph(prelim_fname, data[0], data[1])

			except KeyError:
				print("\a")

	# BETTER NAMES
	def average(self):
		data_to_average = []
		for fname in self.get_selected():
			data_to_average.append(self.currently_displayed[fname])
		# TODO broken
		data = self.data_analyzer.average(data_to_average)
		self.add_graph("average", data[0], data[1])

	def incr(self,n,cnum):
		self.fit_bound[cnum-1].set(self.fit_bound[cnum-1].get()+n)
		if cnum == 1:
			self.cursor1.set_xdata(self.fit_bound[cnum-1].get())
		if cnum == 2:
			self.cursor2.set_xdata(self.fit_bound[cnum-1].get())
		self.canvas.draw()

	def minu(self,n,cnum):
		self.fit_bound[cnum-1].set(self.fit_bound[cnum-1].get()-n)
		if cnum == 1:
			self.cursor1.set_xdata(self.fit_bound[cnum-1].get())
		if cnum == 2:
			self.cursor2.set_xdata(self.fit_bound[cnum-1].get())
		self.canvas.draw()

	def temp_fit(self):
		fname = self.get_selected()[0]
		data_t = self.currently_displayed[fname]
		temp_fit_lower = np.where(data_t[0] == self.fit_bound[0].get())[0][0]
		temp_fit_upper = np.where(data_t[0] == self.fit_bound[1].get())[0][0]
		temps = []
		for upper_bound in range(temp_fit_lower, temp_fit_upper+1):
			for lower_bound in range(temp_fit_lower, upper_bound):
				if abs(lower_bound-upper_bound) == 1:
					pass
				else:
					m,b = np.polyfit(data_t[0][lower_bound:upper_bound], data_t[1][lower_bound:upper_bound], 1)
					temps.append(1/m)

		temps = np.array(temps)
		av = np.average(temps)
		std = np.std(temps)

		self.temperature.set(str(av) + " +- " + str(std))

		print("Temp: ", av)
		print("Bounds: %f to %f" % (av - std, av + std) )

	def derivative(self):
		for fname in self.get_selected():
			try:
				data = self.data_analyzer.derivative(self.currently_displayed[fname],1)
				prelim_fname = fname.split("/")[-1].split(".")[0] + "_der." + fname.split("/")[-1].split(".")[1]
				if prelim_fname not in list(self.graph_indexes.keys()):
					self.add_graph(prelim_fname, data[0], data[1])
			except KeyError:
				print("\a")

	def natural(self):
		for fname in self.get_selected():
			try:
				data = [self.currently_displayed[fname][0],np.log(self.currently_displayed[fname][1])]
				prelim_fname = fname.split("/")[-1].split(".")[0] + "_ln." + fname.split("/")[-1].split(".")[1]
				if prelim_fname not in list(self.graph_indexes.keys()):
					self.add_graph(prelim_fname, data[0], data[1])
			except KeyError:
				print("\a")



	def get_data(self, fname):
		if self.data_type_old == True:
			f = open(fname, "r")
			vi_data = f.readlines()
			f.close()
			# Fix the data into a format usable by the code
			vi_data = vi_data[0]
			vi_data = vi_data.split(",")
			x = np.array([float(vi_data[i]) for i in range(len(vi_data)) if i % 2 == 0])
			y = np.array([float(vi_data[i]) for i in range(len(vi_data)) if i % 2 == 1])
		else:
			f = open(fname, "r")
			vi_data = f.readlines()
			f.close()
			x = np.array([float(vi_data[i].split(self.xy_split)[0]) for i in range(len(vi_data))])
			y = np.array([float(vi_data[i].split(self.xy_split)[1]) for i in range(len(vi_data))])


		################# EXPERIMENTAL #################

		avv = np.average(y)
		for i in range(1,len(y)-1):
			if abs(y[i]-avv) >= 0.1:
				y[i] = (y[i+1] + y[i-1])/2

		return x,y

	def add_graph(self, f, x, y):
		self.currently_displayed.update({f: [x,y]})

		file_frame = ctk.CTkFrame(master = self.selector_frame)

		cb_value = tk.IntVar()
		label = ctk.CTkLabel(master = file_frame, text = f.split("/")[-1])
		cb = ctk.CTkCheckBox(master = file_frame, text = "",variable = cb_value)

		self.selector_display.update({f: [file_frame,cb_value]})
		self.update_next_index()
		self.graph_indexes.update({f: self.next_index})

		self.plot(x,y)
		file_frame.pack()
		label.grid(row=0, column=0)
		cb.grid(row=0, column=1)

	def update_next_index(self):
		indexes = list(self.graph_indexes.values())
		indexes.sort()
		i=0
		while i in indexes:
			i += 1

		self.next_index = i

	def delete_file(self):
		for s in self.get_selected():
			self.currently_displayed.pop(s)
			self.selector_display[s][0].pack_forget()
			self.selector_display[s][0].destroy()
			self.selector_display.pop(s)
			self.plot1.get_lines()[self.graph_indexes[s]].remove()
			i = self.graph_indexes[s]
			del self.graph_indexes[s]
			for e in self.graph_indexes:
				if self.graph_indexes[e] > i:
					self.graph_indexes[e] -= 1

		self.canvas.draw()

	def plot(self,x,y):
		self.plot1.plot(x,y,'o')
		self.canvas.draw()


if __name__ == "__main__":
	app = App()
	app.mainloop()
