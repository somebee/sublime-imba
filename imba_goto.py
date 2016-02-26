import sublime
import sublime_plugin

class ImbaGoto(sublime_plugin.TextCommand):
    def run(self, edit):

        """
        Goto Symbol In Index for current cursor position.
        Note: Only does it for first selected region.
        """
        selections = self.view.sel()
        if selections:
            # Get required search word
            region = selections[0]

            if not self.view.match_selector(region.a,"source.imba"):
                return

            if region.a == region.b:
                region = self.view.word(region)
            highlighted = self.view.substr(region)

            if self.view.match_selector(region.a,"entity.name.tag.type,entity.name.tagdef"):
                highlighted = "tag " + highlighted

            if self.view.match_selector(region.a,"accessor.invocation,identifier.basic"):
                highlighted = "def " + highlighted

            if self.view.match_selector(region.a,"identifier.class"):
                highlighted = "class " + highlighted

            # Get definition locations of word
            self.options = self.view.window().lookup_symbol_in_index(highlighted)

            if not self.options:
                sublime.status_message(
                    'Found no definition for "%s".' % highlighted
                )
                return

            # Test if all results are for the same location
            # If they are, don't give a option, just go there
            first_abs_path = None

            for abs_path, proj_path, row_col in self.options:
                file_path = abs_path + ':' + str(row_col[0])
                if first_abs_path is not None and not file_path == first_abs_path:
                    break
                first_abs_path = file_path
            else:
                self.on_done(file_path)
                return

            # Display options in quick panel
            display_options = []
            for option in self.options:
                display_options.append(option[1] + ':' + str(option[2][0]))
            self.view.window().show_quick_panel(
                items=display_options,
                on_select=self.on_done,
                on_highlight=self.on_highlight
            )

    def on_done(self, option):
        """
        Open the specified file on the correct line number.
        """
        if option == -1:
            return
        if isinstance(option, int) or option.isdigit():
            option = self.options[option]
            file_path = option[0] + ':' + str(option[2][0])
        else:
            file_path = option
        self.view.window().open_file(file_path, sublime.ENCODED_POSITION)

    def on_highlight(self, option):
        """
        Preview the specified file on the correct line number.
        """
        option = self.options[option]
        file_path = option[0] + ':' + str(option[2][0])
        self.view.window().open_file(
            file_path,
            sublime.ENCODED_POSITION | sublime.TRANSIENT
        )