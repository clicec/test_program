from PySide6.QtCore import QTime, QTimer, Slot
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit
from PySide6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QWidget

import rpyc
from rpyc.core.protocol import Connection

import logging
import sys

DefaultLog = 'kill_base.log'
DefaultName = 'Kill Base'
DefaultHostname = 'localhost'
DefaultPort = 50555
DefaultDebugStart = 'kill_base Start'

logging.basicConfig(filename=DefaultLog, level=logging.INFO)
	
class KillException(Exception):
	pass
	
class KillClientNotConnected(KillException):
	pass
	
	
class ClientService(rpyc.Service):
	DebugInitStart = 'ClientService Start'
	DebugConnectError = 'ClientService Connection Error'
	DebugPingServerError = 'ClientService ping_server Error'
	
	NeverConnected = 'Never Connected'
	Connected = 'Connected'
	NotConnected = 'Not Connected'
	
	def __init__(self, name=DefaultName):
		self.connection = None
		self.status = self.NeverConnected
		self.name = name
		logging.debug(self.DebugInitStart)
		
	def my_connect(self):
		try:
			self.connection = rpyc.connect(DefaultHostname, DefaultPort, service = self)
			self._check_status()
		except Exception as error:
			logging.error(self.DebugConnectError, error)
		
	def is_closed(self):
		return self.connection is not Connection or self.connection.closed
	
	def _check_status(self):
		if self.is_closed():
			if self.status==self.Connected:
				self.status = self.NotConnected
		else:
			if self.status != self.Connected:
				self.status = self.Connected
				
	def get_status(self):
		self._check_status()
		return self.status
			
	def on_connect(self):
		pass
		
	def on_disconnect(self):
		pass
		
	def exposed_check(self, name):
		return name == self.name
		
	def ping_server(self):
		result = not self.is_closed()
		if result:
			try:
				self.connection.root.ping()
			except Exception as error:
				result = False
				logging.error(self.DebugPingServerError, error)
		return result


class ClientControl:
	def __init__(self, app):
		self.my_app = app
		self.my_service = ClientService()
		self.my_model = ClientModel(self.my_service)
		self.my_view = ClientView(self.my_model, self.my_app)


class ClientModel:
	def __init__(self, service):
		self.my_service = service
		self.start_time = QTime.currentTime()
		self.current_time = self.start_time

	def update_service(self):
		self.my_service.ping_server()
	
	def update_time(self):
		self.current_time = QTime.currentTime()
		self.update_service()

	def get_time(self):
		return self.current_time
		
	def get_start_time(self):
		return self.start_time
		
	def get_service_status(self):
		return self.my_service.get_status()
	
					
class ClientView(QMainWindow):
	TimeFormat = 'h:mm:ss ap'
	DefaultSize = 256

	def __init__(self, model, app):
		super().__init__()
		self.my_model = model
		self.my_app = app
		self.create_objects()
		
		self.setWindowTitle(DefaultName)
		self.setFixedSize(self.DefaultSize, self.DefaultSize)
		self.setCentralWidget(self.my_widget)
		self.my_widget.setLayout(self.layout)

		self.layout.addWidget(self.name_label)
		self.layout.addWidget(self.start_label)
		self.layout.addWidget(self.last_label)
		self.update_objects()
		self.create_time(app)
		
	def create_objects(self):
		self.layout = QVBoxLayout()
		self.my_widget = QWidget(self)
		self.name_label = QLabel(self.my_widget)
		self.start_label = QLabel(self.my_widget)
		self.last_label = QLabel(self.my_widget)
		self.status_label = QLabel(self.my_widget)
		
	def update_objects(self):
		self.name_label.setText(self.get_name_label())
		self.start_label.setText(self.get_start_label())
		self.last_label.setText(self.get_last_label())
		self.status_label.setText(self.get_status_label())
		self.status_label.adjustSize()

		
	def get_name_label(self):
		return 'Program: ' + DefaultName
		
	def get_start_label(self):
		return 'Time Started: ' + self.get_time_label(self.my_model.get_start_time())
		
	def get_last_label(self):
		return 'Last Updated: ' + self.get_time_label(self.my_model.get_time())

	def get_status_label(self):
		return 'Connection Status: ' + self.my_model.get_service_status()
		
	def get_time_label(self, time):
		return time.toString(self.TimeFormat)
		
	@Slot()
	def update_time(self):
		self.my_model.update_time()
		self.update_objects()

	def create_time(self, app):
		self.my_timer = QTimer(app)
		self.my_timer.start(1000)
		self.my_timer.timeout.connect(self.update_time)


def main():
	logging.info(DefaultDebugStart)
	my_app = QApplication(sys.argv)
	my_control = ClientControl(my_app)
	my_service = my_control.my_service
	my_model = my_control.my_model
	my_view = my_control.my_view
	my_view.show()
	sys.exit(my_app.exec())

if __name__ == '__main__':
	main()
