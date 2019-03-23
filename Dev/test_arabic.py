# -*- coding: utf-8 -*-

import unittest

from arabic import Character, LetterShape, LinkType, Text


class TestCharacter(unittest.TestCase):

    def test_init(self):
        # Non Arabic char
        txt = 'A'.decode('utf-8')
        char = Character(txt)

        self.assertEquals(char.decimal_value, 65)
        self.assertFalse(char.is_arabic_character)
        self.assertEquals(char.shape, LetterShape.ISOLATED)
        self.assertEquals(char.link_type, LinkType.WITHOUT)
        self.assertEquals(char.offset, None)

        # Arabic char
        txt = 'م'.decode('utf-8')
        char = Character(txt)

        self.assertEquals(char.decimal_value, 1605)
        self.assertTrue(char.is_arabic_character)
        self.assertEquals(char.shape, LetterShape.ISOLATED)
        self.assertEquals(char.link_type, LinkType.BOTH)
        self.assertEquals(char.offset, 36)

    def test_is_special_char(self):
        raw = '?@<>%*=&#¨ ^/|\\~`_-«»[]{}'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertTrue(char.is_special_char())

        raw = 'ءآأؤإئابةتثجحخدذرزسشصضطعظغػؼؽؾؿـفكقكلمنهوىي'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertFalse(char.is_special_char())

        raw = 'ًٌٍَُِّْ'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertFalse(char.is_special_char())

    def test_is_alif(self):
        raw = 'آأإا'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertTrue(char.is_alif())

        raw = 'ةتثجحخدذرزسشصضطعظغػؼؽؾؿـفكقكلمنهوىي'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertFalse(char.is_alif())

    def test_is_lam(self):
        raw = 'ل'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertTrue(char.is_lam())

    def test_is_tachkil(self):
        raw = 'ًٌٍَُِّْ'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertTrue(char.is_tachkil())

    def test_is_shadda(self):
        raw = 'ّ'
        txt = raw.decode('utf-8')
        for c in txt:
            char = Character(c)
            self.assertTrue(char.is_shadda())

    def test_can_be_connected(self):
        raw = 'ئبتثجحخسشصضطظعغـفقكلمني'
        txt = raw.decode('utf-8')
        i = 1
        while i < len(txt):
            c = Character(txt[i])
            p = Character(txt[i-1])
            i += 1
            self.assertTrue(c.can_be_connected_to(p))

        raw = 'ءآأؤإاةدذرزوx123#'
        txt = raw.decode('utf-8')
        i = 1
        while i < len(txt):
            c = Character(txt[i])
            p = Character(txt[i-1])
            i += 1
            self.assertFalse(c.can_be_connected_to(p))

    def test_transform_char(self):
        raw = 'ل'
        txt = raw.decode('utf-8')
        char = Character(txt)
        self.assertEquals('ﻝ'.decode('utf-8'), char.transform_char())

        raw = 'ل'
        txt = raw.decode('utf-8')
        char = Character(txt)
        char.shape = LetterShape.ISOLATED
        self.assertEquals('ﻝ'.decode('utf-8'), char.transform_char())

        raw = 'ل'
        txt = raw.decode('utf-8')
        char = Character(txt)
        char.shape = LetterShape.INITIAL
        self.assertEquals('ﻟ'.decode('utf-8'), char.transform_char())

        raw = 'ل'
        txt = raw.decode('utf-8')
        char = Character(txt)
        char.shape = LetterShape.MIDDLE
        self.assertEquals('ﻠ'.decode('utf-8'), char.transform_char())

        raw = 'ل'
        txt = raw.decode('utf-8')
        char = Character(txt)
        char.shape = LetterShape.FINAL
        self.assertEquals('ﻞ'.decode('utf-8'), char.transform_char())

        raw = 'و'
        txt = raw.decode('utf-8')
        char = Character(txt)
        char.shape = LetterShape.FINAL
        self.assertEquals('ﻮ'.decode('utf-8'), char.transform_char())

        raw = 'ء'
        txt = raw.decode('utf-8')
        char = Character(txt)
        char.shape = LetterShape.ISOLATED
        self.assertEquals('ﺀ'.decode('utf-8'), char.transform_char())

        special_chars = '(){}<>[]?'
        special_chars_transformed = ''
        for c in special_chars:
            txt = c.decode('utf-8')
            char = Character(txt)
            special_chars_transformed += char.transform_char()

        self.assertEquals(')(}{><][؟'.decode('utf-8'), special_chars_transformed)

        raw = 'z'
        txt = raw.decode('utf-8')
        char = Character(txt)
        self.assertEquals('z', char.transform_char())

        raw = 'َ'
        txt = raw.decode('utf-8')
        char = Character(txt)
        self.assertEquals('ﹶ'.decode('utf-8'), char.transform_char())

        raw = '@'
        txt = raw.decode('utf-8')
        char = Character(txt)
        self.assertEquals('@', char.transform_char())

    def test_transform_lam_alif_char(self):
        raw = 'ا'
        txt = raw.decode('utf-8')
        char = Character(txt)
        self.assertEquals('ﻻ'.decode('utf-8'), char.transform_lam_alif_char())

    def test_transform_shadda(self):
            raw = 'َ'
            txt = raw.decode('utf-8')
            char = Character(txt)
            self.assertEquals('ﱠ'.decode('utf-8'), char.transform_shadda_char())


