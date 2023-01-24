from ij import IJ
from ij.io import FileSaver


###############################################################
#  Track Mate script (based on the code from TrackMate
# https://github.com/fiji/TrackMate/scripts/ExampleScript_1.py )
###############################################################

import sys
import csv
 
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



##-----------------------------
### Open and Prepare Image for Tracking
##-----------------------------
# Get currently selected image
#imp = WindowManager.getCurrentImage()

FOLDER_TO_SAVE='../Motility_27.10.2020/'
ORIG_FILE_NAME='../Motility_27.10.2020/Data/Psa_KB_KB_1_cziPsa_KB_KB_1_czi_40003.ome.tiff_ORIG.tiff'
PREP_FILE_NAME=FOLDER_TO_SAVE+ORIG_FILE_NAME.split('/')[-1].split('ORIG.tiff')[0]+'3_PREP.tiff'

imp=ImagePlus(ORIG_FILE_NAME)

# Substruct Background
IJ.run(imp,"Subtract Background...", "rolling=10 stack");
# Denoise
IJ.run(imp, "Median...", "radius=3 stack")
fs=FileSaver(imp)
fs.saveAsTiff(PREP_FILE_NAME) 

#----------------------------
# Create the model object now
#----------------------------
    
# Some of the parameters we configure below need to have
# a reference to the model at creation. So we create an
# empty model now.
    
model = Model()   
# Send all messages to ImageJ log window.
model.setLogger(Logger.IJ_LOGGER)
    
    
       
#------------------------
# Prepare settings object
#------------------------
       
settings = Settings()
settings.setFrom(imp)

# Setting taking from the image dx,dy,dt
print("dx=",settings.dx)
print("dy=",settings.dy)
print("time_interval=",settings.dt)
print(settings.dt)
       
# Spot Detector
settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings = { 
    'DO_SUBPIXEL_LOCALIZATION' : True,
    'RADIUS' : 3.0,
    'TARGET_CHANNEL' : 1,
    'THRESHOLD' : 1.0,
    'DO_MEDIAN_FILTERING' : False,
}  
    
# Configure spot filters - Classical filter on quality
#filter1 = FeatureFilter('QUALITY', 30, True)
#settings.addSpotFilter(filter1)
     
# Configure tracker - We want to allow merges and fusions
settings.trackerFactory = SparseLAPTrackerFactory()
settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap() # almost good enough
settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
settings.trackerSettings['LINKING_MAX_DISTANCE'] = 15.0

 
# Add ALL the feature analyzers known to TrackMate, via
# providers. 
# They offer automatic analyzer detection, so all the 
# available feature analyzers will be added. 
 
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
    
    
#-------------------
# Instantiate plugin
#-------------------
trackmate = TrackMate(model, settings)
       
#--------
# Process
#--------
ok = trackmate.checkInput()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
    
ok = trackmate.process()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
    
       
#----------------
# Display results
#----------------
selectionModel = SelectionModel(model)
displayer =  HyperStackDisplayer(model, selectionModel, imp)
displayer.render()
displayer.refresh()

# command CaptureOverlayAction.capture(trackmate, startframe, endframe) 
capture = CaptureOverlayAction.capture(trackmate, -1, imp.getNFrames()) 

# save capture image with overlay as tiff 
savePath='../Motility_27.10.2020/'
saveName='Visual'
FileSaver(capture).saveAsTiff( savePath+saveName + ".tif")



#--------------------------
# Write tracks to the file
#--------------------------
    
# Echo results with the logger we set at start:
model.getLogger().log(str(model))
# The feature model, that stores edge and track features.
fm = model.getFeatureModel()

list_track_results=[]

for id in model.getTrackModel().trackIDs(True):
	model.getLogger().log('')
	v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
	duration = fm.getTrackFeature(id, 'TRACK_DURATION')
	model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits()+'track_duration='+str(duration)+model.getTimeUnits())
	track = model.getTrackModel().trackSpots(id)
	for spot in track:
		sid = spot.ID()
		# Fetch spot features directly from spot. 
		x=spot.getFeature('POSITION_X')
		y=spot.getFeature('POSITION_Y')
		t=spot.getFeature('FRAME')
		q=spot.getFeature('QUALITY')
		snr=spot.getFeature('SNR') 
		mean=spot.getFeature('MEAN_INTENSITY')
		radius=spot.getFeature('RADIUS')
		model.getLogger().log('Track ID='+str(id)+'spot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+'radius='+str(radius)+str(q) +'snr='+str(snr) + 'mean = ' + str(mean))
		list_track_results.append([id,sid,x,y,t,radius,q,snr,mean])


with open('../Motility_27.10.2020/results.csv', mode='w') as csv_file:
	fieldnames = ['TRACK_ID', 'POINT_ID', 'POSITION_X','POSITION_Y','FRAME','RADIUS','QUALITY','SNR','MEAN']
	writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
	writer.writeheader()
	
	for line in list_track_results:
		writer.writerow({'TRACK_ID':line[0],'POINT_ID':line[1],'POSITION_X':line[2],'POSITION_Y':line[3],'FRAME':line[4],'QUALITY':line[5],'SNR':line[6],'MEAN':line[7]})
print("Done")

    

   

