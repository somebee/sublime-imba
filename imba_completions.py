import sublime, sublime_plugin
import re

import os
import os.path
import re
import glob


if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    # from fsutils import *
else:
    _ST3 = True
    # from .fsutils import *



def getviewcwd(view):
    default = '/' ## What to return if nothing else found
    cwd     = view.file_name() ## Try to get the current view's filename
    if cwd == None:
        cwd = default
        if debug:
            print("FSAutocompletion: getviewcwd: No view filename found")
        ## File is not saved to disk, look for project dir
        window = sublime.active_window()
        if window == None:
            if debug:
                print("FSAutocompletion: getviewcwd: No active window found")
            return cwd ## Give up here if we can't even get an active window!
        try:
            folder = window.project_data()['folders'].pop()
            if debug:
                print("FSAutocompletion: getviewcwd: folder found", folder)
            cwd = folder['path']
        except AttributeError:
            if debug:
                print("FSAutocompletion: getviewcwd: project_data not found, or no folders found in data")
            try:
                folder = window.folders().pop()
                if debug:
                    print("FSAutocompletion: getviewcwd: folder found", folder)
                cwd = folder.path
            except AttributeError:
                if debug:
                    print("FSAutocompletion: getviewcwd: folders() not found, or was empty list")
                pass
        if debug:
            print("FSAutocompletion: getviewcwd: returning cwd", cwd)
        return cwd
    else:
        return os.path.dirname(cwd)



def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

def make_completion(tag):
    # make it look like
    # ("table\tTag", "table>$1</table>"),
    return (tag + "\t" + '<' + tag + '>', tag + "$0") # hmm


def make_auto_completion(item,type):
    # make it look like
    # ("table\tTag", "table>$1</table>"),
    return (item + "\t" + type, item)

