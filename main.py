import os
import vlc
from appJar import gui
import json
import ttkthemes
import tkinter
import time
import datetime
from PIL import Image

# thumbnail image functions

def makeThumbnail(imagepath):
	app.debug(f'making thumbnail for {imagepath}')
	try:
		IM=Image.open(imagepath)
		IM = IM.resize((150,150))
		thumbnailpath =f'{imagepath[:-4]}_thumbnail.gif'
		IM.save(thumbnailpath)
		del IM
		return thumbnailpath
	except Exception as e:
		app.error(f'error making thumbnail: {e}')
		return 'no_image.gif'

# misc functions

def reorderLibrary():
	global library
	library = dict(sorted(library.items()))


def setupTime():
	setupTime = round(time.time()-starttime,3)
	app.info(f'completed setup in {setupTime}s')
	if setupTime > 20:
		app.warn('setup took VERY long')
	elif setupTime > 10:
		app.warn('setup took longer than expected')

def cropText(text,cropnum=25):
	if len(text) > cropnum+1: 
		return f'{text[:cropnum]}...'
	else:
		return text

def stopFunction():
	try:
		stoppingtime = time.time()
		try:
			with open('theme.json','w') as f:
				f.write(app.getMenuRadioButton('Ttk theme','radio_theme'))
			app.info('saved theme.json')
		except BaseException as e:
			app.error(f'error saving theme.json: {e}')
		updateLeftoffTime()
		saveLibrary()
		app.info(f'finished up in {round(time.time()-stoppingtime,3)}s')
		app.info(f'total runtime was {round(time.time()-starttime,3)}s')
		return True
	except:
		return True

def milliFormat(milliseconds,subtractH=True):
	try:
		if subtractH:
			millisecondos = milliseconds-3600000
		return datetime.datetime.fromtimestamp(millisecondos / 1000).strftime('%H:%M:%S')
	except:
		return datetime.datetime.fromtimestamp(milliseconds / 1000).strftime('%H:%M:%S')
# player functions

def closePlayerWindow():
	try:
		state = str(vlcPlayer.get_state()).lower().replace('state.','')
		if state == 'playing' or state == 'paused':
			vlcPlayer.set_pause(1)
		updateLeftoffTime()
	except:
		pass
	return True

def updateLeftoffTime():
	global library
	library[currentlyPlaying]['leftoff']['time'] = vlcPlayer.get_position()


def saveTimeAndFile():
	global library
	while True:
		state = str(vlcPlayer.get_state()).lower().replace('state.','')
		if state == 'playing' or state == 'paused':
			library[currentlyPlaying]['leftoff']['file'] = "".join(app.getListBox("list_queue"))
			updateLeftoffTime()	
			app.debug(f'saved leftoff time & file ({library[currentlyPlaying]["leftoff"]["time"]}, {library[currentlyPlaying]["leftoff"]["file"]})')
			saveLibrary()
		time.sleep(5*60)

def timelineScrub(name):
	playerpos = app.getScale('scale_player_timeline')
	playerpos = float(playerpos)/10000
	vlcPlayer.set_position(playerpos)

def updatePlayerInfo():
	state = str(vlcPlayer.get_state()).lower().replace('state.','')
	if state == 'playing':
		app.hideButton('btn_player_play')
		app.showButton('btn_player_pause')
		app.setLabel('player_current_playing_title',cropText(' '.join(app.getListBox("list_queue")),cropnum=17))
		app.setLabel('player_author',cropText(library[currentlyPlaying]['author']))
		app.setLabel('player_name',cropText(library[currentlyPlaying]['name']))
		playerpos = vlcPlayer.get_position()
		playerpos = int(playerpos*10000)
		try:
			app.setScale('scale_player_timeline',playerpos,callFunction=False)
		except:
			pass
		# 00:00:00/00:00:00
		app.setLabel('lbl_player_timeline_timeframe',f'{milliFormat(vlcPlayer.get_time(),subtractH=True)}/{milliFormat(vlcPlayer.get_length(),subtractH=True)}')
	elif state == 'paused':
		app.showButton('btn_player_play')
		app.hideButton('btn_player_pause')
		app.setLabel('player_current_playing_title',cropText(' '.join(app.getListBox("list_queue")),cropnum=17))
		app.setLabel('player_author',cropText(library[currentlyPlaying]['author']))
		app.setLabel('player_name',cropText(library[currentlyPlaying]['name']))
	else:
		app.showButton('btn_player_play')
		app.hideButton('btn_player_pause')
		app.setLabel('player_current_playing_title','Nothing playing')
		app.setLabel('player_author','No author')
		app.setLabel('player_name','No name')

