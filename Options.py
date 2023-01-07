import tkinter as tk
mode = True
try:	
	import customtkinter as ctk
except:
	mode = False


#Add a way to adjust options.txt with GUI
class Options:
	def __init__(self, top_level):
		if mode == True:
			op = ctk.CTkToplevel(top_level)
			op.title("Help & Options")
			op.geometry("%ix%i" % (400,400))

			option_file = open("options.txt", "r")
			self.options = [l.split("\t")[1][:-1] for l in option_file.readlines()]
			option_file.close()

			self.buttons_frame = ctk.CTkFrame(master=op)

			self.windowsize_variable = tk.IntVar(value=self.options[0])
			self.xyseparator_variable = tk.StringVar(value=self.options[1])
			self.datatype_variable = tk.BooleanVar(value=eval(self.options[2]))
			self.gastype_variable = tk.DoubleVar(value=float(self.options[3]))
			self.ecurr_variable = tk.BooleanVar(value=eval(self.options[4]))
			

			self.windowsize_entry = ctk.CTkEntry(master=self.buttons_frame, textvariable=self.windowsize_variable) 
			self.xyseparator_entry = ctk.CTkEntry(master= self.buttons_frame, textvariable = self.xyseparator_variable)
			self.datatype_switch = ctk.CTkSwitch(master =  self.buttons_frame, variable = self.datatype_variable,textvariable=tk.StringVar(value=""))
			self.updater_button = ctk.CTkButton(master=self.buttons_frame, command = self.update_option_values, text="Write")
			self.gastype_entry = ctk.CTkEntry(master= self.buttons_frame, textvariable = self.gastype_variable)
			self.ecurr_switch = ctk.CTkSwitch(master= self.buttons_frame, variable = self.ecurr_variable,textvariable=tk.StringVar(value=""))


			self.windowsize_label = ctk.CTkLabel(master = self.buttons_frame, textvariable = tk.StringVar(value="Windowsize:")) 
			self.xyseparator_label = ctk.CTkLabel(master = self.buttons_frame, textvariable = tk.StringVar(value="XY Separator:")) 
			self.datatype_label= ctk.CTkLabel(master = self.buttons_frame, textvariable = tk.StringVar(value="Datatype:")) 
			self.gastype_label = ctk.CTkLabel(master=self.buttons_frame, textvariable = tk.StringVar(value="Gastype (AMU):"))
			self.ecurr_label = ctk.CTkLabel(master=self.buttons_frame, textvariable = tk.StringVar(value="Isat fit show:"))

		else:
			op = tk.Toplevel(top_level)
			op.title("Help & Options")
			op.geometry("%ix%i" % (400,400))

			option_file = open("options.txt", "r")
			self.options = [l.split("\t")[1][:-1] for l in option_file.readlines()]
			option_file.close()

			self.buttons_frame = tk.Frame(master=op)

			self.windowsize_variable = tk.IntVar(value=self.options[0])
			self.xyseparator_variable = tk.StringVar(value=self.options[1])
			self.datatype_variable = tk.BooleanVar(value=eval(self.options[2]))
			self.gastype_variable = tk.DoubleVar(value=float(self.options[3]))
			self.ecurr_variable = tk.BooleanVar(value=eval(self.options[4]))
			

			self.windowsize_entry = tk.Entry(master=self.buttons_frame, textvar=self.windowsize_variable) 
			self.xyseparator_entry = tk.Entry(master= self.buttons_frame, textvar = self.xyseparator_variable)
			self.datatype_switch = tk.Switch(master =  self.buttons_frame, variable = self.datatype_variable,textvariable=tk.StringVar(value=""))
			self.updater_button = tk.Button(master=self.buttons_frame, command = self.update_option_values, text="Write")
			self.gastype_entry = tk.Entry(master= self.buttons_frame, textvar = self.gastype_variable)
			self.ecurr_switch = tk.Switch(master= self.buttons_frame, variable = self.ecurr_variable,textvariable=tk.StringVar(value=""))


			self.windowsize_label = tk.Label(master = self.buttons_frame, textvar = tk.StringVar(value="Windowsize:")) 
			self.xyseparator_label = tk.Label(master = self.buttons_frame, textvar = tk.StringVar(value="XY Separator:")) 
			self.datatype_label= tk.Label(master = self.buttons_frame, textvar = tk.StringVar(value="Datatype:")) 
			self.gastype_label = tk.Label(master=self.buttons_frame, textvar = tk.StringVar(value="Gastype (AMU):"))
			self.ecurr_label = tk.Label(master=self.buttons_frame, textvar = tk.StringVar(value="Isat fit show:"))
			

		self.windowsize_entry.grid(row=0,column=1)
		self.xyseparator_entry.grid(row=1,column=1)
		self.datatype_switch.grid(row=2,column=1)
		self.gastype_entry.grid(row=3,column=1)
		self.ecurr_switch.grid(row=4,column=1)

		self.windowsize_label.grid(row=0,column=0)
		self.xyseparator_label.grid(row=1,column=0)
		self.datatype_label.grid(row=2,column=0)
		self.gastype_label.grid(row=3,column=0)
		self.ecurr_label.grid(row=4,column=0)

		self.updater_button.grid(row=5,column=0)


		self.buttons_frame.grid(row=0,column=0)

	def update_option_values(self):
		towrite = "windowsize:\t%i\n" % self.windowsize_variable.get()
		towrite += "xyseparator:\t%s\n" % self.xyseparator_variable.get()
		towrite += "datatype:\t%s\n" % str(self.datatype_variable.get())
		towrite += "gastype:\t%s\n" % str(self.gastype_variable.get())
		towrite += "ecurr_view:\t%s\n" % str(self.ecurr_variable.get())
	
		option_file = open("options.txt", "w")
		option_file.write(towrite)
		option_file.close()
