# -*- coding:UTF-8 -*-

import cv2
import numpy as np
import math
from SimpleLogger import logger
import time
import os


bin_threshold = 35


def p_to_l(x0, y0, x1, y1, x2, y2):
	return math.fabs((y2-y1)*x0+(x1-x2)*y0+((x2*y1)-(x1*y2))) / (math.sqrt(math.pow(y2-y1, 2) + math.pow(x1-x2, 2)))


def pic_hough(edges, img):
	lines = cv2.HoughLines(edges, 1, np.pi/180, 50)
	tmp_lines = []
	if lines is not None and len(lines):
		tmp_lines.append([])
		for rho, theta in lines[0]:
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))
			#print x1, y1, x2, y2
			cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)
			tmp_lines[0].append((x1, y1, x2, y2))
	return tmp_lines


def pic_houghP(edges, img):
	param = 20
	while True:
		logger.info("param %s", param)
		lines = cv2.HoughLinesP(edges, 1, np.pi/180, param, param, 10)
		if lines is not None and len(lines):
			for x1, y1, x2, y2 in lines[0]:
				#print x1, y1, x2, y2
				cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)
			return lines
		else:
			param -= 1
		if param < 3:
			break
	return None
		

def pic_canny(img):
	edges = cv2.Canny(img, 20, 60)
	return edges

def pic_cut(s, left, right, top, bottom):
	# shape[0] height
	# shape[1] width
	m = s.shape[0]
	n = s.shape[1]
	#print m, n
	temp = s[int(m * top) : int(m * bottom), int(n * left) : int(n * right)]
	return temp


def pic_sub(dest, s1, s2):
	# for x in range(dest.shape[0]):
	# 	for y in range(dest.shape[1]):
	# 		if s1[x, y] > s2[x, y]:
	# 			dest[x, y] = s1[x, y] - s2[x, y]
	# 		else:
	# 			dest[x, y] = s2[x, y] - s1[x, y]
	return cv2.absdiff(s2, s1, dest)

# def pic_sub2(dest, s1, s2, lst):
# 	for p in lst:
# 		x = p[0]
# 		y = p[1]
# 		if s1[x, y] > s2[x, y]:
# 			dest[x, y] = s1[x, y] - s2[x, y]
# 		else:
# 			dest[x, y] = s2[x, y] - s1[x, y]



def pic_bin(dest, t):
	return cv2.threshold(dest, t, 255, cv2.THRESH_BINARY)[1]

def resize(s1):
	ratio = s1.shape[1] / float(s1.shape[0])
	w = 250
	return cv2.resize(s1, (int(ratio * w), int(w)), interpolation=cv2.INTER_CUBIC)


def get_hook(s):
	hook_list = []
	e = np.zeros(s.shape, np.uint8)
	for x in range(s.shape[0]):
		for y in range(s.shape[1]):
			if s[x, y] > 0 and e[x, y] == 0:
				h = []
				hook(s, e, x, y, h, 1)
				hook_list.append(h)
	return hook_list


def hook(s, e, x, y, h, d):
	if x >= 0 and y >= 0 and x < s.shape[0] and y < s.shape[1] and s[x, y] > 0 and e[x, y] == 0 and d < 200:
		h.append([x, y])
		e[x, y] = 1
		hook(s, e, x + 1, y, h, d + 1)
		hook(s, e, x - 1, y, h, d + 1)
		hook(s, e, x, y - 1, h, d + 1)
		hook(s, e, x, y + 1, h, d + 1)
		hook(s, e, x + 1, y + 1, h, d + 1)
		hook(s, e, x - 1, y + 1, h, d + 1)
		hook(s, e, x + 1, y - 1, h, d + 1)
		hook(s, e, x - 1, y - 1, h, d + 1)

x = 0
y = 0
max_x = 1440
max_y = 900
def show_win(name, img):
	global x, y, max_x, max_y
	t_img = resize(img)
	cv2.imshow(name, t_img)
	w = t_img.shape[1]
	h = t_img.shape[0]
	
	cv2.moveWindow(name, x, y)

	if x + w > max_x:
		x = 0
		y = y + h + 40
	else:
		x = x + w + 15


