# -*- coding: utf-8 -*-

# Author: safina3d
# Blog: https://safina3d.blogspot.com


import os
import c4d
from c4d import plugins, gui, bitmaps

PLUGIN_ID = 1027598
PLUGIN_VERSION = '1.3.5'


class LetterShape:
    """ Character shape depending on its position within a word."""
    ISOLATED = 0
    INITIAL = 2
    MIDDLE = 3
    FINAL = 1

    def __init__(self): pass


class LinkType:
    """ Character link types """
    WITHOUT = 0
    BEFORE = 1
    BOTH = 2
    EXTENSION = 3

    def __init__(self): pass


class AbjadData:

    HAMZA_DECIMAL_VALUE = 1569

    LAM_DECIMAL_VALUE = 1604

    FATHATAN_DECIMAL_VALUE = 1611

    SHADDA_DECIMAL_VALUE = 1617

    SOUKOUN_DECIMAL_VALUE = 1618

    LINK_TYPE_LIST = [
        LinkType.WITHOUT, LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE,
        LinkType.BOTH, LinkType.BEFORE, LinkType.BOTH, LinkType.BEFORE, LinkType.BOTH, LinkType.BOTH,
        LinkType.BOTH, LinkType.BOTH, LinkType.BOTH, LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE,
        LinkType.BEFORE, LinkType.BOTH, LinkType.BOTH, LinkType.BOTH, LinkType.BOTH, LinkType.BOTH,
        LinkType.BOTH, LinkType.BOTH, LinkType.BOTH, LinkType.WITHOUT, LinkType.WITHOUT, LinkType.WITHOUT,
        LinkType.WITHOUT, LinkType.WITHOUT, LinkType.EXTENSION, LinkType.BOTH, LinkType.BOTH, LinkType.BOTH,
        LinkType.BOTH, LinkType.BOTH, LinkType.BOTH, LinkType.BOTH, LinkType.BEFORE, LinkType.BOTH,
        LinkType.BOTH, LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE,
        LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE, LinkType.BEFORE
    ]

    ARABIC_FORM_B_VALUES = [
        65152, 65153, 65155, 65157, 65159, 65161, 65165, 65167, 65171, 65173,
        65177, 65181, 65185, 65189, 65193, 65195, 65197, 65199, 65201, 65205,
        65209, 65213, 65217, 65221, 65225, 65229, 1595, 1596, 1597, 1598,
        1599, 1600, 65233, 65237, 65241, 65245, 65249, 65253, 65257, 65261,
        65263, 65265, 65136, 65138, 65140, 65142, 65144, 65146, 65148, 65150
    ]

    ALIF_VALUES = [1570, 1571, 1573, 1575]

    LAM_ALIF_VALUES = [65275, 65269, 65271, 65275, 65273, 65275, 65275]

    SHADDA_VALUES = [64608, 64606, 64607, 64608, 64609, 64610, 64754, 64755, 64756]

    def __init__(self): pass


class Character:

    def __init__(self, character):
        self.character = character
        self.decimal_value = ord(character)
        self.is_arabic_character = False
        self.shape = LetterShape.ISOLATED
        self.link_type = LinkType.WITHOUT
        self.offset = None
        self.__update_char_values()

    def __update_char_values(self):
        """ private: update the default values if the passed current character is arabic """
        self.is_arabic_character = AbjadData.HAMZA_DECIMAL_VALUE <= self.decimal_value <= AbjadData.SOUKOUN_DECIMAL_VALUE

        if self.is_arabic_character:
            self.offset = self.decimal_value - AbjadData.HAMZA_DECIMAL_VALUE
            self.link_type = AbjadData.LINK_TYPE_LIST[self.offset]

    def is_special_char(self):
        return not (self.character.isalnum() or self.is_tachkil())

    def is_alif(self):
        return self.decimal_value in AbjadData.ALIF_VALUES

    def is_hamza(self):
        return self.decimal_value == AbjadData.HAMZA_DECIMAL_VALUE

    def is_lam(self):
        return self.decimal_value == AbjadData.LAM_DECIMAL_VALUE

    def is_tachkil(self):
        return AbjadData.FATHATAN_DECIMAL_VALUE <= self.decimal_value <= AbjadData.SOUKOUN_DECIMAL_VALUE

    def is_shadda(self):
        return self.decimal_value == AbjadData.SHADDA_DECIMAL_VALUE

    def can_be_connected_to(self, other_char):
        return self.link_type != LinkType.WITHOUT and (other_char.link_type == LinkType.BOTH or other_char.link_type == LinkType.EXTENSION)

    def transform_char(self):

        if self.is_special_char():
            return self.flip_special_char()

        if self.is_arabic_character:

            decimal_value = AbjadData.ARABIC_FORM_B_VALUES[self.offset]

            if self.link_type == LinkType.WITHOUT:
                return unichr(decimal_value)
            if self.link_type == LinkType.BEFORE:
                return unichr(decimal_value + self.shape % 2)
            if self.link_type == LinkType.BOTH:
                return unichr(decimal_value + self.shape)

        return self.character

    def transform_lam_alif_char(self):
        decimal_value = AbjadData.LAM_ALIF_VALUES[self.offset] + self.shape % 2
        return unichr(decimal_value)

    def transform_shadda_char(self):
        index = self.offset % 42 + 3 * (self.shape % 2)
        if index < len(AbjadData.SHADDA_VALUES):
            return unichr(AbjadData.SHADDA_VALUES[index])
        return unichr(65148 + self.shape % 2)

    def flip_special_char(self):
        """ Returns the opposite character """
        if self.character == '(':
            return ')'
        if self.character == ')':
            return '('
        if self.character == '{':
            return '}'
        if self.character == '}':
            return '{'
        if self.character == '[':
            return ']'
        if self.character == ']':
            return '['
        if self.character == '<':
            return '>'
        if self.character == '>':
            return '<'
        if self.character == ',':
            return unichr(1548)
        if self.character == ';':
            return unichr(1563)
        if self.character == '?':
            return unichr(1567)
        if self.character == unichr(171):
            return unichr(187)
        if self.character == unichr(187):
            return unichr(171)
        return self.character


