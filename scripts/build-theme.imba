var fs = require 'fs'
var path = require 'path'
import {colors,scopes,globals,vstheme} from '../imba.theme.imba'

def exportTmTheme
	let scheme = {
		name: "Imba Color Scheme"
		globals: globals
		rules: []
	}
	for scope in scopes
		let item = {
			name: scope[0]
			scope: scope[0]
		}

		if scope[1]
			if scope[1].background
				item.background = scope[1].background
			else
				item.foreground = scope[1]

		if scope[2]
			item.font_style = scope[2]
		scheme.rules.push(item)
	
	let text = JSON.stringify(scheme,null,2)
	let dest = path.join(__dirname,'..','Imba2.sublime-color-scheme')
	fs.writeFileSync(dest,text)
	
def exportVSCodeTheme
	let scheme = {
		name: "Imba Dark"
		type: "dark"
		base: "vs-dark"
		inherit: false
		tokenColors: []
		colors: vstheme
	}
	let rules = scheme.tokenColors
	for scope in scopes
		let style = scope[1]
		let item = {
			name: scope[0]
			scope: scope[0]
			settings: {}
		}
	
		if typeof style == 'string'
			style = {foreground: style}
		item.settings = style
		rules.push(item)
	
	let text = JSON.stringify(scheme,null,2)
	let dest = path.join(__dirname,'..','..','vscode-imba','themes','ImbaDark.json')
	fs.writeFileSync(dest,text)
	

exportTmTheme()
exportVSCodeTheme()

###
{
	"name": "Example Color Scheme",
	"globals":
	{
		"background": "rgb(34, 34, 34)",
		"foreground": "#EEEEEE",
		"caret": "white"
	},
	"rules":
	[
		{
			"name": "Comment",
			"scope": "comment",
			"foreground": "#888888"
		},
		{
			"name": "String",
			"scope": "string",
			"foreground": "hsla(50, 100%, 50%, 1)",
		},
		{
			"name": "Number",
			"scope": "constant.numeric",
			"foreground": "#7F00FF",
			"font_style": "italic",
		}
	]
}

{
  "base": "vs-dark",
  "inherit": false,
  "named": {
	"background": "282f33",
	"lvar": "dcdbc7"
  },
  "tokenColors": [
	{
	  "name": "",
	  "scope": "",
	  "settings": {
		"foreground": "#D4D4D4"
	  }
	},
  ],
  "type": "dark",
  "name": "Imba Dark"
}
###