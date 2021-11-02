from threading import Thread

from PySide6.QtCore import QTime, QTimer, Slot
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QWidget

import datetime
import logging
import rpyc
from rpyc.utils.server import ThreadedServer
import sqlite3
import sys
import unittest.mock as mock

DefaultLog = 'kill_server.log'
DefaultName = 'Kill Server'
DefaultHostname = 'localhost'
DefaultPort = 50555
DefaultDebugStart = 'kill_server Start'
		

class ClientsData:
	def __init__(self, name, connection, start_time, last_time):
		self.name=name
		self.connection = connection
		self.start_time = start_time
		self.last_time = last_time

						
class ServerControl:
	def __init__(self, app, my_map=None):
		self.my_app = app
		if my_map is None:
			my_map = {}
		self.my_map = my_map
		self.my_service = ServerService(self)
		self.my_model = ServerModel(self)
		self.my_view = ServerView(self)


class ServerView(QMainWindow):
	TimeFormat = 'h:mm:ss ap'
	DefaultSize = 1024
	NameLabel = 'Name'
	StartLabel = 'Start Time'
	LastLabel = 'Last Updated'
	StatusLabel = 'Status'

	def __init__(self, control):
		super().__init__()
		self.my_control = control
		self.my_model = control.my_model
		self.setFixedSize(self.DefaultSize, self.DefaultSize)
		self.layout = QVBoxLayout()
		self.my_widget = QWidget(self)
		self.my_programs = QTableWidget(self.my_widget)
		self.layout.addWidget(self.my_programs)		
		self.setWindowTitle(self.my_model.name)
		self.setCentralWidget(self.my_widget)
		self.my_widget.setLayout(self.layout)
		self.update_objects()
		self.create_time(self.my_control.my_app)
		
	def update_objects(self):
		self.update_programs_table()
		
	def update_programs_table(self):
		self.my_programs.clearContents()
		data = self.my_control
		self.my_programs.setRowCount(1 + len(data.my_map))
		self.my_programs.setColumnCount(4)
		self.my_programs.setHorizonalHeaderLabels(self.get_program_labels())
		self.my_programs.setItem(0, 0, QTableWidgetItem(data.my_model.name))
		self.my_programs.setItem(0, 1, QTableWidgetItem(self.get_start_label()))
		self.my_programs.setItem(0, 2, QTableWidgetItem(self.get_last_label()))
		print('rows: ' + str(self.my_programs.rowCount()))
		for r, data in self.my_control.my_map.items():
			item_name = QTableWidgetItem(data.name)
			self.my_programs.setItem( r+1, 0, item_name )
			item_start = QTableWidgetItem(self.get_d_start_label(data))
			self.my_programs.setItem( r+1, 1, item_start )
			item_last = QTableWidgetItem(self.get_d_last_label(data))
			self.my_programs.setItem( r+1, 2, item_last )	
			item_status = QTableWidgetItem(self.get_d_status_label(data))
			self.my_programs.setItem( r+1, 3, item_status )			
		self.my_programs.resizeColumnsToContent()
			
	def get_name_label(self):
		return 'Program: ' + DefaultName
		
	def get_start_label(self):
		return 'Time Started: ' + self.get_time_label(self.my_model.get_start_time())
		
	def get_last_label(self):
		return 'Last Updated: ' + self.get_time_label(self.my_model.get_time())
		
	def get_d_start_label(self, data):
		return 'Time Started: ' + self.get_time_label(data.start_time)
		
	def get_d_last_label(self, data):
		return 'Last Updated: ' + self.get_time_label(data.last_time)
		
	def get_d_status_label(self, data):
		result = 'Connection Status: '
		connection = data.connection
		if connection is None or connection.closed:
			result += 'Not Connected'
		else:
			result += 'Connected'
		return result
		
	def get_time_label(self, time):
		return time.toString(self.TimeFormat)
		
	def get_program_labels(self):
		return [ self.NameLabel, self.StartLabel, self.LastLabel, self.StatusLabel ]
		
	@Slot()
	def update_time(self):
		self.my_model.update_time()
		self.update_objects()

	def create_time(self, app):
		self.my_timer = QTimer(app)
		self.my_timer.start(1000)
		self.my_timer.timeout.connect(self.update_time)


class ServerModel:
	
	def __init__(self, control, name=None, start_time=None, last_time=None):
		self.my_control = control		
		if name is None: name=DefaultName
		if start_time is None: start_time=QTime.currentTime()
		if last_time is None: last_time=QTime.currentTime()
		self.name = name
		self.start_time = start_time
		self.last_time = last_time
		
	def update_service(self):
		pass
	
	def update_time(self):
		self.last_time = QTime.currentTime()
		self.update_service()

	def get_time(self):
		return self.last_time
		
	def get_start_time(self):
		return self.start_time
		
	def get_service_status(self):
		return not self.my_service.get_status()	
			

class ServerService(rpyc.Service):
	DebugInitStart = 'ServerService Start'
	DebugConnectError = 'ServerService Connection Error'
	DebugPingServerError = 'ServerService ping_server Error'
	
	NeverConnected = 'Never Connected'
	Connected = 'Connected'
	NotConnected = 'Not Connected'
		
	client_dict = {}
		
	def __init__(self, control, hostname=DefaultHostname, port=DefaultPort):
		self.my_control = control
		self.hostname=hostname
		self.port=port
		logging.debug(self.DebugInitStart)
		
	def check_status(self):
		return len(self.client_dict)
				
	def get_status(self):
		self._check_status()
		return self.status

	def on_connect(self, conn, name):
		self.conn = conn
		self.client_dict[name] = conn
		self.db.add_program(name)
		
	def on_disconnect(self, conn, name):
		del self.client_dict[name]
		self.db.remove_program(self.name)
		
	def exposed_ping(self, name):
		return name in self.client_dict
					

def main():
	logging.info(DefaultDebugStart)
	my_app = QApplication(sys.argv)
	my_control = ServerControl(my_app)
	my_model = my_control.my_model
	my_view = my_control.my_view
	my_service = my_control.my_service
	my_server = ThreadedServer(my_service, hostname=my_service.hostname, port=my_service.port)
	t = Thread(target=my_server.start)
	t.daemon = True
	t.start()
	my_view.show()
	sys.exit(my_app.exec())

if __name__ == '__main__':
	main()