def nextFile():
	try:
		app.selectListItemAtPos('list_queue',audioFiles.index(''.join(app.getListBox('list_queue')))+1,callFunction=True)
	except:
		pass

def previousFile():
	try:
		app.selectListItemAtPos('list_queue',audioFiles.index(''.join(app.getListBox('list_queue')))-1,callFunction=True)
	except:
		pass

def playFile(filename):
	media = vlcInstance.media_new(filename)
	media.get_mrl()
	vlcPlayer.set_media(media)
	vlcPlayer.play()

def queueClick(name):
	global library
	listBox = app.getListBox('list_queue')
	if len(listBox) > 0:
		filename=app.getListBox("list_queue")[0]
	else:
		return
	directory=library[currentlyPlaying]["directory"]
	fullfilename = f'{directory}/{filename}'
	playFile(fullfilename)
	library[currentlyPlaying]['leftoff']['file'] = filename
	app.setLabel('player_current_playing_title',cropText(' '.join(app.getListBox("list_queue")),cropnum=17))
	app.setLabel('player_author',library[currentlyPlaying]['author'])
	app.setLabel('player_name',library[currentlyPlaying]['name'])



def preparePlayer(entry):
	global audioFiles
	audioFiles = getAudioFiles(entry['directory'])
	app.updateListBox('list_queue',audioFiles,callFunction=False)
	global currentlyPlaying
	app.setImage('player_image',entry['thumbnail'])
	currentlyPlaying = entry['name']
	leftoffFile = entry['leftoff']['file']
	leftoffTime = entry['leftoff']['time']
	if leftoffFile != None and leftoffFile in audioFiles:
		app.selectListItem('list_queue',leftoffFile)
	else:
		app.selectListItem('list_queue',audioFiles[0])
	if leftoffTime != 0:
		vlcPlayer.set_position(leftoffTime)
	app.showSubWindow('window_player')


def rateScaleHandler():
	settings = {1:0.3, 2:0.50, 3:0.8, 4:0.9, 5:1.0, 6:1.1, 7:1.20, 8:1.50, 9:1.80, 10:2.0}
	currate = app.getScale('scale_player_rate')
	setting = int(round(currate))
	newrate = settings[setting]
	app.setScale('scale_player_rate',setting,callFunction=False)
	try:
		vlcPlayer.set_rate(newrate)
	except BaseException as e:
		app.warn(f'cannot change playback rate: {e}')

def volumeScaleHandler():
	vlc.audio_set_volume(app.getScale('scale_player_volume'))


def playerButtons(name):
	state = str(vlcPlayer.get_state()).lower().replace('state.','')
	if name == 'btn_player_play':
		if state == 'paused':
			vlcPlayer.set_pause(0)
			app.hideButton('btn_player_play')
			app.showButton('btn_player_pause')
	elif name == 'btn_player_pause':
		if state == 'playing':
			updateLeftoffTime()
			vlcPlayer.set_pause(1)
			app.showButton('btn_player_play')
			app.hideButton('btn_player_pause')
	elif name == 'btn_player_fastforward':
		vlcPlayer.set_time(vlcPlayer.get_time()+30000)
	elif name == 'btn_player_fastbackbackward':
		vlcPlayer.set_time(vlcPlayer.get_time()-30000)
	elif name == 'btn_player_next':
		nextFile()
	elif name == 'btn_player_previous':
		previousFile()
	elif name == 'btn_player_resetvolume':
		app.setScale('scale_player_volume',100,callFunction=True)
	elif name == 'btn_player_resetrate':
		app.setScale('scale_player_rate',5,callFunction=True)

