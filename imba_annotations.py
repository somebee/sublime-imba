import sublime, sublime_plugin
import re
import json
import os
import subprocess
import threading
import _thread as thread
from time import time, sleep
from distutils.spawn import find_executable

IMBA_WARN_CACHE = []
IMBA_HINT_CACHE = {}
CURRENT_ERR_REGION = None
CURRENT_ERR_MSG = None

class ImbaEventTrigger(object):

	def __init__(self):
		self.time = time()
		self.reschedule = False
		self.running = False
		this = self
		self.handler = lambda: this.run_event()
	
	def delay(self,delay):
		if self.running == True:
			 #print("delay - is running - reschedule")
			self.reschedule = True
			self.time = time() * 1000 + delay
		else:
			# print("set timeout now")
			self.running = True
			sublime.set_timeout_async(self.handler,delay)
		pass

	def run_event(self):
		self.running = False

		if self.reschedule == True:
			self.reschedule = False
			# schedule a new event after this
			delta = self.time - time() * 1000

			if delta > 100: # dont wait if it is a very small delta
				self.delay(delta) # using ms
				# print("rescheduled" + str(delta))
				return

		self.running = False
		self.run()
		pass

	def run(self):
		window = sublime.active_window()
		view = window.active_view() if window != None else None
		on_caret_hold(view)
		pass

IMBA_CARET_HOLD_HANDLER = ImbaEventTrigger()


class ImbaDocumentListener(sublime_plugin.EventListener):

	def log(self,str):
		print(str)
		pass

	def init_plugin():
		pass

	def ignore_event(self, view):
		"""
		Ignore request to highlight if the view is a widget,
		or if it is too soon to accept an event.
		"""
		if not view.match_selector(0,"source.imba"): return True
		# syntax = view.settings().get('syntax')
		# not_imba = syntax != "Packages/Imba/Imba.tmLanguage"
		# should ignore everything but imba files
		return view.settings().get('is_widget')

	def on_modified(self, view):
		print('document was modified')
		return

	def on_text_command(self, view, cmd, args):
		print('received text command')
		return

	def on_selection_modified(self,view):
		global CURRENT_ERR_REGION
		# print("selection modified - async")
		if self.ignore_event(view): return
		reg = view.sel()[0]
		# print(reg.a,reg.b,CURRENT_ERR_REGION)
		if CURRENT_ERR_REGION and CURRENT_ERR_REGION.contains(reg):
			# print("already in the region")
			view.show_popup(CURRENT_ERR_MSG, sublime.COOPERATE_WITH_AUTO_COMPLETE) 
			return
		else:
			CURRENT_ERR_REGION = None

		IMBA_CARET_HOLD_HANDLER.delay(1000)
		return

	def on_post_save_async(self, view):
		name, ext = os.path.splitext(view.file_name())

		# only if it has changed
		print("annotate post_save_async?")

		if ext == '.imba':
			start = time()
			data = self.get_annotations_for_view(view)
			print("getting took " + str(time() - start) + "s")
			if view.is_dirty(): return
			show_annotations_for_view(view,data)
			

	def on_load_async(self,view):
		name, ext = os.path.splitext(view.file_name())

		if ext == '.imba':
			data = self.get_annotations_for_view(view)
			if view.is_dirty(): return
			show_annotations_for_view(view,data)

		pass

	def get_annotations_for_view(self, view):
		return get_annotations_for_file(view.file_name())


def add_error(view,message,region):
	options = sublime.PERSISTENT
	options |= sublime.DRAW_NO_OUTLINE
	options |= sublime.DRAW_SOLID_UNDERLINE
	# print('add_error')
	view.add_regions("hint.errors",[region],"hint.warning","dot",options)
	pass

def add_reg(view,data,regions,name,style,options,icon = ""):
	data["regions"].append(name)
	view.add_regions(name,regions,style,icon,options)
	pass

