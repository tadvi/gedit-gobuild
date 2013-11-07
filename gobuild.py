# Copyright (c) 2013 Tad Vizbaras All rights reserved.
# Contact author by email: tad at etasoft com
# This is released with MIT license. Free to distribute but must include copyright notice
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# GoBuild plugin version 1.0 for GEdit. 
# Runs "go build" but if current filename has _test.go in the name then runs "go test".
# Waits for few seconds and then timeouts if process takes too long, so GEdit would 
# no freeze.
# Current directory is determined based on current open file directory.

from gi.repository import GObject, Gtk, Gedit
import re
import subprocess,datetime, os, time
import locale

encoding = locale.getdefaultlocale()[1]

class GoBuildGlobal:
	windowClass = 0


class GoBuildAfterSavePlugin(GObject.Object, Gedit.ViewActivatable):
	"""Run GoBuild after save document"""

	__gtype_name__ = "GoBuildAfterSavePlugin"
	view = GObject.property(type=Gedit.View)
	handlers = []

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		"""Activate plugin."""
		self.doc = self.view.get_buffer()
		handler_id = self.doc.connect("saved", self.on_document_saving)
		self.handlers.append(handler_id)

	def do_deactivate(self):
		"""Deactivate plugin."""
		for handler_id in self.handlers:
			self.doc.disconnect(handler_id)		

	def do_update_state(self):
		"""Window state updated"""
		pass

	def on_document_saving(self, *args):
		"""Strip trailing spaces in document."""
		if self.doc.get_language():
			lang = self.doc.get_language().get_name()		
			if lang == "Go":
				self.timeout_command(4.8)	# do not wait for more than 4.8 sec.
			
	def show_error(self, msg):
		if GoBuildGlobal.windowClass != 0:
			GoBuildGlobal.windowClass.setPanelErrorMessage(msg)
			
	def show_msg(self, msg):
		if GoBuildGlobal.windowClass != 0:
			GoBuildGlobal.windowClass.setPanelSimpleMessage(msg)				
			
	def hide(self):
		if GoBuildGlobal.windowClass != 0:
			GoBuildGlobal.windowClass.setPanelNoErrors()	
			
	def timeout_command(self, timeout):
		"""call shell-command with timeout and return blank if does not stop within timeout"""		
		filename = self.doc.get_location().get_basename()
		pdir = os.path.dirname(self.doc.get_location().get_path())
		command = 'cd ' + pdir + ' && go build'
		self.test_mode = False
		if '_test.go' in filename:	# run testing if it is test file
			command = 'cd ' + pdir + ' && go test'
			self.test_mode = True
		
		start = datetime.datetime.now()
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		while p.poll() is None:
			time.sleep(0.1)			
			now = datetime.datetime.now()			
			if (now - start).seconds > timeout:	
				return self.show_error("Timeout: build process takes too long, had to exit.")
		return self.parse_result(filename, p)   # did not time out, parse results

	def parse_result(self, filename, p):		
		output, errors = p.communicate()
		
		if p.returncode:	
			errlist = errors.decode(encoding).split('\n')
			for err in errlist:		
				pos1 = err.find('.go:')
				pos2 = err.find(': ', pos1+1)			
				thisFile = True
				
				if pos1 != -1 and pos2 != -1:
					# extract error message
					if err.find(filename) == -1:
						thisFile = False
						# got error in some other file, show full error msg
						errorMsg = err.strip()
					else:
						errorMsg = err[(pos2+1):].strip()
					
					# extract line number and jump to error
					# if it is this current file with error
					if thisFile:
						pos1 = pos1 + 4
						lineNum = ""
						errors = err[pos1:pos2]
					
						for letter in errors:
							if letter.isdigit():
								lineNum += letter
							else:
								break
					
						lineNum = int(float(lineNum))
				
						# select error line
						self.doc.goto_line(lineNum-1)
						self.view.scroll_to_cursor()
						# Gtk.TextBuffer
						buff = self.view.get_buffer();
						iter1 = buff.get_iter_at_line(lineNum-1)
						iter2 = buff.get_iter_at_line(lineNum)
						# select line to better indicate where error is
						if iter1 and iter2:						
							buff.select_range(iter1, iter2)
						
					self.show_error(errorMsg)
					return	# only capture the very first error

			if self.test_mode:	# we are in test mode
				k = len(output)
				if k > 81: 
					k = 80	# limit output to 80 chars
				output = output[:k]
				output = output.replace("\n", " ")
				self.show_msg(output)
				return
		else:	# not error returned
			self.hide()

class GoBuildAfterSaveWindowPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "GoBuildAfterSaveWindowPlugin"
	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):		
		GoBuildGlobal.windowClass = self
		status_bar = self.window.get_statusbar()
		self._branch_label = Gtk.Label(None)
		self._branch_label.set_selectable(True)
		self._branch_label.set_single_line_mode(True)
		self._branch_label.show()
		
		# Add a container, so the Label does not overflow the vspace of the statusbar
		self._container = Gtk.Frame()
		self._container.show()
		self._container.add(self._branch_label)
		status_bar.pack_end(self._container, expand=False, fill=True, padding=0)
        
		# show all
		self.do_update_state()

	def do_deactivate(self):
		self._branch_label.hide()
		self._container.hide()
		self.window = None
		
	def do_update_state(self):
		pass

	def setPanelErrorMessage(self, msg):
		self._branch_label.set_markup("<span background='#d01010' foreground='#f0f0f0' size='large'> " + msg + " </span>")

	def setPanelSimpleMessage(self, msg):
		self._branch_label.set_markup("<span background='#d0d0d0' foreground='#000000' size='large'> " + msg + " </span>")

	def setPanelNoErrors(self):
		now = datetime.datetime.now()
		self._branch_label.set_markup(" gobuild -- %02d:%02d " % (now.hour, now.minute))	