def get_tag_to_attributes():
    # maps tags to all available attributes
    return (
        {
        'all': ['title','tabindex','style'],
        'a' : ['accesskey', 'charset', 'coords', 'dir', 'href', 'hreflang', 'lang', 'name', 'rel', 'rev', 'shape', 'style', 'tabindex', 'target', 'title', 'type'],
        'applet' : ['align', 'alt', 'archive', 'code', 'codebase', 'height', 'hspace', 'name', 'object', 'style', 'title', 'vspace', 'width'],
        'area' : ['accesskey', 'alt', 'coords', 'dir', 'href', 'lang', 'nohref', 'shape', 'style', 'tabindex', 'target', 'title'],
        'base' : ['href', 'target'],
        'basefont' : ['color', 'face', 'size'],
        'bdo' : ['dir', 'lang', 'style', 'title'],
        'blockquote' : ['cite', 'dir', 'lang', 'style', 'title'],
        'body' : ['alink', 'background', 'bgcolor', 'dir', 'lang', 'link', 'style', 'text', 'title', 'vlink'],
        'br' : ['clear', 'style', 'title'],
        'button' : ['accesskey', 'dir', 'disabled', 'lang', 'name', 'style', 'tabindex', 'title', 'type', 'value'],
        'caption' : ['align', 'dir', 'lang', 'style', 'title'],
        'col' : ['align', 'char', 'charoff', 'dir', 'lang', 'span', 'style', 'title', 'valign', 'width'],
        'colgroup' : ['align', 'char', 'charoff', 'dir', 'lang', 'span', 'style', 'title', 'valign', 'width'],
        'del' : ['cite', 'datetime', 'dir', 'lang', 'style', 'title'],
        'dir' : ['compact', 'dir', 'lang', 'style', 'title'],
        'div' : ['align', 'dir', 'lang', 'style', 'title'],
        'dl' : ['compact', 'dir', 'lang', 'style', 'title'],
        'font' : ['color', 'dir', 'face', 'lang', 'size', 'style', 'title'],
        'form' : ['accept-charset', 'accept', 'action', 'dir', 'enctype', 'lang', 'method', 'name', 'style', 'target', 'title'],
        'frame' : ['frameborder', 'longdesc', 'marginheight', 'marginwidth', 'name', 'noresize', 'scrolling', 'src', 'style', 'title'],
        'frameset' : ['cols', 'rows', 'style', 'title'],
        'h1' : ['align', 'dir', 'lang', 'style', 'title'],
        'h2' : ['align', 'dir', 'lang', 'style', 'title'],
        'h3' : ['align', 'dir', 'lang', 'style', 'title'],
        'h4' : ['align', 'dir', 'lang', 'style', 'title'],
        'h5' : ['align', 'dir', 'lang', 'style', 'title'],
        'h6' : ['align', 'dir', 'lang', 'style', 'title'],
        'head' : ['dir', 'lang', 'profile'],
        'hr' : ['align', 'dir', 'lang', 'noshade', 'size', 'style', 'title', 'width'],
        'html' : ['dir', 'lang', 'version'],
        'iframe' : ['align', 'frameborder', 'height', 'longdesc', 'marginheight', 'marginwidth', 'name', 'scrolling', 'src', 'style', 'title', 'width'],
        'img' : ['align', 'alt', 'border', 'dir', 'height', 'hspace', 'ismap', 'lang', 'longdesc', 'name', 'src', 'style', 'title', 'usemap', 'vspace', 'width'],
        'input' : ['accept', 'accesskey', 'align', 'alt', 'checked', 'dir', 'disabled', 'ismap', 'lang', 'maxlength', 'name', 'readonly', 'size', 'src', 'style', 'tabindex', 'title', 'type', 'usemap', 'value'],
        'ins' : ['cite', 'datetime', 'dir', 'lang', 'style', 'title'],
        'isindex' : ['dir', 'lang', 'prompt', 'style', 'title'],
        'label' : ['accesskey', 'dir', 'for', 'lang', 'style', 'title'],
        'legend' : ['accesskey', 'align', 'dir', 'lang', 'style', 'title'],
        'li' : ['dir', 'lang', 'style', 'title', 'type', 'value'],
        'link' : ['charset', 'dir', 'href', 'hreflang', 'lang', 'media', 'rel', 'rev', 'style', 'target', 'title', 'type'],
        'map' : ['dir', 'lang', 'name', 'style', 'title'],
        'menu' : ['compact', 'dir', 'lang', 'style', 'title'],
        'meta' : ['content', 'dir', 'http-equiv', 'lang', 'name', 'scheme'],
        'object' : ['align', 'archive', 'border', 'classid', 'codebase', 'codetype', 'data', 'declare', 'dir', 'height', 'hspace', 'lang', 'name', 'standby', 'style', 'tabindex', 'title', 'type', 'usemap', 'vspace', 'width'],
        'ol' : ['compact', 'dir', 'lang', 'start', 'style', 'title', 'type'],
        'optgroup' : ['dir', 'disabled', 'label', 'lang', 'style', 'title'],
        'option' : ['dir', 'disabled', 'label', 'lang', 'selected', 'style', 'title', 'value'],
        'p' : ['align', 'dir', 'lang', 'style', 'title'],
        'param' : ['name', 'type', 'value', 'valuetype'],
        'pre' : ['dir', 'lang', 'style', 'title', 'width'],
        'q' : ['cite', 'dir', 'lang', 'style', 'title'],
        'script' : ['charset', 'defer', 'language', 'src', 'type'],
        'select' : ['dir', 'disabled', 'lang', 'multiple', 'name', 'size', 'style', 'tabindex', 'title'],
        'style' : ['dir', 'lang', 'media', 'title', 'type'],
        'table' : ['align', 'bgcolor', 'border', 'cellpadding', 'cellspacing', 'dir', 'frame', 'lang', 'rules', 'style', 'summary', 'title', 'width'],
        'tbody' : ['align', 'char', 'charoff', 'dir', 'lang', 'style', 'title', 'valign'],
        'td' : ['abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colspan', 'dir', 'headers', 'height', 'lang', 'nowrap', 'rowspan', 'scope', 'style', 'title', 'valign', 'width'],
        'textarea' : ['accesskey', 'cols', 'dir', 'disabled', 'lang', 'name', 'readonly', 'rows', 'style', 'tabindex', 'title'],
        'tfoot' : ['align', 'char', 'charoff', 'dir', 'lang', 'style', 'title', 'valign'],
        'th' : ['abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colspan', 'dir', 'headers', 'height', 'lang', 'nowrap', 'rowspan', 'scope', 'style', 'title', 'valign', 'width'],
        'thead' : ['align', 'char', 'charoff', 'dir', 'lang', 'style', 'title', 'valign'],
        'tr' : ['align', 'bgcolor', 'char', 'charoff', 'dir', 'lang', 'style', 'title', 'valign'],
        'ul' : ['compact', 'dir', 'lang', 'style', 'title', 'type'],}
        )

