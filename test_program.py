from PySide6.QtCore import QTime, QTimer, Slot
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit
from PySide6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QWidget
import rpyc
import logging
import sys

DefaultLog = 'test_program.log'
DefaultName = 'Test Program'
DefaultHostname = 'localhost'
DefaultPort = 50555
DefaultDebugStart = 'test_program Start'

logging.basicConfig(filename=DefaultLog, level=logging.INFO)
	
	
class ClientService(rpyc.Service):
	DebugInitStart = 'ClientService Start'
	DebugConnectError = 'ClientService Connection Error'
	DebugPingServerError = 'ClientService ping_server Error'
	
	def __init__(self):
		self.connection = None
		self.connected = False
		self.name = DefaultName
		logging.debug(self.DebugInitStart)
		
	def my_connect():
		result = False
		try:
			self.connection = rpyc.connect(DefaultHostname, DefaultPort, service = self)
			result = True
		except Error as error:
			logging.error(self.DebugConnectError, error)
		return result
	
	def on_connect():
		self.connected = True
		
	def on_disconnect():
		self.connected = False
		
	def exposed_check(self, name):
		return name == Name
		
	def ping_server():
		result = (self.connected or self.connection is None)
		if not result:
			result = my_connect()
		if result:
			try:
				result = self.connection.root.ping()
			except Error as error:
				logging.error(self.DebugPingServerError, error)
		self.connected = result
		return result

class ClientControl:
	def __init__(self, model, view):
		self.my_model = model
		self.my_view = view


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
		
	def get_service_status():
		return self.service.connected:
	
					
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
		
	def get_name_label(self):
		return 'Program: ' + DefaultName
		
	def get_start_label(self):
		return 'Time Started: ' + self.get_time_label(self.my_model.get_start_time())
		
	def get_last_label(self):
		return 'Last Updated: ' + self.get_time_label(self.my_model.get_time())

	def get_status_label(self):
		result = 'Connection Status: '
		if my_model.is_service_connected:
			result += 'Connected'
		else:
			result += 'Not Connected'
		return result
		
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
	my_model = ClientModel()
	my_view = ClientView(my_model, my_app)
	my_control = ClientControl(my_model, my_view)
	my_view.show()
	my_service = ClientService()
	sys.exit(my_app.exec())

if __name__ == '__main__':
	main()