def show_annotations_for_view(view,data):
	start = time()
	prev = get_cached_annotations_for_view(view) # IMBA_HINT_CACHE[str(view.id())] or {}

	prev_regions = view.settings().get("imba.regions",[])
	clear_regions_for_view(view)

	data["regions"] = []
	# add helper-class for different regions?
	# a class that wraps the format output by imba would be very helpful
	icon = ""

	options = sublime.PERSISTENT
	options |= sublime.DRAW_NO_OUTLINE
	options |= sublime.DRAW_SOLID_UNDERLINE
	style = "hint.var"

	class Regs:
  		var = []
  		err = []
  		warn = []


	# for now we just add them all to the same register
	regnr = 0
	scopes = []
	scope_opts = sublime.PERSISTENT

	# regions = []
	varcounts = 0
	selfcounts = 0

	if False:
		if "scopes" in data:
			for scope in data["scopes"]:
				level = scope.get("level",0)
				typ = scope.get("type","Scope")
				region = sublime.Region(scope["loc"][0],scope["loc"][1])
				scopes.append(region)

				for var in scope["vars"]:
					var_regions = []		
					for ref in var["refs"]:
						region = sublime.Region(ref["loc"][0],ref["loc"][1])
						var_regions.append(region)
						varcounts = varcounts + 1
					style = "hint.var" + "." + var.get("type","decl") + "." + typ # + ".level" + str(level)
					add_reg(view,data,var_regions,str(regnr + 1),style,options)
					regnr = regnr + 1
				# print (style)
	# print("add autoself?",data)

	autoselfs = []
	if "autoself" in data:
		for implicit in data["autoself"]:
			style = "hint.var.autoself"
			region = sublime.Region(implicit["loc"][0],implicit["loc"][1])
			autoselfs.append(region)
			selfcounts = selfcounts + 1


	add_reg(view,data,autoselfs,str(regnr + 1),"hint.var.autoself",options)

	view.erase_regions("hint.var")

	# print("added self",selfcounts)
	# print("added vars",varcounts)

	options = sublime.PERSISTENT
	options |= sublime.DRAW_NO_FILL
	options |= sublime.DRAW_NO_OUTLINE
	options |= sublime.DRAW_SOLID_UNDERLINE
	# options |= sublime.DRAW_STIPPLED_UNDERLINE
	style = "hint.warning"
	icon = "dot"
	
	if 'warnings' in data:
		# add warnings
		for warning in data["warnings"]:
			msg = warning["message"]
			loc = warning["loc"]
			region = sublime.Region(loc[0],loc[1])
			Regs.warn.append(region)
		# view.show_popup('hello', sublime.COOPERATE_WITH_AUTO_COMPLETE)

	view.erase_status("errors")

	if 'errors' in data:
		# add warnings
		for note in data["errors"]:
			msg = note["message"]
			reg = None
			if 'loc' in note:
				loc = note["loc"]
				reg = sublime.Region(loc[0],loc[1])
			elif 'line' in note:
				pt = view.text_point(note["line"], 0)
				pt2 = view.text_point(note["line"], 0) 
				reg = sublime.Region(pt,pt2)
			if reg:
				Regs.err.append(reg)
			view.set_status("errors", msg)

	view.add_regions("hint.warning",Regs.warn,style,icon,options)
	view.add_regions("hint.error",Regs.err,style,icon,options)

	view.settings().set("imba.regions", data["regions"])

	IMBA_HINT_CACHE[str(view.id())] = data
	elapsed = time() - start
	print("took " + str(elapsed))
	pass

def get_annotations_for_file(path):

	start = time()
	args = ['imba','analyze',path]

	executable = find_executable("imbac", path="/usr/local/bin:$PATH")

	if executable:
		args = ['imbac','--analyze','--print',path]

	# what about on windows?
	proc = subprocess.Popen(args,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		env={"PATH": "/usr/local/bin:$PATH"}
	)

	output, err = proc.communicate()
	output = output.decode("utf-8")
	elapsed = time() - start
	print("analyze took " + str(elapsed) + "s")
	return json.loads(output)
	# str(output).rstrip(os.linesep).decode('ascii').strip()

def get_cached_annotations_for_view(view):
	return IMBA_HINT_CACHE.get(str(view.id()),None)

def clear_regions_for_view(view):
	view.erase_regions("hint.warning")
	view.erase_regions("hint.error")
	view.erase_regions("hint.var")

	regions = view.settings().get("imba.regions",[])
	
	for region in regions:
		view.erase_regions(region)

	pass

def show_err(view,region,msg):
	global CURRENT_ERR_REGION
	global CURRENT_ERR_MSG
	CURRENT_ERR_REGION = region
	CURRENT_ERR_MSG = msg
	view.show_popup("<b>" + msg + '</b> <a href="moo">details</a>', sublime.HTML, max_width = 600)
	pass

def on_caret_hold(view):
	global CURRENT_ERR_REGION
	global CURRENT_ERR_MSG
	# print('on caret hold')
	# if we are over an error
	sel = view.sel()[0]
	info = None

	for idx,region in enumerate(view.get_regions("hint.warning")):
		if region.contains(sel):
			if info == None:
				info = get_cached_annotations_for_view(view)
			print("warning-region contains caret!",CURRENT_ERR_REGION)
			if info:
				msg = info and info["warnings"][idx]["message"]
				show_err(view,region,msg)

	for idx,region in enumerate(view.get_regions("hint.error")):
		if region.contains(sel):
			if info == None:
				info = get_cached_annotations_for_view(view)
			if info:
				msg = info and info["errors"][idx]["message"]
				show_err(view,region,msg)

	# sublime.run_command("show_auto_complete")
	pass

def blank_function(view):
	pass

def plugin_loaded():
	print("plugin_loaded")
	return
