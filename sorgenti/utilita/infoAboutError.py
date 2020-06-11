import logging
import os
import sys


def getErrorInfo(exception: Exception):
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exception, exc_type, fname, exc_tb.tb_lineno)
	logging.error(exception)