# external file loading stuff

def getAudioFiles(directory):
	audioFiles = []
	for item in os.listdir(directory):
		if os.path.isfile(f'{directory}/{item}'):
			if item.endswith('.mp3') or item.endswith('.m4a') or item.endswith('.wav'):
				audioFiles.append(item)
	audioFiles.sort()
	return audioFiles

def saveLibrary():
	app.debug(f'saving library.json')
	try:
		with open('library.json','w') as f:
			f.write(json.dumps(library))
			app.debug('library.json saved.')
	except BaseException as e:
		app.critical(f'error writing library.json: {e}')

def libraryInit():
	app.info('loading library')
	try:
		if os.path.isfile('library.json'):
			app.debug('library.json exists')
			with open('library.json','r') as f:
				library=json.loads(f.read())
				app.debug(f'library loaded: {", ".join(library)}')
		else:
			app.debug('library.json doesnt exist')
			with open('library.json','w') as f:
				library={}
				f.write(json.dumps(library))
				app.debug(f'library.json file written')
	except BaseException as e:
		app.critical(f'error reading/writing library.json: {e}')
		app.warningBox('Critical error',f'Could not read/write library file.\n{e}')
		library = {}
	app.info('done loading library')	
	return library

def loadTheme():
	app.info('loading default theme')
	try:
		if os.path.isfile('theme.json'):
			app.debug('theme.json exists')
			with open('theme.json','r') as f:
				defaultTheme = f.read()
				app.debug(f'theme.json read: {defaultTheme}')
		else:
			app.debug('theme.json doesnt exist')
			with open('theme.json','w') as f:
				defaultTheme = 'breeze'
				f.write(defaultTheme)
				app.debug(f'theme.json written, default theme set as {defaultTheme}')
	except BaseException as e:
		app.error(f'error reading/writing theme.json: {e}')
		app.warningBox('Error',f'Could not import default theme.\n{e}')
		defaultTheme = 'breeze'
	try:
		app.setTtkTheme(defaultTheme)
	except BaseException as e:
		app.error(f'could not set Ttk theme: {e}, falling back on breeze & attempting removal of theme.json')
		app.setTtkTheme('breeze')
		os.remove('theme.json')

	themes = app.getTtkThemes()
	try:
		themes.sort()
	except BaseException as e:
		app.error(f'error sorting themes ({e}), attempting fix')
		themes = list(themes)
		themes.sort()
	app.debug(f'availible themes: {", ".join(themes)}')
	for item in themes:
		if item == defaultTheme:
			app.addMenuRadioButton('Ttk theme','radio_theme',item,ttkThemeSwitcher,underline=0)
		else:
			app.addMenuRadioButton('Ttk theme','radio_theme',item,ttkThemeSwitcher)
	app.setMenuRadioButton('Ttk theme','radio_theme',defaultTheme)
	app.info('done loading default theme')



# button functions

def libraryButton(name):
	name = name.replace('libraryEntry_thumbnail_','')
	if vlcPlayer.is_playing() and currentlyPlaying == name:
		app.showSubWindow('window_player')
	else:
		app.debug(f'playing {name}')
		preparePlayer(library[name])

def ttkThemeSwitcher(name):
	theme =app.getMenuRadioButton('Ttk theme','radio_theme')
	app.info(f'switching to ttk theme {theme}')	
	try:
		app.setTtkTheme(theme)
	except BaseException as e:
		app.error(f'error switching Ttk theme: {e}')