def get_pseudo_selectors():
    items = (['before','after','hover','selected','focus','active'])
    return [make_auto_completion(item,'pseudo-selector') for item in items]

def get_html_tags():
    items = (["a","abbr", "acronym", "address", "applet", "area", "b", "base", "big", "blockquote", "body", "button", "center", "caption",
            "cdata", "cite", "col", "colgroup", "code", "div", "dd", "del", "dfn", "dl", "dt", "em", "fieldset", "font", "form", "frame", "frameset",
            "head", "h1", "h2", "h3", "h4", "h5", "h6", "i", "ins", "kbd", "li", "label", "legend", "map", "noframes", "object", "ol", "optgroup", "option",
            "p", "pre", "span", "samp", "select", "small", "strong", "sub", "sup", "table", "tbody", "td", "textarea", "tfoot", "th", "thead", "title",
            "tr", "tt", "u", "ul", "var", "article", "aside", "audio", "canvas", "footer", "header", "nav", "section", "video"])
    return items

class ImbaCompletions(sublime_plugin.EventListener):
    """
    Provide tag completions for Imba
    It matches just after typing the first letter of a tag name
    """
    def __init__(self):
        completion_list = self.default_completion_list()
        self.prev_prefix = "<<"
        self.prefix_completion_dict = {}
        self.default_pseudo_selectors = get_pseudo_selectors()
        self.complete_context = None
        self.default_html_tags = [make_auto_completion(item,'tag') for item in get_html_tags()]
        self.prefix_tag_completion = [make_completion(item) for item in get_html_tags()]
        
        # construct a dictionary where the key is first character of
        # the completion list to the completion
        for s in completion_list:
            prefix = s[0][0]
            self.prefix_completion_dict.setdefault(prefix, []).append(s)

        # construct a dictionary from (tag, attribute[0]) -> [attribute]
        self.tag_to_attributes = get_tag_to_attributes()


    def get_selector_classes(self,view):
        items = []
        symbols = view.find_by_selector("entity.name.tag.class")
        for sym in symbols:
            ref = view.substr(sym)
            if len(ref) == 1: continue
            items.append(ref)

        return [(ref,ref) for ref in sorted(set(items))]

    def get_selector_ids(self,view,prefix = None):
        symbols = view.find_by_selector("entity.name.tag.id")
        items = []
        for sym in symbols:
            ref = view.substr(sym)
            if len(ref) == 1: continue
            items.append(ref)

        return [(ref,ref) for ref in sorted(set(items))]
        # return [(prefix+"app\ttag","app")]

    def get_ivars(self,view,ctx = None):
        # could also just do a regex in the file,no?
        seen = {}
        scope = None

        if ctx:
            classes = view.find_by_selector("scope.class.imba")
            for r in classes:
                name = view.substr(view.word(r.a - 2))
                print(name)
                if r.contains(ctx): scope = r

        ivars = view.find_by_selector("variable.instance")
        props = view.find_by_selector("entity.name.property")
        # both = view.find_by_selector("variable.instance,entity.name.property")
        names = []
        items = []

        for r in props:
            if scope and not scope.contains(r): continue
            ref = "@"+view.substr(r)
            names.append(ref)

        for r in ivars:
            if scope and not scope.contains(r): continue
            ref = view.substr(r)
            names.append(ref)

        items = [(ref + "\tivar",ref) for ref in sorted(set(names))]
        return items
        # return [("canvas\tclass","canvas")]

    def match_type(self,view,loc,typ):
        return view.match_selector(loc,"entity.name.tag." + typ)


    def tag_type(self,view,loc):
        start = view.find_by_class(loc,False, sublime.CLASS_PUNCTUATION_END, "<")
        # to = view.find_by_class(loc,False, sublime.CLASS_WORD_START, "<")
        typ = view.substr(view.word(start))
        print("tag type starts at",loc,start,typ)
        return typ
    

    def on_query_completions(self, view, prefix, locations):

        if not view.match_selector(locations[0],"source.imba"): return []

        print('prefix:', prefix)

        if len(prefix) > 1 and prefix.startswith(self.prev_prefix):
            # is this right?
            print('prefix starts with the previous(!)')
            return ([],sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        self.prev_prefix = prefix

        warn = view.get_status("hint.warning")
        if warn:
            print(warn)
            view.erase_status("hint.warning")
            return [(prefix + ": " + warn + "\t" + "warning", "hint.warning")]
        
        #print('scope_name before:', view.scope_name(locations[0] - 1))
        loc = locations[0]
        word = view.word(loc)
        char = view.substr(loc - 1)
        items = []



        if len(prefix) > 0:
            char = view.substr(word.a - 1)

        in_tag = view.match_selector(loc,"meta.tag")
        tag_type = None
        spaced = char == " "

        if in_tag:
            tag_type = self.tag_type(view,loc)

        print('info:',prefix,loc,char,in_tag,spaced)

        # if view.match_selector(loc,"identifier.singletag.imba")
        if view.match_selector(loc,"string.quoted.filepath"):
            return self.get_path_completions(view,prefix,locations)

        if char == '@':
            items = self.get_ivars(view,locations[0])

        elif in_tag:

            if spaced:
                print("attributes")
                attrmap = self.tag_to_attributes
                attrs = attrmap.get(tag_type,attrmap["all"])

                if attrs:
                    items = [(ref,ref + "=${1:val}") for ref in attrs]

            elif char == ".":
                items = self.get_selector_classes(view)
                self.complete_context = "."
            elif char == "#":
                items = self.get_selector_ids(view)
                self.complete_context = "#"
            elif char == '<' or self.match_type(view,loc - 1,"type"):
                items.extend(self.default_html_tags)

        elif view.match_selector(locations[0],"meta.selector"):
            items = []
            print('autocomplete ' + char)
            if char == ".":
                items = self.get_selector_classes(view)
            elif char == "#":
                items = self.get_selector_ids(view)
                self.complete_context = "#"
            elif char == ":":
                items = self.default_pseudo_selectors
            elif char == " ":
                items = self.default_html_tags

        elif char == "<":
            return self.prefix_tag_completion
            # items = (items,sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
            # return items

        elif char == "#" or view.match_selector(loc - 1,"identifier.singletag.imba"):
            items = self.get_selector_ids(view,'#')

        elif view.match_selector(loc - 1,"comment"):
            return (items,sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        else:
            return (items,sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        return (items,sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        # basically returning nothing?!?

        # check if we are inside a tag
        is_inside_tag = view.match_selector(locations[0],
                "text.html meta.tag - text.html punctuation.definition.tag.begin")

        return self.get_completions(view, prefix, locations, is_inside_tag)

    def on_modified(self,view):
        # print("on_modified from completions!")
        pass

    def on_text_command(self,view, command_name, args):
        region = view.sel()[0]
        char = view.substr(region.a - 1)
        # print("on_text_command from completions!" + command_name + char)
        if command_name == "left_delete" and (char == "#" or char == "@" or char == "%"):
            view.run_command("hide_auto_complete")
        pass

    def on_window_command(self,view, command_name, args):
        # print("on_window_command from completions!" + command_name)
        pass

    def get_path_completions(self, view, prefix, locations):


        region = view.extract_scope(locations[0])
        region = sublime.Region(region.a + 1, region.b - 1)
        base = sublime.Region(region.a,locations[0] - len(prefix))
        path = view.substr(region)
        word = view.word(region)

        rel = getviewcwd(view) + '/'

        if rel == '//':
            return []

        realpath = os.path.realpath(rel + view.substr(base))
        # print(path,region,word,view.substr(base),rel,realpath)

        items = []

        for f in glob.iglob(realpath + "/*"): # generator, search immediate subdirectories 
            name = f.replace(realpath + '/','')
            if os.path.isdir(f):
                name = name + '/'
            
            items.append((name + '\t' + f,name.replace('.imba','')))

        return (items,sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


    def get_completions(self, view, prefix, locations, is_inside_tag):
        # see if it is in tag.attr or tag#attr format
        pt = locations[0] - len(prefix) - 1
        ch = view.substr(sublime.Region(pt, pt + 1))

        # print('prefix:', prefix)
        # print('location0:', locations[0])
        # print('substr:', view.substr(sublime.Region(locations[0], locations[0] + 3)), '!end!')
        # print('is_inside_tag', is_inside_tag)
        # print('ch:', ch)

        completion_list = []
        if is_inside_tag and ch != '<':
            if ch in [' ', '\t', '\n']:
                # maybe trying to type an attribute
                completion_list = self.get_attribute_completions(view, locations[0], prefix)
            # only ever trigger completion inside a tag if the previous character is a <
            # this is needed to stop completion from happening when typing attributes
            return (completion_list, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        if prefix == '':
            # need completion list to match
            return ([])

        # match completion list using prefix
        completion_list = self.prefix_completion_dict.get(prefix[0], [])

        # if the opening < is not here insert that
        if ch != '<':
            completion_list = [(pair[0], '<' + pair[1]) for pair in completion_list]

        flags = 0

        if is_inside_tag:
            sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS

        return (completion_list, flags)

    def default_completion_list(self):
        """ generate a default completion list for Imba """
        default_list = []
        normal_tags = (["abbr", "acronym", "address", "applet", "area", "b", "base", "big", "blockquote", "body", "button", "center", "caption",
            "cdata", "cite", "col", "colgroup", "code", "div", "dd", "del", "dfn", "dl", "dt", "em", "fieldset", "font", "form", "frame", "frameset",
            "head", "h1", "h2", "h3", "h4", "h5", "h6", "i", "ins", "kbd", "li", "label", "legend", "map", "noframes", "object", "ol", "optgroup", "option",
            "p", "pre", "span", "samp", "select", "small", "strong", "sub", "sup", "table", "tbody", "td", "textarea", "tfoot", "th", "thead", "title",
            "tr", "tt", "u", "ul", "var", "article", "aside", "audio", "canvas", "footer", "header", "nav", "section", "video"])

        for tag in normal_tags:
            default_list.append(make_completion(tag))
            default_list.append(make_completion(tag.upper()))

        default_list += ([
            ("a\tTag", "a href=\"$1\">$0</a>"),
            ("iframe\tTag", "iframe src=\"$1\">$0</iframe>"),
            ("link\tTag", "link rel=\"stylesheet\" type=\"text/css\" href=\"$1\">"),
            ("script\tTag", "script type=\"${1:text/javascript}\">$0</script>"),
            ("style\tTag", "style type=\"${1:text/css}\">$0</style>"),
            ("img\tTag", "img src=\"$1\">"),
            ("param\tTag", "param name=\"$1\" value=\"$2\">")
        ])

        return default_list


    def get_attribute_completions(self, view, pt, prefix):
        SEARCH_LIMIT = 500
        search_start = max(0, pt - SEARCH_LIMIT - len(prefix))
        line = view.substr(sublime.Region(search_start, pt + SEARCH_LIMIT))

        line_head = line[0:pt - search_start]
        line_tail = line[pt - search_start:]

        # find the tag from end of line_head
        i = len(line_head) - 1
        tag = None
        space_index = len(line_head)
        while i >= 0:
            c = line_head[i]
            if c == '<':
                # found the open tag
                tag = line_head[i + 1:space_index]
                break
            if c == ' ':
                space_index = i
            i -= 1

        # check that this tag looks valid
        if not tag or not tag.isalnum():
            return []

        # determines whether we need to close the tag
        # default to closing the tag
        suffix = '>'

        for c in line_tail:
            if c == '>':
                # found end tag
                suffix = ''
                break
            if c == '<':
                # found another open tag, need to close this one
                break

        if suffix == '' and not line_tail.startswith(' ') and not line_tail.startswith('>'):
            # add a space if not there
            suffix = ' '

        # got the tag, now find all attributes that match
        attributes = self.tag_to_attributes.get(tag, [])
        # ("class\tAttr", "class="$1">"),
        attri_completions = [(a + '\tAttr', a + '="$1"' + suffix) for a in attributes]
        return attri_completions

