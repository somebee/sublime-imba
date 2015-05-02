import sublime, sublime_plugin
import re

# Extends TextCommand so that run() receives a View to modify.  
class ImbaCommaCommand(sublime_plugin.TextCommand):
    def run(self, edit, args = None):
    	loc = self.view.sel()[0]
    	if self.view.match_selector(loc.a,"scope.property.imba"):
    		self.view.run_command("insert",{"characters": ", "})
    		self.view.run_command("auto_complete")
    	else:
    		pass

class ImbaDeleteTagCommand(sublime_plugin.TextCommand):
	def run(self, edit, args = None):
		self.view.run_command("right_delete")
		self.view.run_command("left_delete")
		self.view.run_command("hide_auto_complete")

class ImbaWrapTag(sublime_plugin.TextCommand):
	def run(self, edit, args = None):
		self.view.run_command("right_delete")
		self.view.run_command("left_delete")
		self.view.run_command("hide_auto_complete")

class ImbaOpenTag(sublime_plugin.TextCommand):
	def run(self, edit, args = None):
		self.view.run_command("insert_snippet",{"contents": "<${1:$SELECTION}>"})
		# self.view.run_command("hide_auto_complete")