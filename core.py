# -*- coding:UTF-8 -*-

import cv2
import numpy as np
import math
from SimpleLogger import logger
import time


def p_to_l(x0, y0, x1, y1, x2, y2):
	return math.fabs((y2-y1)*x0+(x1-x2)*y0+((x2*y1)-(x1*y2))) / (math.sqrt(math.pow(y2-y1, 2) + math.pow(x1-x2, 2)))


def pic_hough(edges, img):
	lines = cv2.HoughLines(edges, 1, np.pi/180, 40)
	if lines is not None and len(lines):
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
	m = s.shape[0]
	n = s.shape[1]
	#print m, n
	temp = s[int(m * top) : int(m * bottom), int(n * left) : int(n * right)]
	return temp


def pic_sub(dest, s1, s2):
	for x in range(dest.shape[0]):
		for y in range(dest.shape[1]):
			if s1[x, y] > s2[x, y]:
				dest[x, y] = s1[x, y] - s2[x, y]
			else:
				dest[x, y] = s2[x, y] - s1[x, y]

def pic_sub2(dest, s1, s2, lst):
	for p in lst:
		x = p[0]
		y = p[1]
		if s1[x, y] > s2[x, y]:
			dest[x, y] = s1[x, y] - s2[x, y]
		else:
			dest[x, y] = s2[x, y] - s1[x, y]



def pic_bin(dest, threshold):
	for x in range(dest.shape[0]):
		for y in range(dest.shape[1]):
			if dest[x, y] < threshold:
				dest[x, y] = 0
			else:
				dest[x, y] = 255

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
	if x >= 0 and y >= 0 and x < s.shape[0] and y < s.shape[1] and s[x, y] > 0 and e[x, y] == 0 and d < 15:
		h.append([x, y])
		e[x, y] = 1
		hook(s, e, x + 1, y, h, d + 1)
		hook(s, e, x - 1, y, h, d + 1)
		hook(s, e, x, y - 1, h, d + 1)
		hook(s, e, x, y + 1, h, d + 1)
		hook(s, e, x + 2, y, h, d + 1)
		hook(s, e, x - 2, y, h, d + 1)
		hook(s, e, x, y - 2, h, d + 1)
		hook(s, e, x, y + 2, h, d + 1)


