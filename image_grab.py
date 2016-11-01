# -*- coding:UTF-8 -*-

import ctypes
from PIL import ImageGrab
from SimpleLogger import logger
from SimpleLogger import to_gbk
from SimpleLogger import to_utf8

#构造RECT结构体  
class RECT(ctypes.Structure):  
	_fields_ = [('left', ctypes.c_long),  
				('top', ctypes.c_long),  
				('right', ctypes.c_long),  
				('bottom', ctypes.c_long)]  
	def __str__(self):  
		return str((self.left, self.top, self.right, self.bottom)) 

def grab_wnd(wnd_name):
	wnd_name = to_gbk(wnd_name)
	HWND = ctypes.windll.user32.FindWindowA(None, wnd_name)
	#logger.info("找到HWND %s", str(HWND))
	if HWND == 0:  
		logger.info("找不到窗口 %s", to_utf8(wnd_name))
		return None, None
	rect =RECT()  
	ctypes.windll.user32.GetWindowRect(HWND,ctypes.byref(rect))  
	#去掉状态栏
	print rect.left, rect.top, rect.right, rect.bottom
	rangle = (rect.left, rect.top, rect.right, rect.bottom)
	im = ImageGrab.grab(rangle)
	#im.show()
	return im, rect

def put_foreground(wnd_name):
	wnd_name = to_gbk(wnd_name)
	HWND = ctypes.windll.user32.FindWindowA(None, wnd_name)
	#logger.info("找到HWND %s", str(HWND))
	if HWND == 0:  
		logger.info("找不到窗口 %s", to_utf8(wnd_name))
		return None
	ctypes.windll.user32.SetForegroundWindow(HWND)  

if __name__ == "__main__":
	grab_wnd("计算器")

