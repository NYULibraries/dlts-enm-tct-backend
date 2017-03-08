from django.test import TestCase


from otcore.lex.models import StopWord
from otcore.lex.models import Expression, Irregular
from otcore.lex.lex_utils import lex_slugify


# Create your tests here.


class LexModelTests(TestCase):

    def setUp(self):

        StopWord.objects.create(word='of')
        StopWord.objects.create(word='in')

    def test_slug(self):
        """
        Create "New York"
        Check if it creates a basket with label: "new-york_0"
        """
        dy = lex_slugify("Duke of York")
        self.assertEqual(dy, 'duke-york')

    def test_repeat_word(self):
        """
        Slug removes duplicates
        """
        blahblah = lex_slugify('Blah-Blah')
        self.assertEqual(blahblah, 'blah')

    def test_expression(self):
        e = Expression.objects.create(expression='Social Security')
        e_without_spaces = e.expression.replace(' ', '')
        self.assertEqual(e_without_spaces, 'SocialSecurity')
        r = lex_slugify(e_without_spaces)
        self.assertEqual(r, 'socialsecurity')
        self.assertEqual(lex_slugify('Social Security'), 'socialsecurity')

    def test_irregular(self):
        Irregular.objects.create(word='King of Hearts', token='koh')
        x = lex_slugify('King of Hearts')
        self.assertEqual(x, 'koh')

    def test_plural(self):
        x = lex_slugify('Databases')
        self.assertEqual(x, 'database')

    def test_plural2(self):
        x = lex_slugify('Pushing Up Daisies')
        self.assertEqual(x, 'daisy-push-up')

    def test_plural3(self):
        x = lex_slugify('Do Wolves Eat Daisies?')
        self.assertEqual(x, 'daisy-do-eat-wolf')

    """
    NOTE: Michel -- This test is current failing: the actual result of the slugification is
        champ-dans-dernier-ete-l-mais

        Check and see if that's the expected result and, if not, what you'd want to fix
    def test_accents(self):
        Irregular.objects.create(word='dans', token='dans')
        StopWord.objects.create(word='un')
        StopWord.objects.create(word='de')
        x = lex_slugify("L'été dernier dans un champ de maïs")
        self.assertEqual(x, 'champ-dans-dernier-ete-mais')
    """

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
        Irregular.objects.create(word='four', token='4')
        x = lex_slugify('four')
        self.assertEqual(x, '4')

    def test_identical_irregular_and_stop_word2(self):
        # The irregular prevails over the stopword.
        StopWord.objects.create(word='four')
        Irregular.objects.create(word='four', token='4')
        x = lex_slugify('four apples')
        self.assertEqual(x, '4-apple')

    def test_expression_is_stopword(self):
        Expression.objects.create(expression='New York')
        StopWord.objects.create(word='New York')
        self.assertEqual(lex_slugify('New York'), 'newyork')

    def test_expression_is_stopword2(self):
        Expression.objects.create(expression='New York')
        StopWord.objects.create(word='New York')
        self.assertEqual(lex_slugify('New York is in USA'), 'is-newyork-usa')

    def test_stop_word_is_identical_to_expression(self):

        StopWord.objects.all().delete()
        self.assertEqual(StopWord.objects.count(), 0)
        StopWord.objects.create(word='New Jersey')
        Expression.objects.create(expression='New Jersey')
        x = lex_slugify('New Jersey')
        self.assertEqual(x, 'newjersey')

    def test_lex_slugify(self):
        slug1 = lex_slugify('King of Hearts')
        self.assertEqual(slug1, 'heart-k')

        expression_koh = Expression(expression='King of Hearts')
        expression_koh.save()
        slug2 = lex_slugify('King of Hearts')
        self.assertEqual(slug2, 'kingofheart')

        slug3 = lex_slugify('King of Hearts')
        self.assertEqual(slug3, 'kingofheart')
        expression_koh.delete()

    def test_rule_combination(self):

        self.assertEqual(lex_slugify('pinged'), 'pinge')
        self.assertEqual(lex_slugify('beding'), 'bed')
        self.assertEqual(lex_slugify('readied'), 'ready')
        self.assertEqual(lex_slugify('united'), 'unite')
        self.assertEqual(lex_slugify('bed'), 'bed')
        self.assertEqual(lex_slugify('red'), 'red')
        self.assertEqual(lex_slugify('marred'), 'mar')
        self.assertEqual(lex_slugify('parking'), 'park')
        self.assertEqual(lex_slugify('bowling'), 'bowl')
        self.assertEqual(lex_slugify('registering'), 'register')
        self.assertEqual(lex_slugify('registered'), 'register')
        self.assertEqual(lex_slugify('required'), 'require')
        self.assertEqual(lex_slugify('freeing'), 'free')
        self.assertEqual(lex_slugify('rewarding'), 'reward')
        self.assertEqual(lex_slugify('porting'), 'port')
        self.assertEqual(lex_slugify('ported'), 'port')

    def test_dash_replacement(self):
        """
        Test em dash is replaced by hyphen, thus creating two tokens
        """
        self.assertEqual(lex_slugify('Anti—Semitism'), 'anti-semitism')

    def test_slash_replacement(self):
        """
        Test that forward slash (/) is replace by hyphen, thus creating two tokens
        """
        self.assertEqual(lex_slugify('Public/private'), 'private-public')

    def test_apostrophe_replacement(self):
        """
        Test that apostrophes are replaced correctly
        """
        self.assertEqual(lex_slugify("Matt's Art"), 'art-matt')
        self.assertEqual(lex_slugify("States' Rights"), 'right-state')