class TestText(unittest.TestCase):

    def test_get_word_list(self):
        raw = 'aaa bbb ccc ذهب الولد'
        res = [u'aaa', u' ', u'bbb', u' ', u'ccc', u' ', u'ذهب', u' ', u'الولد']
        txt = Text(raw)
        self.assertEquals(res, txt.get_word_list())

    def test_transform_word(self):
        raw = 'ذهب'
        txt = raw.decode('utf-8')
        self.assertEquals('ﺐﻫﺫ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'لُ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﹸﻝ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'ل'
        txt = raw.decode('utf-8')
        self.assertEquals('ﻝ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'ذَهَبَ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﹶﺐﹷﻫﹶﺫ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'ممَم'
        txt = raw.decode('utf-8')
        self.assertEquals('ﻢﹷﻤﻣ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'aaa'
        txt = raw.decode('utf-8')
        self.assertEquals('aaa'.decode('utf-8'), Text.transform_word(txt))

        raw = 'لأ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﻷ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'لآ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﻵ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'ملآ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﻶﻣ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'ذلإ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﻹﺫ'.decode('utf-8'), Text.transform_word(txt))

        # shadda fatha
        raw = 'َّ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﱠ'.decode('utf-8'), Text.transform_word(txt))

        # fatha shadda
        raw = 'َّ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﱠ'.decode('utf-8'), Text.transform_word(txt))

        # shadda dhamma
        raw = 'ُّ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﱡ'.decode('utf-8'), Text.transform_word(txt))

        # shadda kasra
        raw = 'ِّ'
        txt = raw.decode('utf-8')
        self.assertEquals('ﱢ'.decode('utf-8'), Text.transform_word(txt))

        raw = 'مِّد'
        txt = raw.decode('utf-8')
        self.assertEquals('ﺪﳴﻣ'.decode('utf-8'), Text.transform_word(txt))

        # Lafd al Jalaala
        raw = 'الله'
        txt = raw.decode('utf-8')
        self.assertEquals('ﷲ'.decode('utf-8'), Text.transform_word(txt))

    def test_transform_text(self):
        raw = 'ذهب الولد'
        txt = Text(raw)
        self.assertEquals('ﺪﻟﻮﻟﺍ ﺐﻫﺫ'.decode('utf-8'), txt.transform_text())

    def test_text_to_unicode_string(self):
        raw = 'ذهب الولد'
        txt = Text(raw)
        self.assertEquals('\u0630\u0647\u0628\u0020\u0627\u0644\u0648\u0644\u062f', txt.text_to_unicode_string())


if __name__ == '__main__':
    unittest.main()
