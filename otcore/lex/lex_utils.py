# -- coding: utf-8 --
from __future__ import unicode_literals

from django.conf import settings
from django.utils.text import slugify

from otcore.lex.models import StopWord, Expression, Irregular
from otcore.settings import setting


def lex_slugify(value):
    """
    This is a modified version of the slugify script provided by Django.
    Converts to ASCII. Converts spaces to hyphens. Removes characters that
    aren't alphanumerics, underscores, or hyphens. Converts to lowercase.
    Also strips leading and trailing whitespace.

    If there are words that need to stay together (aka 'expressions'), do that.

    Incoming value ends with a semi-column and a number indicating the scope.
    This part should be removed while processing for words, irregulars,
    and expressions. Each token will have a number added to make it distinct
    from the same name in another scope.

    """
    # Eliminate hyphens and make it a full word.

    # This works recursively when several expressions are included
    # in a given string. Use set operations.

    # First, look if the name to be slugified is irregular. If
    # yes, it has an exact translation as token. All the rest of
    # of the processing is ignored.

    irregular_words = [irregular.word for irregular in Irregular.objects.all()]

    if value in irregular_words:
        return Irregular.objects.get(word=value).slug

    # Get rid of apostrophe. Replace it with space.
    value = value.replace("'s", "").replace("'", "")

    # If the SPLIT_ON_PUNCTATUON is true, replace slashes, em dashes, and en dashes with hyphens
    if setting('SPLIT_ON_PUNCTUATION'):
        value = value.replace('/', '-').replace('—', '-').replace('–', '-')

    # Load the list of stop words.

    stopwords = set([slugify(stopword_object.word, allow_unicode=True) for stopword_object in StopWord.objects.all()])

    # Reload the irregular list, because any word can have a translation.
    # Load the irregular dictionary mapping an irregular word to a token.

    irregular = {}
    for word in Irregular.objects.all():
        irregular[slugify(word.word, allow_unicode=True)] = slugify(word.token, allow_unicode=True)

    expression_list = [slugify(e.expression, allow_unicode=True) for e in Expression.objects.all()]

    # If unicode characters don't convert into Ascii, string becomes null.
    # If it's null, skip slugify.
    saved_value = value
    value = slugify(value, allow_unicode=True)
    if value == '':
        value = "{}".format(saved_value.encode('utf-8'))

    # If the name is exactly the same as one of the expression.
    # Checking if the value has the same slug as one of the expressions.
    if value in expression_list:
        slugified = slugify(value, allow_unicode=True)
        value = value.replace(slugified, ''.join(slugified.split('-')))
    else:
        # Look at all expressions. Slugify them.
        for expression in Expression.objects.all():

            slugified = slugify(expression.expression, allow_unicode=True)
            # Look if the value is contained in one of the expressions.
            if slugified in value:
                value = value.replace(slugified, ''.join(slugified.split('-')))

    slug_result = slugify(value, allow_unicode=True)

    # Now split again the result into a list of words

    words = set(slug_result.split('-'))

    # Look if some of these words are irregular.

    irregulars_detected = words.intersection(set(irregular.keys()))

    # Remove the stop words.
    # Eliminate the duplicated words.
    # For the others, apply the automatic rules.

    slug_set = set()
    for word in list(words):
        if word in list(irregulars_detected):
            slug_set.add(irregular[word])
        elif setting('ENGLISH_GRAMMAR'):
            slug_set.add(english_grammar_transform(word))
        else:
            slug_set.add(word)

    # Specific case where all what remains is a stop word that
    # would be removed and ended as an empty slug. In that case
    # the slug will be the stop word.

    if slug_set == {''}:
        slug_set = set(slug_result)

    # Now remove the stopwords.
    # Stopwords will not be removed if the name of a topic is
    # a stopword.

    # Check if value is a stopword. In that case, keep it.
    # print('slug_result=%s stopwords=%s' % (slug_result, stopwords))

    if slug_result in stopwords:
        slug_list = list(slug_set)
    else:
        minus_stopwords = slug_set.difference(stopwords)
        # If there is nothing left after stopwords are removed, ignore the stopwords altogether.
        if len(minus_stopwords):
            slug_list = list(minus_stopwords)
        else:
            slug_list = list(slug_set)

    slug_value = '-'.join(sorted(slug_list))
    return slug_value.strip('-')