def toolbarButtons(name):
	if name == 'Add new entry':
		app.clearAllEntries(callFunction=False)
		app.showSubWindow('window_newLib')
	elif name == 'Open player':
		app.showSubWindow('window_player')
	elif name == 'Sort library':
		sortLibraryEntries()
	elif name == 'radio_color':
		changeColorScheme(app.getMenuRadioButton('Color scheme','radio_color'))
	elif name == 'Clear library':
		if app.yesNoBox('Confirm library deletion','Are you sure you want to clear the library? This will remove all your entries & forget their timestamps.\nNote: this will NOT remove the files themselves, you can always re-add the entries.'):
			try:
				global library
				app.info('clearing library')
				os.remove('library.json')
				library = {}
				sortLibraryEntries()
				app.infoBox('Clear completed','Library has been cleared.')
			except Exception as e:
				app.error(f'error deleting library.json: {e}')
				app.warningBox(f'Error','Error clearing library: {e}')
	elif name == 'About':
		app.infoBox('About',f'Version {version} - build {buildDate}\n\nPyCasts is an podcast/audiobook player made by Anne mocha (@mocchapi) for Lilli snaog :>\n\nFollow development at https://github.com/mocchapi/PyCasts')

def newLibButtons(name):
	if name == 'btn_newLib_cancel':
		app.hideSubWindow('window_newLib')
		app.clearAllEntries(callFunction=False)
	if name == 'btn_newLib_save':
		entries=app.getAllEntries()
		for key in entries:
			if entries[key] == '' and key != 'entry_newLib_thumbnail' and key.startswith('entry_newLib'):
				app.warningBox('Missing info','Please fill in all fields')
				return
		tempdict = {}
		tempdict['name'] = entries['entry_newLib_name']
		tempdict['author'] = entries['entry_newLib_author']
		if os.path.isdir(entries['entry_newLib_directory']):
			tempdict['directory'] = entries['entry_newLib_directory']
		else:
			app.warningBox('Invalid directory','The entered directory is invalid')
		if entries['entry_newLib_thumbnail'] == '':
			thumbnail = 'no_image.gif'
		else:
			thumbnail = entries['entry_newLib_thumbnail']
		if os.path.isfile(thumbnail):
			generatedThumb = makeThumbnail(thumbnail)
			tempdict['thumbnail'] = generatedThumb
		else:
			app.warningBox('Invalid thumbnail file','The entered thumbnail file is invalid.\nThis entry can be left blank.')
			return
		tempdict['leftoff'] = {'file':None,'time':0}
		global library
		library[tempdict['name']] = tempdict
		app.info(f'Added library entry {tempdict}')
		app.hideSubWindow('window_newLib')
		app.clearAllEntries()
		saveLibrary()
		buildEntry(tempdict)


def editEntryButton(name):
	name = name.replace('Edit ','')
	global editedEntry
	editedEntry=name
	openEditWindow(name)

def editEntryOtherButton(name):
	if name == 'btn_editLib_save':
		editEntry(editedEntry)
		app.hideSubWindow('window_editLib')
	else:
		app.clearAllEntries()
		app.hideSubWindow('window_editLib')

def removeEntryButton(name):
	name = name.replace('Remove ','')
	if app.yesNoBox('Confirm',f'Are you sure you want to remove {name}?'):
		removeEntry(name)
		del library[name]
		saveLibrary()

# UI stuff
def sortLibraryEntries():
	app.debug('sorting library entries')
	global libraryY
	global libraryX
	libraryX = 0
	libraryY = 0
	for entry in library:
		removeEntry(library[entry]['name'])
	reorderLibrary()
	for entry in library:
		buildEntry(library[entry])

def openEditWindow(name):
	app.debug(f'editing {name}')
	app.setEntry('entry_editLib_thumbnail',library[name]['thumbnail'])
	app.setEntry('entry_editLib_directory',library[name]['directory'])
	app.setEntry('entry_editLib_name',library[name]['name'])
	app.setEntry('entry_editLib_author',library[name]['author'])
	app.showSubWindow('window_editLib')