def print_result(result_list, s2, s1):
	min_x = 99999
	max_x = 0
	min_y = 99999
	max_y = 0
	map_dict = {}
	for p in result_list:
		if min_x > p[0]:
			min_x = p[0]
		if max_x < p[0]:
			max_x = p[0]
		if min_y > p[1]:
			min_y = p[1]
		if max_y < p[1]:
			max_y = p[1]
		map_dict[(p[0], p[1])] = True

	logger.log_file("s2: %s %s %s %s\n" % (min_x, max_x, min_y, max_y))
	for x in range(min_x, max_x + 1):
		for y in range(min_y, max_y + 1):
			if map_dict.get((x, y), None) is not None:
				logger.log_file(str(s2[x, y]) + "\t")
			else:
				logger.log_file("0" + "\t")
		logger.log_file("\n")
	logger.log_file("\n")

	logger.log_file("s1: \n")
	for x in range(min_x, max_x + 1):
		for y in range(min_y, max_y + 1):
			if map_dict.get((x, y), None) is not None:
				logger.log_file(str(s1[x, y]) + "\t")
			else:
				logger.log_file("0" + "\t")
		logger.log_file("\n")
	logger.log_file("\n")

def find_hook(s1, s2, waitKey=False):
	t_width = s1.shape[0]

	result_list = []
	target_pos = None
	total_grey_diff = 0
	
	scale = s1.shape[0] / t_width
	basex = 1 / 4.0 * s1.shape[1]
	ratio = s1.shape[1] / float(s1.shape[0])
	s1 = cv2.resize(s1, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	s1 = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY)
	s1_back = s1.copy()
	
	s1 = pic_cut(s1, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s1_back = pic_cut(s1_back, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	
	s = cv2.resize(s2, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	s2_back = s.copy()
	s2 = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
	s2 = pic_cut(s2, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	#s2_back = pic_cut(s2_back, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s2_back = s2.copy()
	s = pic_cut(s, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)

	minus = np.zeros(s1.shape, np.uint8)

	pic_sub(minus, s1, s2)

	minus_backup = minus.copy()

	if waitKey:
		#show_win("original", resize(s1))
		#show_win("target", resize(s2))
		show_win("minus", resize(minus))

	if waitKey:
		cv2.waitKey(10)

	# 对灰度图做边缘检测
	canny = pic_canny(minus)
	#canny = minus.copy()
	
	if waitKey:
		show_win("canny", resize(canny))
		cv2.waitKey(10)

	s3 = s.copy()
	# 直线检测
	lines = pic_hough(canny, s)
	#show_win("s3", canny)
	
	minus = pic_bin(minus, bin_threshold)
	bin_back = minus.copy()
	
	if waitKey:
		show_win("hough", resize(s))
		cv2.waitKey(10)
		show_win("binary", resize(minus))
		cv2.waitKey(10)

	if lines is not None and len(lines):
		d = []
		for x1, y1, x2, y2 in lines[0]:
			d.append(p_to_l(s1.shape[1] / 2, s1.shape[0], x1, y1, x2, y2))

		for idx, dis in enumerate(d):
			if dis == min(d):
				x1, y1, x2, y2 = lines[0][idx]
				cv2.line(s3,(x1,y1),(x2,y2),(0,0,255),1)
				if waitKey:
					show_win("choose_line", resize(s3))
				break
	else:
		logger.info("Cannot find lines")
		return result_list, target_pos, total_grey_diff

	if waitKey:
		cv2.waitKey(10)

	for x in range(s2.shape[0]):
		for y in range(s2.shape[1]):
			if s2[x, y] > 150:
				minus[x, y] = 0
			if x > s2.shape[0] / 10.0 * 9.0 or x < s2.shape[0] / 5.0:
				minus[x, y] = 0

	for x in range(minus.shape[0]):
		for y in range(minus.shape[1]):
			#print x, y, x1, y1, x2, y2, p_to_l(x, y, x1, y1, x2, y2)
			if minus[x, y] > 1 and p_to_l(y, x, x1, y1, x2, y2) < 10:
				pass
			else:
				minus[x, y] = 0
	t1 = time.time()
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))
	# 做一次开运算，消除噪音点
	opened = cv2.morphologyEx(minus, cv2.MORPH_OPEN, kernel)
	# 在做一次闭运算，连接误分的对象
	#kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7, 7))
	diamond = cv2.getStructuringElement(cv2.MORPH_RECT,(9, 9))  

	closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, diamond)

	closed = cv2.dilate(closed, diamond)  
	t2 = time.time()
	logger.info("morphologyEx cost %ss", str(t2 - t1))

	if waitKey:
		show_win("opened", resize(opened))
		cv2.waitKey(10)
		show_win("closed", resize(closed))
		cv2.waitKey(10)

	minus = closed

	if waitKey:
		show_win("filter_point", resize(minus))
		cv2.waitKey(10)
	t3 = time.time()
	hook_list = get_hook(minus)
	t4 = time.time()
	logger.info("get_hook cost %ss", str(t4 - t3))
	max_hook_len = 0
	max_hook = None
	for h in hook_list:
		if max_hook_len < len(h):
			max_hook_len = len(h)
			max_hook = h

	#logger.info("max_hook %s", len(max_hook))
	target_num = 0
	total_x = 0
	total_y = 0
	if max_hook:
		t5 = time.time()
		hook_map = {}
		for p in max_hook:
			hook_map[(p[0], p[1])] = True
		for x in range(minus.shape[0]):
			for y in range(minus.shape[1]):
				if hook_map.get((x, y), None) is not None:
					if minus[x, y] > 0 and bin_back[x, y] > 10:
						target_num += 1
						result_list.append((x, y))
						total_x += y * scale + basex
						total_y += x * scale
						#total_grey_diff += abs(abs(float(s2_back[x, y])) - abs(float(s1_back[x, y])))
					else:
						minus[x, y] = 0
				else:
					minus[x, y] = 0
		logger.info("len result_list %s", len(result_list))
		if len(result_list) > 100:
			min_x = 99999
			max_x = 0
			min_y = 99999
			max_y = 0
			map_dict = {}
			for p in result_list:
				if min_x > p[0]:
					min_x = p[0]
				if max_x < p[0]:
					max_x = p[0]
				if min_y > p[1]:
					min_y = p[1]
				if max_y < p[1]:
					max_y = p[1]
				map_dict[(p[0], p[1])] = True
			new_result_list = []
			for p in result_list:
				if p[1] < (min_y + max_y) / 2.0:
					new_result_list.append(p)
				else:
					minus[p[0], p[1]] = 0
			result_list = new_result_list


		#print_result(result_list, s2_back, s1_back)

		t6 = time.time()
		logger.info("filter hook cost %ss", str(t6 - t5))
	if target_num > 0:
		target_pos = (int(total_x / target_num), int(total_y / target_num))

	
	if waitKey:
		show_win("result", resize(minus))
		cv2.waitKey(10)

		# logger.info("press key to continue")
		# cv2.waitKey(0)
	total_grey_diff = len(result_list)
	return result_list, target_pos, total_grey_diff


def cal_diff_ratio(s1, s2, result_list, total_grey_diff):
	t_width = s1.shape[0]
	ratio = s1.shape[1] / float(s1.shape[0])
	s1 = cv2.resize(s1, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	s1 = pic_cut(s1, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s1 = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY)
	s = cv2.resize(s2, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	s2 = pic_cut(s2, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s2 = cv2.cvtColor(s2, cv2.COLOR_BGR2GRAY)

	minus = np.zeros(s1.shape, np.uint8)
	t1 = time.time()
	pic_sub(minus, s1, s2)
	t2 = time.time()
	minus = pic_bin(minus, bin_threshold)
	t3 = time.time()
	#logger.info("sub cost %ss", t2 - t1)
	#logger.info("bin cost %ss", t3 - t2)
	total = 0
	for p in result_list:
		if minus[p[0], p[1]] > 10:
			total += 1
		#total += abs(abs(float(s2[p[0], p[1]])) - abs(float(s1[p[0], p[1]])))
	#logger.info("len(result_list) %s total %s total_grey_diff %s", len(result_list), total, total_grey_diff)
	diff_ratio = math.fabs(total_grey_diff - total) / float(total_grey_diff)

	#print_result(result_list, s2, s1)
	#logger.log_file("ratio: %s%%" % str(math.floor(diff_ratio * 100)))

	return diff_ratio


if __name__ == "__main__":
	is_quit = False
	dir_list = []
	for f in os.listdir("."):
		if os.path.isdir(f) and f.isdigit():
			dir_list.append(f)
	dir_list = sorted(dir_list, reverse=True)
	for f in dir_list:
		original_file = None
		for p_file in os.listdir(f):
			if p_file.find("(1)") != -1:
				original_file = p_file
		if original_file:
			for p_file in os.listdir(f):
				if p_file == original_file:
					continue
				
				s1 = cv2.imread(os.path.join(f, original_file))
				s2 = cv2.imread(os.path.join(f, p_file))
				result_list, target_pos, total_grey_diff = find_hook(s1, s2, True)
				logger.info("target_pos %s", target_pos)
				if target_pos and total_grey_diff:
					diff_ratio = cal_diff_ratio(s1, s2, result_list, total_grey_diff)
					logger.info("diff_ratio %s", diff_ratio)
				logger.info("original_file %s p_file %s", os.path.join(f, original_file), os.path.join(f, p_file))
				x = 0
				y = 0
				logger.info("press esc to break, other key to continue")
				k = cv2.waitKey(0)&0xFF
				if k == 27:
					is_quit = True
					break
				else:
					cv2.destroyAllWindows()
			if is_quit:
				break
		if is_quit:
			break

	logger.info("press key to exit")
	cv2.waitKey(0)
	cv2.destroyAllWindows()