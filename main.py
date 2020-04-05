import os
#import vlc
from appJar import gui
import json

app = gui('PyCasts','800x500')
app.setBg('linen')
app.setFont(size=12, family="Open Sans")
app.setIcon('ico.gif')
app.setLogLevel('debug')
app.startSubWindow('secret_subwindow')
app.addLabel('var_posY',0)
app.addLabel('var_posX',0)
app.stopSubWindow()


#important functions

#json loading and saving
def save_json(data):
	with open('data.json','w') as f:
		print('@save_json, data: ',data)
		writeData = json.dumps(data)
		print('json data: ',writeData)
		f.write(writeData)

def get_json():
	app.debug('@get_json')
	with open('data.json','r') as f:
		library = json.loads(f.read())
		return library

def refresh_library():
	app.debug('refreshing library')
	app.emptyLabelFrame('frame_libraryView')
	app.setLabel('var_posX',0)
	app.setLabel('var_posY',0)
	load_library()
	update_remove_submenu()

def load_library():
	try:
		library = library_list('get')
		try:
			for item in library:
				new_library_icon(item)
		except BaseException as e:
			app.error(e)
			app.warningBox('item error',e)
	except BaseException as e:
		app.error(e)

def crop_text(text,limit):
	if len(text) > limit:
		if text[:limit-3].endswith(' '):
			return (f'{text[:limit-4]}...',True)
		else:
			return (f'{text[:limit-3]}...',True)
	else:
		return (text,False)

def get_names():
	names = []
	for item in library_list('get'):
		names.append(item['name'])
	return names

def new_library_icon(data):
#	app.debug(f'\n@new_library_icon, data:\n{data}\ntype:{type(data)}')
	posX = int(app.getLabel('var_posX'))
	posY = int(app.getLabel('var_posY'))
	if posX == 2:
		app.setLabel('var_posX',0)
		app.setLabel('var_posY',posY+1)
	else:
		app.setLabel('var_posX',posX+1)
	icon = f'{data["folder"]}/ico.gif'
	name = data['name']
	author = data['author']
	app.openLabelFrame('frame_libraryView')
	app.startFrame(f'library_frame_{name}',posY,posX)

	try:
		app.addImage(f'library_image_{name}',icon,0,0)
	except:
		app.addImage(f'library_image_{name}','no_image.gif',0,0)
	app.setImageSize(f'library_image_{name}',150,150)
	app.setImageSubmitFunction(f'library_image_{name}',app.debug)
	app.setImageMouseOver(f'library_image_{name}','play_button.gif')

	shortname = crop_text(name,12)
	print(shortname)
	app.addLabel(f'library_lbl_name_{name}',shortname[0],1,0)
	if shortname[1]:
		app.setLabelTooltip(f'library_lbl_name_{name}',name)

	shortauthor = crop_text(author,15)
	app.addLabel(f'library_lbl_author_{name}',shortauthor[0],2,0)
	if shortauthor[1]:
		app.setLabelTooltip(f'library_lbl_author_{name}',author)

	app.setLabelFg(f'library_lbl_author_{name}','honeydew4')
	app.getLabelWidget(f'library_lbl_author_{name}').config(font='Arial 10')
	app.stopFrame()
	app.stopLabelFrame()


def library_list(option,data=None):
	app.debug('@library_list')
	if option == 'append' and data !=None:
		try:
			current_lib = get_json()
		except:
			current_lib = []
		print('data: ',data)
		print('lib: ',current_lib)
		current_lib.append(data)
		print('current_lib:',current_lib)
		save_json(current_lib)
	elif option == 'get':
		return get_json()


def add_folder():
	app.debug('@add_folder')
	directory = app.directoryBox('select folder')
	print(directory)
	if directory == None:
		return
	name = app.textBox('Podcast name','Please enter the podcast name.')
	if name == None:
		return
	author = app.textBox('Author name','Please enter the podcast author(s).')
	if author == None:
		return
	else:
		newLibEntry = {'name':name,'author':author,'folder':directory,'leftoff_file':None,'leftoff_timestamp':None}
		library_list('append',newLibEntry)
		new_library_icon(newLibEntry)
		update_remove_submenu()

def update_remove_submenu():
	app.debug('@update_remove_submenu')
	names = get_names()
#	app.removeMenu'Remove')
	app.addSubMenu('Library','Remove')
	app.addMenuList('Remove',names,toolbar_remove_entry)



def select_podcast(name):
	pass


#toolbar
def toolbar_remove_entry(name):
	print(f'remove entry {name}')
	library = library_list('get')
	for indx,entry in enumerate(library):
		if entry['name'] == name:
			print(f'{entry["name"]} == {name}')
			del library[indx]
			save_json(library)
			refresh_library()

def toolbar_buttons(name):
	app.debug(f'@toolbar_buttons, data: {name}')
	if name == 'Add folder to library':
		add_folder()
	if name == 'Refresh library':
		refresh_library()

app.addMenuList('Library',['Add folder to library','Refresh library'],toolbar_buttons)
app.addSubMenu('Library','Remove')
try:
	update_remove_submenu()
except:
	pass
app.setStretch('both')
app.setSticky('nesw')
app.startLabelFrame('frame_libraryView',label='Library')
app.setSticky('n')
app.stopLabelFrame()

load_library()
app.go()