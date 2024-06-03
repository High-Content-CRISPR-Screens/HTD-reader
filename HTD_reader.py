"""
HTD Reader by Dias, André (2024)
This script opens htd files fol high-throughput screens inside of FIJI 
by allowing one to select a well and site location."

"""

# --- Imports ---
import os
from ij import IJ
from ij.plugin import Concatenator
from ij.gui import NonBlockingGenericDialog

# --- Classes / Functions ---
def create_gui(def_val=[]):
	if def_val == []:
		def_val = {
			"file_path": "",
			"well_id": "A01",
			"site_no": "01"
		}
	# --- Create an instance of GenericDialogPlus ---
	gui = NonBlockingGenericDialog("HTD Reader")
	gui.addFileField("Image:", def_val["file_path"])
	
	gui.addMessage("______________________________________")
	gui.addMessage("")
	
	gui.addStringField("               Well ID :", def_val["well_id"])
	
	gui.addMessage("______________________________________")
	gui.addMessage("")
	
	gui.addStringField("               Site no :", def_val["site_no"])
	
	gui.hideCancelButton()
	gui.setOKLabel("Open Image")
	
	# --- Show the GUI ---
	gui.showDialog()
	if gui.wasOKed():
		file_path = gui.getNextString()
		well_id = gui.getNextString().upper()
		site_no = int(gui.getNextString())
		prefs = {
			"file_path": file_path,
			"well_id": well_id,
			"site_no": str(site_no)
		}
		open_htd(file_path, well_id, site_no)
		gui.dispose()
		create_gui(prefs)

def open_htd(file_path, well_id, site_no):
	htd_name = os.path.basename(file_path)
	main_dir = os.path.dirname(file_path)
	files_in_main_dir = os.listdir(main_dir)
	image_folders = [folder for folder in files_in_main_dir if os.path.isdir(os.path.join(main_dir,folder))]
	n_timepoints = len(image_folders) # Get the number of timepoints.
	
	# Read the images data and detect the number of channels using timepoint 1.
	dir_timepoint_1 = os.path.join(main_dir,folder)
	images_names = [file for file in os.listdir(dir_timepoint_1) if any([file.endswith(".TIF"),file.endswith(".tif")])]
	images_data = []
	n_channels = 0
	for image_name_full in images_names:
		image_name = os.path.splitext(image_name_full)[0]
		image_data_as_list = image_name.split("_")
		image_data = {
			"full_name": image_name_full,
			"dir": dir_timepoint_1,
			"plate_name": image_data_as_list[0],
			"well_id": image_data_as_list[1].upper(),
			"site": int(image_data_as_list[2][1:]),
			"channel": int(image_data_as_list[3][1:]),
		}
		if image_data["channel"] > n_channels: n_channels = image_data["channel"]
		images_data.append(image_data)
	
	# TODO - merge the images of different channels
	# Select the images to open
	images_to_open = [image for image in images_data if image["well_id"] == well_id and image["site"] == site_no]
	
	# Open_images
	for i in range(len(images_to_open)):
		if i == 0:
			img = IJ.openImage(os.path.join(images_to_open[i]["dir"],images_to_open[i]["full_name"]))
			continue
		img_temp = IJ.openImage(os.path.join(images_to_open[i]["dir"],images_to_open[i]["full_name"]))
		
		# Merge images
		img = Concatenator.run(img, img_temp)
		
	new_title = images_to_open[i]["plate_name"] + "_" + well_id + "_" + str(site_no)
	img.setTitle(new_title)
	IJ.run(img, "Properties...", "channels=" + str(n_channels) + " slices=1 frames=1 pixel_width=1.0000 pixel_height=1.0000 voxel_depth=1.0000");
	img.show()

#	TODO - Add metadata
#   TODO - merge the images of different timepoints
#	print images_to_open

# --- Main ---
if __name__ == "__main__":
	create_gui()