class Text:

    def __init__(self, user_text):
        self.user_text = user_text.decode('utf-8')

    def get_word_list(self):
        """ Split the given text into words """
        word_list = []
        current_word = ''
        for c in self.user_text:
            char = Character(c)
            if char.is_special_char() and not char.is_tachkil():
                if current_word:
                    word_list.append(current_word)
                    current_word = ''
                word_list.append(c)
            else:
                current_word += c
        if current_word:
            word_list.append(current_word)
        return word_list

    @staticmethod
    def is_last_letter(word, index):
        return Text.get_next_letter(word, index)[0] is None

    @staticmethod
    def is_shadda_context(current_char, next_char):
        if next_char is None:
            return False
        return current_char.is_shadda() and next_char.is_tachkil() or current_char.is_tachkil() and next_char.is_shadda()

    @staticmethod
    def is_lam_alif_context(current_char, next_letter):
        if next_letter is None:
            return False
        return current_char.is_lam() and next_letter.is_alif()

    @staticmethod
    def get_next_char(word, index):
        word_length = len(word)
        current_index = index + 1
        return Character(word[current_index]) if 0 <= current_index < word_length else None

    @staticmethod
    def get_previous_char(word, index):
        word_length = len(word)
        current_index = index - 1
        return Character(word[current_index]) if 0 <= current_index < word_length else None

    @staticmethod
    def get_next_letter(word, index):
        word_length = len(word)
        current_index = index + 1
        while current_index < word_length:
            current_char = Character(word[current_index])
            if not current_char.is_tachkil():
                return current_char, current_index
            current_index += 1
        return None, None

    @staticmethod
    def get_previous_letter(word, index):
        word_length = len(word)
        if word_length == 0:
            return None
        current_index = index - 1
        while current_index >= 0:
            current_char = Character(word[current_index])
            if not current_char.is_tachkil():
                return current_char, current_index
            current_index -= 1
        return None, None

    @staticmethod
    def transform_word(word):
        """ Projection: from Arabic to Arabic Presentation Forms-B """
        result_word = ''
        word_length = len(word)
        last_char_index = word_length - 1
        index = 0

        while index < word_length:

            previous_char = Text.get_previous_char(word, index)
            current_char = Character(word[index])
            next_char = Text.get_next_char(word, index)

            previous_letter, previous_letter_index = Text.get_previous_letter(word, index)
            next_letter, next_letter_index = Text.get_next_letter(word, index)

            next_index = index + 1

            if not current_char.is_arabic_character and not current_char.is_special_char():
                return word

            # Lam Alif case
            if Text.is_lam_alif_context(current_char, next_letter):
                    if index == 0:
                        next_letter.shape = LetterShape.INITIAL
                    else:
                        if current_char.can_be_connected_to(previous_letter):
                            next_letter.shape = LetterShape.MIDDLE
                        else:
                            next_letter.shape = LetterShape.INITIAL
                    result_word += next_letter.transform_lam_alif_char()
                    index += (next_letter_index - index) + 1
                    continue

            # Shadda case
            if Text.is_shadda_context(current_char, next_char):
                tachkil_char = next_char if current_char.is_shadda() else current_char
                if previous_char and current_char.can_be_connected_to(previous_char) and next_index < last_char_index:
                    tachkil_char.shape = LetterShape.MIDDLE
                result_word += tachkil_char.transform_shadda_char()
                index += 2
                continue

            # Tachkil case
            if current_char.is_tachkil():
                if current_char.can_be_connected_to(previous_char) and index != last_char_index:
                    current_char.shape = LetterShape.MIDDLE
            else:
                if index == 0:
                    if not Text.is_last_letter(word, index):
                        current_char.shape = LetterShape.INITIAL
                elif 0 < index < last_char_index:
                    if Text.is_last_letter(word, index) or (next_letter and next_letter.is_hamza()):
                        if current_char.can_be_connected_to(previous_letter):
                            current_char.shape = LetterShape.FINAL
                    else:
                        if current_char.can_be_connected_to(previous_letter):
                            current_char.shape = LetterShape.MIDDLE
                        else:
                            current_char.shape = LetterShape.INITIAL
                else:
                    if current_char.can_be_connected_to(previous_letter):
                        current_char.shape = LetterShape.FINAL

            result_word += current_char.transform_char()
            index += 1

        return result_word[::-1]

    def transform_text(self):
        word_list = self.get_word_list()
        word_list.reverse()
        result_text = ''
        for word in word_list:
            result_text += Text.transform_word(word)
        return result_text

    def text_to_unicode_string(self):
        ucn = ''
        for char in self.user_text:
            _0x_value = hex(ord(char))
            hex_value = _0x_value[2:]
            zeros = (4 - len(hex_value)) * '0'
            ucn += '\u' + zeros + hex_value
        return ucn


