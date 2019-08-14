import sys
from PyQt4 import QtGui, QtCore


class Screenshot(QtGui.QWidget):  

	def __init__(self):
		super(Screenshot, self).__init__()     
		self.setWindowIcon(QtGui.QIcon('Icon/snip_tool.png'))
		self.setWindowTitle('SnipIt')
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

		self.clipboard = QtGui.QApplication.clipboard()
		self.screenshot_label = QtGui.QLabel(self)
		self.painter = QtGui.QPainter()
		self.pixmap = None
		self.in_snip = False
		self.clicked = False
		self.pos1 = (0, 0)
		self.pos2 = (0, 0)

		self.init_UI()

	# Select the screenshot area
	def paintEvent(self, event):
		width = self.pos2[0] - self.pos1[0]
		height = self.pos2[1] - self.pos1[1]     

		if self.in_snip:
			self.painter.begin(self) 
			self.painter.setPen(QtGui.QColor(255, 80, 80))   

			if self.pos1[0] != self.pos2[0] and self.pos1[1] != self.pos2[1]:   
				self.painter.fillRect(self.pos1[0], self.pos1[1], width, height, QtGui.QColor(53, 153, 255)) 
				self.painter.drawRect(self.pos1[0], self.pos1[1], width, height)

			self.painter.end()
			
	def mousePressEvent(self, event):
		self.clicked = True
		self.pos1 = [event.pos().x(), event.pos().y()]

		if event.button() == QtCore.Qt.RightButton:
			if self.pixmap is None and self.in_snip:
				self.options_menu(True)
			elif self.pixmap is not None:
				self.options_menu(False)

	def mouseMoveEvent(self, event):
		if self.clicked and self.pos1 != self.pos2:
			self.pos2 = [event.pos().x(), event.pos().y()]
			self.update()

	def mouseReleaseEvent(self, event):
		self.pos2 = [event.pos().x(), event.pos().y()]
		self.clicked = False

		if self.in_snip: 

			if self.pos1[0] != self.pos2[0] and self.pos1[1] != self.pos2[1]:
				self.in_snip = False

				self.showMinimized()
				self.select_window(self.pos1[0], self.pos1[1], self.pos2[0], self.pos2[1])

				try:
					if event.button() == QtCore.Qt.LeftButton:
						self.screenshot_label.setPixmap(self.pixmap)
						self.show_UI()
						self.scale_widget()

				except TypeError:
					pass
			
			else:
				self.pos2 = (0, 0)

	def init_UI(self):                           
		self.setGeometry(200, 200, 300, 80)
		self.in_snip = False
		self.screenshot_label.setText('Press <Select Screen> to select freely the screenshot area\n' +
									  'Press <Fullscreen> to take screenshot of the entire screen')

		self.init_buttons()

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.grab_btn)
		hbox.addWidget(self.whole_btn)
		hbox.addWidget(self.save_btn)
		hbox.addWidget(self.copy_btn)
		hbox.addWidget(self.quit_btn)

		grid = QtGui.QGridLayout()
		grid.setSpacing(15)
		grid.addItem(hbox, 1, 0)
		grid.addWidget(self.screenshot_label, 2, 0)

		self.setLayout(grid) 

	def init_buttons(self):
		self.grab_btn = QtGui.QPushButton('Select Screen', self)
		self.grab_btn.resize(self.grab_btn.sizeHint())  
		self.grab_btn.clicked.connect(self.in_snip_mode)

		self.whole_btn = QtGui.QPushButton('Fullscreen', self)
		self.whole_btn.resize(self.whole_btn.sizeHint())
		self.whole_btn.clicked.connect(self.shoot_fullscreen)

		self.save_btn = QtGui.QPushButton('Save', self)
		self.save_btn.resize(self.save_btn.sizeHint())
		self.save_btn.setEnabled(False)
		self.save_btn.clicked.connect(self.save_screenshot)

		self.copy_btn = QtGui.QPushButton('Copy', self)
		self.copy_btn.resize(self.copy_btn.sizeHint())
		self.copy_btn.setEnabled(False)
		self.copy_btn.clicked.connect(self.copy_pixmap)

		self.quit_btn = QtGui.QPushButton('Quit', self)
		self.quit_btn.resize(self.quit_btn.sizeHint())
		self.quit_btn.clicked.connect(self.close_application)

	def shoot_fullscreen(self):
		self.showFullScreen()
		self.setWindowOpacity(0)

		self.pixmap = None
		self.pixmap = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
		self.save_btn.setEnabled(True)
		self.copy_btn.setEnabled(True)

		self.screenshot_label.setPixmap(self.pixmap.scaled(
				self.screenshot_label.size() / 2, QtCore.Qt.KeepAspectRatio,
				QtCore.Qt.SmoothTransformation))

		self.showNormal()
		self.setWindowOpacity(1)
		self.scale_widget()

	def save_screenshot(self):
		initialPath = QtCore.QDir().currentPath() + "/.png"

		file = QtGui.QFileDialog().getSaveFileName(self, "Save as", initialPath,
				"%s Files (*.%s);;All Files (*)" % ('png'.upper(), 'png'))
		if file:
			self.pixmap.save(file, 'png')

	# Scaling the application window according to the screenshot size
	def scale_widget(self):
		screen = QtGui.QDesktopWidget().screenGeometry()

		if screen.width() // 2 > self.pixmap.width() and screen.height() // 2 > self.pixmap.height():
			self.setGeometry(200, 200, self.pixmap.width(), self.pixmap.height())
		else:
			self.setGeometry(0, 30, self.pixmap.width(), self.pixmap.height())

	def in_snip_mode(self):
		self.pixmap = None
		self.pos1 = (0, 0)
		self.pos2 = (0, 0)
		self.in_snip = True
		
		# Changing the cursor
		QtGui.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

		self.hide_UI()

	# Defining the screenshot area
	def select_window(self, x1, y1, x2, y2):
		if x1 < x2 and y1 < y2:
			self.pixmap = QtGui.QPixmap().grabWindow(0, x1, y1, abs(x2 - x1), abs(y2 - y1)) 
		elif x1 < x2 and y1 > y2:
			self.pixmap = QtGui.QPixmap().grabWindow(0, x1, y2, abs(x2 - x1), abs(y2 - y1))
		elif x1 > x2 and y1 < y2:
			self.pixmap = QtGui.QPixmap().grabWindow(0, x2, y1, abs(x2 - x1), abs(y2 - y1)) 
		elif x1 > x2 and y1 > y2:
			self.pixmap = QtGui.QPixmap().grabWindow(0, x2, y2, abs(x2 - x1), abs(y2 - y1))

	def copy_pixmap(self):
		self.clipboard.setPixmap(self.pixmap)

	# Erasing the rectangle which was used to determine the area of the screenshot
	def erase_rect(self):
		self.pos1, self.pos2 = (0, 0), (0, 0)
		self.painter.eraseRect(self.pos1[0], self.pos1[1], self.pos2[0], self.pos2[0])

	def hide_buttons(self):
		self.grab_btn.hide()
		self.whole_btn.hide()
		self.save_btn.hide()
		self.copy_btn.hide()
		self.quit_btn.hide()

	def show_buttons(self):
		self.grab_btn.show()
		self.whole_btn.show()
		self.save_btn.show()
		self.copy_btn.show()
		self.quit_btn.show()

	# Hiding the UI and commanding the application to expand
	def hide_UI(self):
		self.erase_rect()
		self.screenshot_label.clear()
		self.hide_buttons()
		self.showFullScreen()
		self.setWindowOpacity(0.3)

	def show_UI(self):
		self.show_buttons()

		if self.pixmap is not None:
			self.save_btn.setEnabled(True)
			self.copy_btn.setEnabled(True)
		else:
			self.save_btn.setEnabled(False)
			self.copy_btn.setEnabled(False)

		self.showNormal()
		self.setWindowOpacity(1)

		QtGui.QApplication.restoreOverrideCursor()

	# Menu that will popup after the screenshot is taken and when right mouse button is clicked
	def options_menu(self, in_snip_mode):
		menu = QtGui.QMenu(self)

		if in_snip_mode:
			cancel_action = QtGui.QAction('Cancel', self)
			cancel_action.triggered.connect(self.cancel )

			menu.addAction(cancel_action)
		else:
			copy_action = QtGui.QAction('Copy', self)
			copy_action.triggered.connect(self.copy_pixmap)
			save_action = QtGui.QAction('Save as', self)
			save_action.triggered.connect(self.save_screenshot)
			exit_action = QtGui.QAction('Exit', self)
			exit_action.triggered.connect(self.close_application)

			menu.addAction(copy_action)
			menu.addAction(save_action)
			menu.addAction(exit_action)

		menu.popup(QtGui.QCursor().pos())

	# Canceling the free screenshot area selection
	def cancel(self):
		self.in_snip = False
		self.setGeometry(200, 200, 300, 80)
		self.screenshot_label.setText('Press <Select Screen> to choose freely the screenshot area\n' +
							  'Press <Whole Screen> to take screenshot of the entire screen')
		self.show_UI()

	def close_application(self):
		choice = QtGui.QMessageBox().question(self, 'Closing the program...',
											  "Are you sure you want quit?",
											  QtGui.QMessageBox().Yes | QtGui.QMessageBox().No)

		if choice == QtGui.QMessageBox().Yes:
			sys.exit()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	screenshot = Screenshot()
	screenshot.show()

	sys.exit(app.exec_())
