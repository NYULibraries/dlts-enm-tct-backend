from django.test import TestCase

from .processing import read_stopwords, read_recognizers
from .models import StopWord, Recognizer
from .lex_utils import lex_slugify


# Create your tests here.
class LexModelTests(TestCase):
    def setUp(self):
        pass

    def test_slug(self):
        StopWord.objects.create(word='of')
        dy = lex_slugify("Duke of York")
        self.assertEqual(dy, 'duke-york')

    def test_repeat_word(self):
        """
        Slug removes duplicates
        """
        blahblah = lex_slugify('Blah-Blah')
        self.assertEqual(blahblah, 'blah')

    def test_simple_recognizers(self):
        Recognizer.objects.create(recognizer=r's$', replacer='')
        x = lex_slugify('Databases')
        self.assertEqual(x, 'database')

    def test_combined_recognizers(self):
        Recognizer.objects.create(recognizer=r'ies$', replacer='y')
        Recognizer.objects.create(recognizer=r'ing$', replacer='')
        x = lex_slugify('Pushing Up Daisies')
        self.assertEqual(x, 'daisy-push-up')

    def test_rule_following(self):
        Recognizer.objects.create(recognizer=r'[^\w\s-]', replacer='', passthrough=True)
        Recognizer.objects.create(recognizer=r'ves$', replacer='f')
        Recognizer.objects.create(recognizer=r'ies$', replacer='y')
        x = lex_slugify('Do Wolves Eat Daisies?')
        self.assertEqual(x, 'daisy-do-eat-wolf')

    def test_unicode(self):
        x = lex_slugify("漢字 日本語")
        self.assertEqual(x, '日本語-漢字')

    def test_word_is_stop_word(self):
        StopWord.objects.create(word='the')
        x = lex_slugify('the')
        self.assertEqual(x, 'the')

    def test_with_stop_word_in_different_case(self):
        StopWord.objects.create(word='the')
        x = lex_slugify('THE CITY')
        self.assertEqual(x, 'city')

    def test_with_one_letter_word(self):
        self.assertEqual(lex_slugify('s'), 's')

    def test_word_has_one_char_and_is_stop_word(self):
        # The word remains, even though it's a stop word.
        StopWord.objects.create(word='a')
        x = lex_slugify('a')
        self.assertEqual(x, 'a')

    def test_identical_irregular_and_stop_word(self):
        # The irregular prevails over the stopword.
        StopWord.objects.create(word='four')
        Recognizer.objects.create(recognizer='four', replacer='4')
        x = lex_slugify('four')
        self.assertEqual(x, '4')

    def test_identical_irregular_and_stop_word2(self):
        # The irregular prevails over the stopword.
        StopWord.objects.create(word='four')
        Recognizer.objects.create(recognizer='four', replacer='4')
        Recognizer.objects.create(recognizer='s$', replacer='')
        x = lex_slugify('four apples')
        self.assertEqual(x, '4-apple')

    def test_dash_replacement(self):
        """
        Test em dash is replaced by hyphen, thus creating two tokens
        """
        Recognizer.objects.create(recognizer=r'[/—–]', replacer='-')
        self.assertEqual(lex_slugify('Anti—Semitism'), 'anti-semitism')

    def test_slash_replacement(self):
        """
        Test that forward slash (/) is replace by hyphen, thus creating two tokens
        """
        Recognizer.objects.create(recognizer=r'[/—–]', replacer='-')
        self.assertEqual(lex_slugify('Public/private'), 'private-public')

    def test_apostrophe_replacement(self):
        """
        Test that apostrophes are replaced correctly
        """
        Recognizer.objects.create(recognizer=r'\'s?', replacer='', passthrough=True)
        Recognizer.objects.create(recognizer=r's$', replacer='')
        self.assertEqual(lex_slugify("Matt's Art"), 'art-matt')
        self.assertEqual(lex_slugify("States' Rights"), 'right-state')