def editEntry(entry):
	entries=app.getAllEntries()
	for key in entries:
		if entries[key] == '' and key != 'entry_editLib_thumbnail' and key.startswith('entry_editLib'):
			app.warningBox('Missing info','Please fill in all fields')
			return
	tempdict = {}
	tempdict['name'] = entries['entry_editLib_name']
	tempdict['author'] = entries['entry_editLib_author']
	if os.path.isdir(entries['entry_editLib_directory']):
		tempdict['directory'] = entries['entry_editLib_directory']
	else:
		app.warningBox('Invalid directory','The entered directory is invalid')
	if entries['entry_editLib_thumbnail'] == '':
		thumbnail = 'no_image.gif'
	else:
		thumbnail = entries['entry_editLib_thumbnail']
	if os.path.isfile(thumbnail):
		generatedThumb = makeThumbnail(thumbnail)
		tempdict['thumbnail'] = generatedThumb
	else:
		app.warningBox('Invalid thumbnail file','The entered thumbnail file is invalid.\nThis entry can be left blank.')
	tempdict['leftoff'] = {'file':None,'time':0}
	global library
	tempdict['leftoff'] = library[entry]['leftoff']
	del library[entry]
	library[tempdict['name']] = tempdict
	app.info(f'Added library entry {tempdict}')
	app.hideSubWindow('window_editLib')
	app.clearAllEntries()
	saveLibrary()
	sortLibraryEntries()

def removeEntry(name):
	try:
		app.info(f'removing {name}')
		app.emptyLabelFrame(f'libraryEntry_frame_{name}')
		app.removeLabelFrame(f'libraryEntry_frame_{name}')
	except BaseException as e:
		app.error(f'couldnt remove entry {name}: {e}')

def buildEntry(entrydict):
	try:
		app.debug(f'building entry {entrydict["name"]}')
		global libraryX
		global libraryY
		name = entrydict['name']
		author = entrydict['author']
		thumbnail = entrydict['thumbnail']
		directory = entrydict['directory']

		app.openScrollPane('frame_libraryView')
		app.startLabelFrame(f'libraryEntry_frame_{name}',libraryY,libraryX,label='')
		app.setSticky('n')
		app.setStretch('column')
		app.addImage(f'libraryEntry_thumbnail_{name}',thumbnail)
		try:
			app.setImageSize(f'libraryEntry_thumbnail_{name}',150,150)
		except:
			pass
		#app.setImageMouseOver(f'libraryEntry_thumbnail_{name}','play_button.gif')
		try:
			app.createRightClickMenu(f'libraryEntry_rClick_{name}')
			app.addMenuItem(f'libraryEntry_rClick_{name}',f'Edit {name}',editEntryButton)
			app.addMenuItem(f'libraryEntry_rClick_{name}',f'Remove {name}',removeEntryButton)
		except:
			pass
		app.setImageRightClick(f'libraryEntry_thumbnail_{name}',f'libraryEntry_rClick_{name}')
		app.setImageSubmitFunction(f'libraryEntry_thumbnail_{name}',libraryButton)
		app.setImagePadding(f'libraryEntry_thumbnail_{name}',[20,20])
		app.addLabel(f'libraryEntry_name_{name}',cropText(name,cropnum=30))
		app.addLabel(f'libraryEntry_author_{name}',cropText(author,cropnum=30))
		app.stopLabelFrame()
		app.stopScrollPane()
		if libraryX < 4:
			libraryX+=1
		else:
			libraryX=0
			libraryY+=1
	except Exception as e:
		app.error(f'could not build entry {entrydict["name"]}: {e}')
		app.warningBox('Library error',f'could not build entry {entrydict["name"]}: {e}')

def mainUI():
	app.setFont(size=15, family="Open Sans")
	app.setStretch('both')
	app.setSticky('nesw')
	app.startLabelFrame('frame_libraryLabel',label='Library')
	app.setSticky('nesw')
	app.startScrollPane('frame_libraryView')
	app.setSticky('new')
	app.setStretch('both')
	app.stopScrollPane()
	app.stopLabelFrame()

	app.addMenuList('Library',['Add new entry','Sort library','Clear library'],toolbarButtons)
	app.addMenuList('View',['About','Open player'],toolbarButtons)
	app.addSubMenu('View','Ttk theme')