class Zarabic(plugins.CommandData):

    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ErrorGui()

        screen_dimensions = gui.GeGetScreenDimensions(1, 1, False)
        xpos = 0.5 * screen_dimensions['sx2'] - 150
        ypos = 0.5 * screen_dimensions['sy2'] - 50
        current_object = doc.GetActiveObject()

        if current_object is None:
            self.dialog.setMessage('No Text/MoText object selected !')
            return self.dialog.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, xpos, ypos, 300, 100)
        else:
            if Zarabic.is_text_object(current_object):
                doc.StartUndo()
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, current_object)
                original_text = current_object[c4d.PRIM_TEXT_TEXT]
                result = ''
                phrases = original_text.splitlines(False)
                for phrase in phrases:
                    text = Text(phrase)
                    result += text.transform_text() + '\n'

                result = result.strip().encode('utf-8')

                if c4d.GetC4DVersion() > 13016:
                    current_object[c4d.PRIM_TEXT_TEXT] = result
                else:
                    # Cinema 4D R13.016 fix
                    text = Text(result)
                    current_object[c4d.PRIM_TEXT_TEXT] = text.text_to_unicode_string()

                doc.EndUndo()
            else:
                self.dialog.setMessage(current_object.GetTypeName() + ' is not a Text/MoText object !')
                return self.dialog.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, xpos, ypos, 300, 100)

        c4d.EventAdd()
        return True

    @staticmethod
    def is_text_object(c4d_object):
        """ Return true if the passed object type is Text or MoText, otherwise false """
        return 5178 == c4d_object.GetType() or 1019268 == c4d_object.GetType() or 'Text' == c4d_object.GetTypeName() or 'MoText' == c4d_object.GetTypeName()


class UserArea(gui.GeUserArea):
    def __init__(self):
        super(UserArea, self).__init__()
        self.bmp = bitmaps.BaseBitmap()
        self.bmp.InitWith(os.path.join(os.path.dirname(__file__), 'res', 'zarabic.png'))

    def DrawMsg(self, x1, y1, x2, y2, msg):
        self.DrawSetPen(c4d.COLOR_BG)
        self.DrawRectangle(x1, y1, x2, y2)
        w, h = self.bmp.GetSize()
        self.DrawBitmap(self.bmp, 10, 10, w, h, 0, 0, w, h, c4d.BMP_ALLOWALPHA)


class ErrorGui(gui.GeDialog):

    def __init__(self):
        self.message = ''
        self.user_area = UserArea()

    def setMessage(self, message):
        self.message = message

    def CreateLayout(self):
        self.SetTitle('zArabic ' + PLUGIN_VERSION)
        self.GroupBegin(10, c4d.BFH_SCALEFIT)
        self.GroupBorderSpace(2, 2, 2, 2)
        self.AddUserArea(1000, c4d.BFH_LEFT, 128, 64)
        self.AttachUserArea(self.user_area, 1000)
        self.AddStaticText(1001, c4d.BFH_SCALE | c4d.BFH_FIT, 0, 0, self.message, c4d.BORDER_WITH_TITLE_BOLD)
        self.GroupEnd()
        return True

if __name__ == '__main__':
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(os.path.dirname(__file__), 'res', 'zarabic.png'))
    plugins.RegisterCommandPlugin(PLUGIN_ID, 'zArabic ' + PLUGIN_VERSION, 0, icon, 'Write arabic in Cinema4D ;)', Zarabic())