def english_grammar_transform(word):

    # This is a new version which will do all necessary transformation instead of returning
    # the transformed word immediately.
    """
    Supplementary automatic rules to transform words into tokens. This script essentially handles the
    cases of plural forms, and words ending with "ing" and "ed".

    This only works with English.

    - 's' rules:
       - words ending with s which are not transformable by removing the 's': 'status', 'basis', 'business', 'irs', 'corps', etc.)
       - words ending with ...ves that correspond to ...f in singular ('halves' -> 'half', 'calves' -> 'calf', 'wolves' -> 'wolf')
       - words ending with ...ies that correspond to ...y in singular ('parties' -> 'party', etc.)
       - words ending with es that are invariant: 'Philippines'
       - words ending with es that end with e in singular form: 'codes', 'fees', 'sales', 'inheritances', 'lines', etc.
       - words ending with es that don't end with e in singular. 'es' is just taken out.
       - all others become singular by removing the s.
       - children becomes child
    -'ing' Rules
       - words ending with ..ing have a root without the ..ing
       - except some of them which are irregulars: e.g. 'parking' (different from park)
       - except words ending with ..ing that become ..e: 'filing' -> file, 'figuring' -> figure
       - except words that have another letter removed: 'getting' becomes 'get' (not gett)
    - 'ed' rules
       - some words should stay as such: 'united' (not the same as 'unit')
       - ...rred or ..pped become ..r or ..p
       - some words replace 'ed' with 'e': 'used' becomes 'use', 'separated' becomes 'separate', etc.
       - words ending with 'ied' becomes 'y': e.g. 'married' becomes 'marry'
       - all other ...ed become ... (trailing 'ed' is removed)
    - 'tion' rules
       - to be done: 'organization' -> 'organize', 'contribution'-> 'contribute', etc.
    - Synonyms.
       - built-in, always synonyms. Ex: 'type' = 'category'

    - Add: '-able': e.g, 'Accountable' -> 'Account'


    """
    # Removed because it created unwanted merge between "Anderson, B", and "Anderson, C"
    # if len(word) == 1:
    #     # If word is only one letter, remove it.
    #     return ''
    if word.endswith('s'):
        if word.endswith("'s"):
            word = word[:-2]
        if len(word) < 4:
            return word   # Don't touch the word if it's too small
        elif word[-2] in 'uis':
            return word
        elif word.endswith('ves'):
            word = '%sf' % word[:-3]
        elif word.endswith('ies'):
            word = '%sy' % word[:-3]
        elif word.endswith('oes'):
            word = word[:-2]
        elif word.endswith('es'):
            if word[-3] in 'cednglstump':
                word = word[:-1]
            else:  # This is for nouns that end with ch, x, s, or z:
                word = word[:-2]
        else:
            word = word[:-1]
    elif word.endswith('ing'):
        # (Examples: figuring -> figure, living-> live, hedging-> hedge)
        try:
            if word[-4] in 'gvstm':
                if word in ['porting']:
                    word = word[:-3]
                else:
                    word = '%se' % word[:-3]
            else:
                word = word[:-3]
        except IndexError:
            # Case of error detected for word = "digital-DJ-ing: contemporary youth"
            # in UMP1/Mahiri_Digital_9780472027606/index.html
            print ('IndexError for word %s ending with "ing":' % word)

    elif word.endswith('ed'):
        if len(word) <= 3:
            return word
            # Found 'ed'
        elif word.endswith('rred') or word.endswith('pped'):
            word = word[:-3]
        elif word[-3] in 'cgrtszv':  # united, contributed, changed, divorced, required, received (if required makes require, registered would make 'registere')
            if word in ['registered', 'ported']:
                word = word[:-2]
            else:
                word = word[:-1]
        elif word.endswith('ied'):
            word = '%sy' % word[:-3]
        else:
            word = word[:-2]
    else:
        pass

    return word