def playerUI():
	app.startSubWindow('window_player','PyCasts Player',transient=False,modal=False)
	app.setStopFunction(closePlayerWindow)
	app.setFont(size=12, family="Open Sans")
	app.setSize(600, 400)


	app.setStretch('both')
	app.setSticky('nesw')
	app.startFrame('player_frame_top',0,0)
	app.setStretch('both')
	app.setSticky('nesw')
	app.startLabelFrame('player_frame_queue',0,1,label='Queue')
	app.setStretch('both')
	app.setSticky('nesw')
	app.addListBox('list_queue', [])
	app.setListBoxChangeFunction('list_queue',queueClick)
	app.stopLabelFrame()

	app.setStretch('row')
	app.setSticky('nsw')
	app.startFrame('player_frame_info',0,0)
	app.setSticky('new')
	app.setStretch('column')
	app.addLabel('player_janky_image_spacer','')
	app.addImage('player_image','no_image.gif')
	app.addLabel('player_current_playing_title','Nothing playing')
	app.addLabel('player_name','No name')
	app.addLabel('player_author','No author')
	app.getLabelWidget('player_current_playing_title').config(font='Arial 15')
	app.getLabelWidget('player_author').config(font='Arial 12')
	app.getLabelWidget('player_name').config(font='Arial 12')
	app.stopFrame()
	app.stopFrame()
	'''
	icons:
	~/.local/lib/python3.6/site-packages/appJar:

	md-play >
	md-pause II
	md-fast-forward >>
	md-fast-backward <<
	md-next >I
	md-previous I<
	'''
	app.setStretch('column')
	app.setSticky('esw')
	app.startFrame('player_frame_bottom',1,0)
	app.setStretch('none')
	app.setSticky('nes')
	app.addLabel('controls go here')
	app.addLabel('lbl_player_timeline_timeframe','00:00/00:00',0,1)

	app.setStretch('column')
	app.setSticky('nesw')
	app.addScale('scale_player_timeline',0,0)
	app.setScaleRange('scale_player_timeline',0,10000	)
	app.setScaleChangeFunction('scale_player_timeline',timelineScrub)
	app.setScaleIncrement('scale_player_timeline',0)
	app.startFrame('frame_player_buttons',1,0,2)
	app.setStretch('column')
	app.setSticky('nesw')
	app.addIconButton('btn_player_previous',playerButtons,'md-previous',1,0)
	app.addIconButton('btn_player_fastbackbackward',playerButtons,'md-fast-backward',1,1)
	app.addIconButton('btn_player_pause',playerButtons,'md-pause',1,2)
	app.addIconButton('btn_player_play',playerButtons,'md-play',1,2)
	app.hideButton('btn_player_pause')
	app.addIconButton('btn_player_fastforward',playerButtons,'md-fast-forward',1,3)
	app.addIconButton('btn_player_next',playerButtons,'md-next',1,4)

	app.startFrame('frame_player_buttons2',2,0,4)
	app.setStretch('column')
	app.setSticky('nsw')
	app.addIconButton('btn_player_resetvolume',playerButtons,'md-volume-3',0,0)
	app.addScale('scale_player_volume',0,1)
	app.setSticky('nse')
	app.addIconButton('btn_player_resetrate',playerButtons,'time',0,3)
	app.addScale('scale_player_rate',0,4)
	app.setScaleChangeFunction('scale_player_rate',rateScaleHandler)
	app.setScaleRange('scale_player_volume',1,200)
	app.setScaleRange('scale_player_rate',1,10)
	app.setScale('scale_player_volume',100,callFunction=False)
	app.setScale('scale_player_rate',5,callFunction=False)
	app.stopFrame()
	app.stopFrame()	
	app.stopFrame()
	app.stopSubWindow()

