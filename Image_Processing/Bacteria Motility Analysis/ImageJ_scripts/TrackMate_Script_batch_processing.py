import sys
import csv
import os
import glob

from ij import IJ, ImagePlus
from ij import WindowManager
from ij.io import FileSaver

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking import LAPUtils
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.providers import SpotAnalyzerProvider
from fiji.plugin.trackmate.providers import EdgeAnalyzerProvider
from fiji.plugin.trackmate.providers import TrackAnalyzerProvider
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter

from fiji.plugin.trackmate.action import CaptureOverlayAction

FOLDER_WITH_DATA = \
    '../Motility_27.10.2020/Data/'
#File_list = os.listdir(FOLDER_WITH_DATA)
FileList=glob.glob(FOLDER_WITH_DATA+'*_ORIG.tiff')
FOLDER_TO_SAVE = \
    '../Motility_27.10.2020/Track_Mate_results/'


def PrepareImg(imp,PREP_FILE_NAME):
	# Substruct Background
	IJ.run(imp, 'Subtract Background...', 'rolling=10 stack')
    # Denoise
	IJ.run(imp, 'Median...', 'radius=3 stack')
	# Save 
	fs = FileSaver(imp)
	fs.saveAsTiff(PREP_FILE_NAME)
	return imp


def WriteTracks(list_track_results,FileName):
	fieldnames = ['TRACK_ID','POINT_ID','POSITION_X','POSITION_Y','FRAME','RADIUS','QUALITY','SNR','MEAN',]
	with open(FileName, mode='w') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		for line in list_track_results:
			writer.writerow({'TRACK_ID': line[0],'POINT_ID': line[1],'POSITION_X': line[2],'POSITION_Y': line[3],'FRAME': line[4],'RADIUS': line[5],'QUALITY': line[6],'SNR': line[7],'MEAN': line[8],})


for FilePath in FileList:
	File=FilePath.split('/')[-1]
	#-----------------------------
	# open file
	#-----------------------------
	imp=IJ.openImage(FilePath)
	#-----------------------------
	# open file
	#-----------------------------
	# Prepare images
	PREP_FILE_NAME = FOLDER_TO_SAVE + File.split('_ORIG.tiff')[0] + '_PREP.tiff'
	print(PREP_FILE_NAME)
	imp=PrepareImg(imp,PREP_FILE_NAME)
	imp.show()

	#-----------------------------
	# Track Mate
	#-----------------------------
	print('Start TrackMate')
	model = Model()
	# Send all messages to ImageJ log window.
	model.setLogger(Logger.IJ_LOGGER)
	settings = Settings()
	settings.setFrom(imp)
	print ('dx=', settings.dx)
	print ('dy=', settings.dy)
	print ('time_interval=', settings.dt)
	# Spot Detector
	settings.detectorFactory = LogDetectorFactory()
	settings.detectorSettings = {
		'DO_SUBPIXEL_LOCALIZATION': True,
		'RADIUS': 3.0,
		'TARGET_CHANNEL': 1,
		'THRESHOLD': 1.0,
		'DO_MEDIAN_FILTERING': False,
	}
	# Configure tracker 
	settings.trackerFactory = SparseLAPTrackerFactory()
	settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()  # almost good enough
	settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
	settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
	settings.trackerSettings['LINKING_MAX_DISTANCE'] = 15.0
    
	# Add ALL the feature analyzers known to TrackMate, via
	# providers.
	spotAnalyzerProvider = SpotAnalyzerProvider()
	for key in spotAnalyzerProvider.getKeys():
		print( key )
		settings.addSpotAnalyzerFactory( spotAnalyzerProvider.getFactory( key ) )
	edgeAnalyzerProvider = EdgeAnalyzerProvider()
	for  key in edgeAnalyzerProvider.getKeys():
		print( key )
		settings.addEdgeAnalyzer( edgeAnalyzerProvider.getFactory( key ) )
    
	trackAnalyzerProvider = TrackAnalyzerProvider()
	for key in trackAnalyzerProvider.getKeys():
		print( key )
		settings.addTrackAnalyzer( trackAnalyzerProvider.getFactory( key ) )
    
	# Configure track filters - We want to get rid of the two immobile spots at
	# the bottom right of the image. Track displacement must be above 10 pixels.
	filter1 = FeatureFilter('TRACK_DURATION', 3, True)
	settings.addTrackFilter(filter1)
    
	# Iniate plugin
	trackmate = TrackMate(model, settings)
	ok = trackmate.checkInput()
	if not ok:
		sys.exit(str(trackmate.getErrorMessage()))
	ok = trackmate.process()
	if not ok:
		sys.exit(str(trackmate.getErrorMessage()))
	# ----------------
	# Display results
	# ----------------
	selectionModel = SelectionModel(model)
	displayer = HyperStackDisplayer(model, selectionModel, imp)
	displayer.render()
	displayer.refresh()
    
	# command CaptureOverlayAction.capture(trackmate, startframe, endframe)
	capture = CaptureOverlayAction.capture(trackmate, -1,imp.getNFrames())
	# save capture image with overlay as tiff
	saveName = FOLDER_TO_SAVE+File.split('_ORIG.tiff')[0] + '_TRACKS_OVERLAY.tiff'
	FileSaver(capture).saveAsTiff(saveName )
    
	# --------------------------
	# Write tracks to the file
	# --------------------------
	# Echo results with the logger we set at start:
	model.getLogger().log(str(model))
	# The feature model, that stores edge and track features.
	fm = model.getFeatureModel()
    
	list_track_results = []
	for id in model.getTrackModel().trackIDs(True):
		model.getLogger().log('')
		v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
		duration = fm.getTrackFeature(id, 'TRACK_DURATION')
		model.getLogger().log('Track ' + str(id)+ ': mean velocity = ' + str(v) + ' '+ model.getSpaceUnits() + '/'+ model.getTimeUnits()+ 'track_duration=' + str(duration)+ model.getTimeUnits())
		track = model.getTrackModel().trackSpots(id)
        
		# Fetch spot features directly from spot.
		for spot in track:
			sid = spot.ID()
			x = spot.getFeature('POSITION_X')
			y = spot.getFeature('POSITION_Y')
			t = spot.getFeature('FRAME')
			q = spot.getFeature('QUALITY')
			snr = spot.getFeature('SNR')
			mean = spot.getFeature('MEAN_INTENSITY')
			radius = spot.getFeature('RADIUS')
			model.getLogger().log('Track ID=' + str(id)+ 'spot ID = ' + str(sid) + ': x=' + str(x)+ ', y=' + str(y) + ', t=' + str(t) + 'radius='+ str(radius) + str(q) + 'snr=' + str(snr)+ 'mean = ' + str(mean))
			list_track_results.append([id,sid,x,y,t,radius,q,snr,mean,])
	# Write traking results
	FileNameTracks=FOLDER_TO_SAVE+File.split('_ORIG.tiff')[0] + '_TRACKS.csv'
	WriteTracks(list_track_results,FileNameTracks)
	#print 'Tacking Done'
	# Track Mate
	#TrackMate_running(imp)
	imp.close()
print('Done')    