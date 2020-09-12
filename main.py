import numpy as np
from PIL import Image
import cv2
import pytesseract
from datetime import datetime
from time import gmtime, strftime
import csv



class mainclass():

	def process(path):
		cap = cv2.VideoCapture(path)

		while(cap.isOpened()):
			ret, frame = cap.read()

			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			noiceRemoved = cv2.bilateralFilter(gray,11,17,17)
			canny=cv2.Canny(noiceRemoved,100,150)
			ret,thresh_image = cv2.threshold(canny,0,255,cv2.THRESH_OTSU)
			
			# cv2.imshow("test",thresh_image)

			(new, cnts, _) = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			cnts=sorted(cnts, key = cv2.contourArea, reverse = True)[:10] 
			NumberPlateCnt = None

			count=0
			for c in cnts:
				peri=cv2.arcLength(c,True)
				approx=cv2.approxPolyDP(c,0.06*peri,True)
				if len(approx)==4:
					NumberPlateCnt=approx
					break
				
			try:
				if not NumberPlateCnt.any()==False:

					x, y, width, height = cv2.boundingRect(NumberPlateCnt)
					roi = frame[y:y+height, x:x+width]

					#save region of interest into file
					cv2.imwrite("roi.png", roi)

					#draw contours
					cv2.drawContours(frame,[NumberPlateCnt],-1,[0,255,0],2)

					#pre-processing
					roiReadImage = cv2.imread("roi.png")
					resizedImage=cv2.resize(roiReadImage,(640,250))
					grayroiReadImage = cv2.cvtColor(resizedImage, cv2.COLOR_BGR2GRAY)
					blurroiReadImage = cv2.GaussianBlur(grayroiReadImage,(3,3),0)
					ret,thresholdroiReadImage = cv2.threshold(blurroiReadImage,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
					
					#tesseractOCR engine
					text=pytesseract.image_to_string(thresholdroiReadImage)
					nowDate=mainclass.get_ydm()
					nowTime=mainclass.get_time()
					if len(text)>0:
						mainclass.csv_write(text,nowDate,nowTime)
						print("CSV write as recognized")
					else:
						mainclass.csv_write("unrecognized",nowDate,nowTime)
						print("CSV write as un-recognized")
					#you can get the output above as "string" text
					#you can call it via external API

					cv2.imshow('numberPlate',thresholdroiReadImage)
					cv2.moveWindow("numberPlate", 10,20);
					cv2.imshow('livefeed',frame)
					cv2.moveWindow("livefeed", 600,250);


				if cv2.waitKey(1) & 0xFF == ord ('q'):
					print('Application is Closed')
					break

			except AttributeError:
				pass
			
			
		cap.release()
		cv2.destroyAllWindows()

	def get_ydm():
		x=datetime.now()
		return x.strftime("%x")

	def get_time():
		x=datetime.now()
		return x.strftime("%X")


	def csv_write(num,date,time):
		fieldnames=['Number', 'Date', 'Time']

		#change CSV file name here!
		with open(r'licences.csv', mode='a',newline='') as csv_file:
			writer=csv.DictWriter(csv_file, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerow({'Number':num,'Date':date, 'Time':time})


if __name__=='__main__':
	print("***********press 'q' to exit***************")

	#change below code line as your desire

	# 1) for inbuitcamrera = cv2.VideoCapture(0)
	# 2) for externalcamera = cv2.VideoCapture(1)
	# 3) for videofootage = don't change
	
	mainclass.process('intro2.mp4')
