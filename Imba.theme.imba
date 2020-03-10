var chroma = require('chroma-js')

export var colors = {
	gray100: "#f7fafc"
	gray200: "#edf2f7"
	gray300: "#e2e8f0"
	gray400: "#cbd5e0"
	gray500: "#a0aec0"
	gray600: "#718096"
	gray700: "#4a5568"
	gray800: "#2d3748"
	gray900: "#1a202c"
	red100: "#fff5f5"
	red200: "#fed7d7"
	red300: "#feb2b2"
	red400: "#fc8181"
	red500: "#f56565"
	red600: "#e53e3e"
	red700: "#c53030"
	red800: "#9b2c2c"
	red900: "#742a2a"
	orange100: "#fffaf0"
	orange200: "#feebc8"
	orange300: "#fbd38d"
	orange400: "#f6ad55"
	orange500: "#ed8936"
	orange600: "#dd6b20"
	orange700: "#c05621"
	orange800: "#9c4221"
	orange900: "#7b341e"
	yellow200: "#fefcbf"
	yellow300: "#faf089"
	yellow400: "#f6e05e"
	yellow500: "#ecc94b"
	yellow600: "#d69e2e"
	yellow700: "#b7791f"
	yellow800: "#975a16"
	yellow900: "#744210"
	green100: "#f0fff4"
	green200: "#c6f6d5"
	green300: "#9ae6b4"
	green400: "#68d391"
	green500: "#48bb78"
	green600: "#38a169"
	green700: "#2f855a"
	green800: "#276749"
	green900: "#22543d"
	teal100: "#e6fffa"
	teal200: "#b2f5ea"
	teal300: "#81e6d9"
	teal400: "#4fd1c5"
	teal500: "#38b2ac"
	teal600: "#319795"
	teal700: "#2c7a7b"
	teal800: "#285e61"
	teal900: "#234e52"
	blue100: "#ebf8ff"
	blue200: "#bee3f8"
	blue300: "#90cdf4"
	blue400: "#63b3ed"
	blue500: "#4299e1"
	blue600: "#3182ce"
	blue700: "#2b6cb0"
	blue800: "#2c5282"
	blue900: "#2a4365"
	indigo100: "#ebf4ff"
	indigo200: "#c3dafe"
	indigo300: "#a3bffa"
	indigo400: "#7f9cf5"
	indigo500: "#667eea"
	indigo600: "#5a67d8"
	indigo700: "#4c51bf"
	indigo800: "#434190"
	indigo900: "#3c366b"
	purple100: "#faf5ff"
	purple200: "#e9d8fd"
	purple300: "#d6bcfa"
	purple400: "#b794f4"
	purple500: "#9f7aea"
	purple600: "#805ad5"
	purple700: "#6b46c1"
	purple800: "#553c9a"
	purple900: "#44337a"
	pink100: "#fff5f7"
	pink200: "#fed7e2"
	pink300: "#fbb6ce"
	pink400: "#f687b3"
	pink500: "#ed64a6"
	pink600: "#d53f8c"
	pink700: "#b83280"
	pink800: "#97266d"
	pink900: "#702459"
}

def dim color, amount = 0.2
	chroma(color).saturate(-amount).hex()
	
def darken color, amount = 0.2
	chroma(color).darken(amount).hex()

def mix color, other, amount = 0.5
	chroma.mix(color,other,amount).hex()

// run through and desaturate all the colors
for own name,hex of colors
	let color = chroma(hex)
	// if name.match(/orange/)
	//	color = color.saturate(-1)
	// colors[name] = dim() color.hex()
	//console.log('dimmed',hex,color)



colors.prop = dim(colors.blue300,-0.1)
colors.keyword = dim(colors.red500,0.8)
colors.keyword = mix(colors.red400,colors.orange400,0.5)
colors.keyword = "#e88f76"
colors.ivar = dim(colors.blue300,0.3)
colors.private = dim(colors.yellow300,0.5)
colors.imports = darken(colors.purple300,0.2)
colors.pascal = darken(colors.purple300,0.2)
colors.string = colors.green200
colors.regexp = colors.orange400

colors.tag = dim(colors.yellow300,0.5)
colors.type = colors.gray500 // mix(colors.purple400,colors.blue400) // dim(colors.purple400,2)

export var globals = {
	activeGuide: '#3b5567'
	background: '#111111'
	caret: '#A7A7A7'
	foreground: '#F8F8F8'
	guide: '#202e37'
	invisibles: '#CAE2FB2B'
	// lineHighlight: '#FFFFFF1C'
	selection: '#2b383f'
	stackGuide: '#202e37'
}

export var scopes = [
	['comment',colors.gray600,'italic']
	['keyword',colors.keyword]
	['storage',colors.keyword]
	['constant.numeric',colors.blue400]
	['constant.language.boolean',colors.blue500]
	['constant.language.super',colors.keyword]
	['entity.name',colors.blue300]

	['variable.other',colors.gray200]
	['variable.other.instance',colors.ivar]
	['variable.other.private',colors.private]
	['variable.other.property',colors.gray100]
	['variable.language.super',colors.keyword]
	['variable.language.this',colors.blue400]
	['meta.import variable.other',colors.imports]
			
	['meta.embedded.line',colors.gray200]
	['meta.definition.method entity.name.function',colors.prop]
	['meta.definition.property',colors.prop]
	
	['meta.tag',darken(colors.tag,1)]
	['meta.tag.content',darken(colors.tag,0.2)]
	['entity.name.tag',colors.tag]
	['entity.other.tag.class-name',colors.yellow200]
	
	['support.class',colors.pascal]
	['support.variable',colors.pascal]
	// ['support.function',colors.pascal]
	['support.constant',colors.pascal]
	
	['string.quoted',colors.string]
	['string.template',colors.string]
	['string.regexp',colors.regexp]
	
	['meta.type.annotation',colors.type]
	['meta.type.annotation entity.name',colors.type]

	['keyword.operator.type',colors.type]
	['punctuation.accessor',colors.keyword]
	
	// ['meta.tagtree string.quoted',colors.string]
	// ['meta.import punctuation.definition.block',colors.keyword]
	// ['meta.import punctuation.separator.comma',colors.keyword]
]