def newLibUI():
	app.startSubWindow('window_newLib','Add library entry',transient=True,modal=True)
	app.setSize('500x200')
	app.setResizable(False)
	app.setSticky('nesw')
	app.setStretch('both')
	app.startLabelFrame('frame_newLib',0,0,2,label='Configure library entry')
	app.setSticky('new')
	app.setStretch('column')
	app.addEntry('entry_newLib_name',3,3)
	app.addEntry('entry_newLib_author',6,3)
	app.addDirectoryEntry('entry_newLib_directory',9,3)
	app.addFileEntry('entry_newLib_thumbnail',12,3)
	app.setSticky('nw')
	app.setStretch('none')
	app.addLabel('lbl_newLib_name','Name',3,1)
	app.addLabel('lbl_newLib_author','Author(s)',6,1)
	app.addLabel('lbl_newLib_directory','Audio folder ',9,1)
	app.addLabel('lbl_newLib_thumbnail','Thumbnail (optional) ',12,1)
	app.stopLabelFrame()
	app.setSticky('esw')
	app.setStretch('column')
	app.addNamedButton('Cancel','btn_newLib_cancel',newLibButtons,3,0)
	app.addNamedButton('Save','btn_newLib_save',newLibButtons,3,1)
	app.stopSubWindow()

def editLibUI():
	app.startSubWindow('window_editLib','Edit library entry',transient=True,modal=True)
	app.setSize('500x200')
	app.setResizable(False)
	app.setSticky('nesw')
	app.setStretch('both')
	app.startLabelFrame('frame_editLib',0,0,2,label='Configure library entry')
	app.setSticky('new')
	app.setStretch('column')
	app.addEntry('entry_editLib_name',3,3)
	app.addEntry('entry_editLib_author',6,3)
	app.addDirectoryEntry('entry_editLib_directory',9,3)
	app.addFileEntry('entry_editLib_thumbnail',12,3)
	app.setSticky('nw')
	app.setStretch('none')
	app.addLabel('lbl_editLib_name','Name',3,1)
	app.addLabel('lbl_editLib_author','Author(s)',6,1)
	app.addLabel('lbl_editLib_directory','Audio folder ',9,1)
	app.addLabel('lbl_editLib_thumbnail','Thumbnail (optional) ',12,1)
	app.stopLabelFrame()
	app.setSticky('esw')
	app.setStretch('column')
	app.addNamedButton('Cancel','btn_editLib_cancel',editEntryOtherButton,3,0)
	app.addNamedButton('Save','btn_editLib_save',editEntryOtherButton,3,1)
	app.stopSubWindow()

def setup():
	app.setSize('835x500')
	app.setIcon('ico.gif')
	app.setLogLevel('debug')

	global libraryY
	global libraryX
	libraryY = 0 
	libraryX = 0
	app.setStartFunction(setupTime)
	app.setStopFunction(stopFunction)

if __name__ == '__main__':
	version = '1.1.0'
	buildDate = '15/6/2020'
	# very first things, init of appjar & basic global settings, stage 0
	starttime = time.time()
	app = gui('PyCasts library','10x10',useTtk=True,startWindow=None)
	app.debug('###stage 0###')
	app.debug(f'version {version} @ {buildDate}')
	setup()
	#window ui gets set up here, stage 1
	app.debug('###stage 1###')
	mainUI()
	playerUI()
	newLibUI()
	editLibUI()
	# external data (jsons) getloaded, stage 2
	app.debug('###stage 2###')
	loadTheme()
	library = libraryInit()
	# building library, stage 3
	app.debug('###stage 3###')
	reorderLibrary()
	for entry in library:
		buildEntry(library[entry])
	# vlc initialisation, stage 4
	app.debug('###stage 4###')
	try:
		vlcInstance = vlc.Instance()
		vlcPlayer = vlcInstance.media_player_new()
		app.info('Vlc instance created')
	except BaseException as e:
		app.critical(f'error creating vlc instance: {e}')
		app.critical(f'cannot continue')
		app.warningBox('critical error',f'error creating vlc instance: "{e}"\nIs VLC media player installed?')
		exit()
	app.thread(saveTimeAndFile)
	app.registerEvent(updatePlayerInfo)
	app.setPollTime(500)
	currentlyPlaying = None
	app.debug('###all stages complete###')
	app.go()