# -*- coding:UTF-8 -*-

from image_grab import grab_wnd
import PIL
import cv2
import numpy


if __name__ == "__main__":
	pil_image, rect = grab_wnd("魔兽世界")
	opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
	cv2.imshow('image', opencvImage)
	while True:
		k = cv2.waitKey(0)&0xFF
		if k == 27:
			print 'ESC'
			cv2.destroyAllWindows()
			break