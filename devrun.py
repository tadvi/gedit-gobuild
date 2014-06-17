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
# DevRun plugin version 1.0 for GEdit. 
# Runs "go build" but if current filename has _test.go in the name then runs "go test".
# Waits for few seconds and then timeouts if process takes too long, so GEdit would 
# no freeze.
# Current directory is determined based on current open file directory.

from gi.repository import GObject, Gtk, Gdk, Gedit
import re
import subprocess,datetime, os, time
import locale

encoding = locale.getdefaultlocale()[1]

class DevRunGlobal:
	windowClass = 0
	
class DevRunWindowPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "DevRunWindowPlugin"
	window = GObject.property(type=Gedit.Window)
	handlers = []

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):		
		handler_id = self.window.connect('key-press-event', self.on_key_press_event)
		self.handlers.append(handler_id)
		
		DevRunGlobal.windowClass = self
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

	def show_error(self, msg):
		self.setPanelErrorMessage(msg)
			
	def show_msg(self, msg):
		self.setPanelSimpleMessage(msg)				
			
	def hide(self):
		self.setPanelNoErrors()	
	
	def do_deactivate(self):
		for handler_id in self.handlers:
			self.window.disconnect(handler_id)
	
		self._branch_label.hide()
		self._container.hide()
		self.window = None
		
	def timeout_command(self, timeout):
		"""call shell-command with timeout and return blank if does not stop within timeout"""	
		doc = self.window.get_active_document()
		view = self.window.get_active_view()
		if doc == None or view == None:		# if current document not found, do nothing			
			return
						
		filename = doc.get_location().get_basename()
		pdir = os.path.dirname(doc.get_location().get_path())
		command = 'cd ' + pdir + ' && ./dev'
		
		start = datetime.datetime.now()
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		while p.poll() is None:
			time.sleep(0.1)			
			now = datetime.datetime.now()			
			if (now - start).seconds > timeout:	
				return self.show_error("Timeout: build process takes too long, had to exit.")
		return self.parse_result(filename, p)   # did not time out, parse results

	def parse_result(self, filename, p):		
		#output, errors = p.communicate()
		#if p.returncode:	
		#	self.show_error(errorMsg)
		#	return	# only capture the very first error
		#else:	# not error returned
		self.hide()
	
	def on_key_press_event(self, window, event):
		key = Gdk.keyval_name(event.keyval)		
		if key in ('F5', 'f5'):                    
			self.timeout_command(7.8)	# do not wait for more than 4.8 sec.
			
	def do_update_state(self):
		pass

	def setPanelErrorMessage(self, msg):
		self._branch_label.set_markup("<span background='#d01010' foreground='#f0f0f0' size='large'> " + msg + " </span>")

	def setPanelSimpleMessage(self, msg):
		self._branch_label.set_markup("<span background='#d0d0d0' foreground='#000000' size='large'> " + msg + " </span>")

	def setPanelNoErrors(self):
		now = datetime.datetime.now()
		self._branch_label.set_markup("<span background='#d0d0d0' foreground='#000000' size='large'> dev -- %02d:%02d </span>" % (now.hour, now.minute))	


