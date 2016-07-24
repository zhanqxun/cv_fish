# -*- coding:UTF-8 -*-

from image_grab import grab_wnd, put_foreground
import PIL
import cv2
import numpy
import math
import time
from mouse_key_event import key_input
from mouse_key_event import mouse_click, mouse_move
from SimpleLogger import logger
import core

"""空闲状态"""
STATE_IDLE = 1
"""上鱼饵状态"""
STATE_BAIT = 2
"""甩杆状态"""
STATE_CAST = 3
"""截图状态"""
STATE_SNAP = 4
"""等待上钩状态"""
STATE_WAIT = 5
"""收杆状态"""
STATE_FINI = 6
"""上刺钩状态"""
STATE_CUT = 7
"""上特殊鱼饵状态"""
STATE_SPECIAL_BAIT = 8



def esc_exit():
	k = cv2.waitKey(0)&0xFF
	if k == 27:
		print 'ESC'
		cv2.destroyAllWindows()


def grab():
	while True:
		pil_image, rect = grab_wnd("魔兽世界")
		if not pil_image:
			print "Cannot find wow hwnd, esc exit, other continue"
			esc_exit()
		else:
			opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
			return opencvImage, rect
	return None, rect

def foreground():
	put_foreground("魔兽世界")
	


if __name__ == "__main__":
	state = STATE_IDLE
	last_cut_ts = 0
	last_bait_ts = 0
	last_special_bait_ts = 0
	last_cast_ts = 0
	while True:
		if state == STATE_IDLE:
			foreground()
			ori_image, rect = grab()
			# if time.time() - last_cut_ts > 60 * 60:
			# 	"""一个小时上一次刺钩"""
			# 	state = STATE_CUT
			# elif time.time() - last_bait_ts > 60 * 10:
			# 	"""十分钟上一次鱼饵"""
			# 	state = STATE_BAIT
			# elif time.time() - last_special_bait_ts > 60 * 10:
			# 	"""十分钟上一次特殊鱼饵"""
			# 	state = STATE_SPECIAL_BAIT
			# else:
			state = STATE_CAST
			time.sleep(1)
		elif state == STATE_CUT:
			logger.info("上刺钩")
			foreground()
			key_input("3")
			last_cut_ts = time.time()
			time.sleep(2.1)
			state = STATE_IDLE
		elif state == STATE_BAIT:
			logger.info("上鱼饵")
			foreground()
			key_input("2")
			last_bait_ts = time.time()
			time.sleep(2.1)
			state = STATE_IDLE
		elif state == STATE_SPECIAL_BAIT:
			logger.info("上特殊鱼饵")
			foreground()
			key_input("4")
			last_special_bait_ts = time.time()
			time.sleep(2.1)
			state = STATE_IDLE
		elif state == STATE_CAST:
			logger.info("甩杆")
			foreground()
			key_input("1")
			last_cast_ts = time.time()
			time.sleep(1)
			state = STATE_SNAP
		elif state == STATE_SNAP:
			logger.info("截图分析")
			foreground()
			snap_image, rect = grab()
			result_list, target_pos, total_grey_diff = core.find_hook(ori_image, snap_image, False)
			#result_list, target_pos, total_grey_diff = core.find_hook(ori_image, snap_image, True)
			logger.info("target_pos %s total_grey_diff %s", target_pos, total_grey_diff)
			if target_pos:
				state = STATE_WAIT
				time.sleep(0.05)
			else:
				state = STATE_IDLE
				#key_input(["esc"])
				time.sleep(3)
			#cv2.waitKey(0)
		elif state == STATE_WAIT:
			t1 = time.time()
			snap_image, rect = grab()
			t2 = time.time()
			#logger.info("grab cost %s", str(t2 - t1))
			diff_ratio = core.cal_diff_ratio(ori_image, snap_image, result_list, total_grey_diff)
			t3 = time.time()
			#logger.info("cal cost %s", str(t3 - t2))
			#logger.info("diff_ratio %s", str(diff_ratio))
			if diff_ratio > 0.30:
				state = STATE_FINI
				logger.info("diff_ratio %s", str(diff_ratio))
			# else:
			# 	time.sleep(0.001)
			if time.time() - last_cast_ts > 25:
				state = STATE_IDLE
				#key_input(["esc"])
				time.sleep(2)
		elif state == STATE_FINI:
			logger.info("收杆")
			foreground()
			mouse_move(target_pos[0] + rect.left, target_pos[1] + rect.top)
			mouse_click(target_pos[0] + rect.left, target_pos[1] + rect.top)
			state = STATE_IDLE
			time.sleep(2)




		