def find_hook(s1, s2, waitKey=False):
	t_width = s1.shape[0]

	result_list = []
	target_pos = None
	total_grey_diff = 0
	
	scale = s1.shape[0] / t_width
	basex = 1 / 4.0 * s1.shape[1]
	ratio = s1.shape[1] / float(s1.shape[0])
	s1 = cv2.resize(s1, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	s1_back = s1.copy()
	s1 = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY)
	
	s1 = pic_cut(s1, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s1_back = pic_cut(s1_back, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	
	s = cv2.resize(s2, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	s2_back = s.copy()
	s2 = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
	s2 = pic_cut(s2, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s2_back = pic_cut(s2_back, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s = pic_cut(s, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)

	minus = np.zeros(s1.shape, np.uint8)

	#cv2.imwrite("grey.jpg", s2)

	#print s1.shape

	pic_sub(minus, s1, s2)

	minus_backup = minus.copy()

	if waitKey:
		cv2.imshow("original", resize(s1))
		cv2.imshow("target", resize(s2))
		cv2.imshow("minus", resize(minus))

	if waitKey:
		cv2.waitKey(0)

	canny = pic_canny(minus)
	#canny = minus.copy()
	
	if waitKey:
		cv2.imshow("canny", resize(canny))
		cv2.waitKey(0)

	s3 = s.copy()
	lines = pic_houghP(canny, s)
	#cv2.imshow("s3", canny)
	
	pic_bin(minus, 15)
	if waitKey:
		cv2.imshow("hough", resize(s))
		cv2.waitKey(0)
		cv2.imshow("binary", resize(minus))
		cv2.waitKey(0)
	

	if lines is not None and len(lines):
		d = []
		for x1, y1, x2, y2 in lines[0]:
			d.append(p_to_l(s1.shape[1] / 2, s1.shape[0], x1, y1, x2, y2))

		for idx, dis in enumerate(d):
			if dis == min(d):
				x1, y1, x2, y2 = lines[0][idx]
				cv2.line(s3,(x1,y1),(x2,y2),(0,0,255),1)
				if waitKey:
					cv2.imshow("choose_line", resize(s3))
				break
	else:
		logger.info("Cannot find lines")
		return result_list, target_pos, total_grey_diff

	if waitKey:
		cv2.waitKey(0)

	for x in range(s2.shape[0]):
		for y in range(s2.shape[1]):
			if s2[x, y] > 120:
				minus[x, y] = 0

	for x in range(minus.shape[0]):
		for y in range(minus.shape[1]):
			#print x, y, x1, y1, x2, y2, p_to_l(x, y, x1, y1, x2, y2)
			if minus[x, y] > 1 and p_to_l(y, x, x1, y1, x2, y2) < 10:
				pass
			else:
				minus[x, y] = 0

	if waitKey:
		cv2.imshow("filter_point", resize(minus))
		cv2.waitKey(0)

	hook_list = get_hook(minus)
	max_hook_len = 0
	max_hook = None
	for h in hook_list:
		if max_hook_len < len(h):
			max_hook_len = len(h)
			max_hook = h

	logger.info("max_hook %s", str(max_hook))
	if max_hook:
		for x in range(minus.shape[0]):
			for y in range(minus.shape[1]):
				for p in max_hook:
					if p[0] == x and p[1] == y:
						break
				else:
					minus[x, y] = 0


	target_num = 0
	total_x = 0
	total_y = 0
	
	for x in range(minus.shape[0]):
		for y in range(minus.shape[1]):
			if minus[x, y] > 0:
				target_num += 1
				result_list.append((x, y))
				total_x += y * scale + basex
				total_y += x * scale
				total_grey_diff += abs(float(s1_back[x, y, 1]) - float(s2_back[x, y, 1]))
	if target_num > 0:
		target_pos = (int(total_x / target_num), int(total_y / target_num))

	
	if waitKey:
		cv2.imshow("result", resize(minus))
		cv2.waitKey(0)

		logger.info("press key to close")
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	#cv2.destroyAllWindows()
	return result_list, target_pos, total_grey_diff


def cal_diff_ratio(s1, s2, result_list, total_grey_diff):
	t_width = s1.shape[0]
	#t1 = time.time()
	ratio = s1.shape[1] / float(s1.shape[0])
	s1 = cv2.resize(s1, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	#s1 = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY)
	s1 = pic_cut(s1, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	
	s = cv2.resize(s2, (int(ratio * t_width), int(t_width)), interpolation=cv2.INTER_CUBIC)
	#s2 = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
	s2 = pic_cut(s2, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	s = pic_cut(s, 1 / 4.0, 3 / 4.0, 0, 1 / 2.0)
	minus = np.zeros(s1.shape, np.uint8)
	#t2 = time.time()
	#logger.info("resize cost %s", str(t2 - t1))
	
	#pic_sub2(minus, s1, s2, result_list)
	t3 = time.time()
	#logger.info("sub cost %s", str(t3 - t2))
	#pic_bin(minus, 20)

	total = 0
	for p in result_list:
		total += abs(float(s1[p[0], p[1], 1]) - float(s2[p[0], p[1], 1]))
	diff_ratio = math.fabs(total_grey_diff - total) / float(total_grey_diff)
	t4 = time.time()
	#logger.info("total_grey_diff total ratio %s %s %s %s", total_grey_diff, total, diff_ratio, str(t4 - t3))
	return diff_ratio

if __name__ == "__main__":
	s1 = cv2.imread("3 (2).jpg")
	s2 = cv2.imread("3 (1).jpg")
	result_list, target_pos, total_grey_diff = find_hook(s1, s2, True)
	print "target_pos", target_pos
	if target_pos and total_grey_diff:
		diff_ratio = cal_diff_ratio(s1, s2, result_list, total_grey_diff)
		print "diff_ratio", diff_ratio

	cv2.waitKey(0)
	cv2.destroyAllWindows()