from kivy.app import App
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from pygame import font as fonts
import codecs, os
import AST
from Lexer import SMLLexer
from Parser import SMLParser
from Configuration import Configuration

class LoadDialog(Popup):

    def load(self, path, selection):
        self.choosen_file = [None, ]
        self.choosen_file = selection
        Window.title = selection[0][selection[0].rfind(os.sep)+1:]
        self.dismiss()

    def cancel(self):
        self.dismiss()


class SaveDialog(Popup):

    def save(self, path, selection):
        _file = codecs.open(selection, 'w', encoding='utf8')
        _file.write(self.text)
        Window.title = selection[selection.rfind(os.sep)+1:]
        _file.close()
        self.dismiss()

    def cancel(self):
        self.dismiss()

class ConfigPopup(Popup):

  font_size = NumericProperty(14)

  def __init__(self, LMS):
    super(ConfigPopup, self).__init__()
    self.LMS = LMS

  def on_font_size(self, instance, value):
    self.LMS.font_size = value

  def cancel(self):
    print dir(self)
    self.dismiss()

class LMS(Widget):

    error_window_height = NumericProperty(10)
    font_size = NumericProperty(14)
    files = ListProperty([None, ])

    def __init__(self):
      super(LMS, self).__init__()
      self.configuration = Configuration()
      self.lexer  = SMLLexer(self.configuration)
      self.parser = SMLParser(self.configuration)
      self.config_popup = ConfigPopup(self)
      self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
      self._keyboard.bind(on_key_down=self._on_keyboard_down)

      ewh = self.configuration.get_option('GUI_Error_Window_Height')
      if ewh:
        ewh.set_prop(self.error_window_height)
      #Clock.schedule_once(self.initialize, 10)

    def initialize(self, time):
      print dir(self)
      print self.font_size
      print self.config_popup.font_size
      self.error_window_height = 100

    def _keyboard_closed(self):
      pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
      if keycode[0] == 286: # F5
        self.parse()
      return False

    def parse(self):
      tokens = self.lexer.lex(str(self.code_input.text))
      print tokens

      self.parser.clear()
      ASTToplevel, position  = self.parser.parse(tokens)
      print str(ASTToplevel), position
      nodes = []
      ASTToplevel.traverse(lambda x: (nodes.append(x) if x.is_expression else None),
                          pred_recurse = lambda x: x not in nodes)

      self.expression_list.clear_widgets()
      for node in nodes:
        self.expression_list.add_widget(Button(text='%s' % str(node), background_color=[.2, .2, .2, 1]))

      node= nodes[0]
      i = self.expression_tree_image_area.size[1]
      self.expression_tree_image_area.add_widget(Label(text=node.get_token_text(), pos=(self.expression_tree_image_area.size[0]/2, i)))
      for child in node.children:
        i-=20
        self.expression_tree_image_area.add_widget(Label(text=child.get_token_text(), pos=(self.expression_tree_image_area.size[0]/2, i)))
      print self.expression_list.children
      print nodes

    def traverse_ast(self, node, predicate, recurse = True):
      nodes = []
      for child in node.children:
        if predicate(child):
          nodes.append(child)
          if recurse:
            nodes += self.traverse_ast(child, predicate, recurse)
        else:
          nodes += self.traverse_ast(child, predicate, recurse)

      return nodes

    def on_font_size(self, instance, value):
      self.code_input.font_size = value

    def _open_config(self):
      self.config_popup.open()

    def _update_size(self, instance, size):
        self.code_input.font_size = float(size)

    def _update_font(self, instance, fnt_name):
        instance.font_name = self.code_input.font_name =\
            fonts.match_font(fnt_name)

    def _file_menu_selected(self, instance, value):
        if value == 'File':
            return
        instance.text = 'File'
        if value == 'Open':
            if not hasattr(self, 'load_dialog'):
                self.load_dialog = LoadDialog()
            self.load_dialog.open()
            self.load_dialog.bind(choosen_file=self.setter('files'))
        elif value == 'SaveAs':
            if not hasattr(self, 'saveas_dialog'):
                self.saveas_dialog = SaveDialog()
            self.saveas_dialog.text = self.code_input.text
            self.saveas_dialog.open()
        elif value == 'Save':
            if self.files[0]:
                _file = codecs.open(self.files[0], 'w', encoding='utf8')
                _file.write(self.code_input.text)
                _file.close()
        elif value == 'Close':
            if self.files[0]:
                self.code_input.text = ''
                Window.title = 'untitled'

    def on_files(self, instance, values):
        if not values[0]:
            return
        _file = codecs.open(values[0], 'r', encoding='utf8')
        self.code_input.text = _file.read()
        _file.close()

#Factory.register('LMS', LMS)

class LMSApp(App):
    def build(self):
      lms = LMS()
      return lms

if __name__ == '__main__':
    LMSApp().run()
