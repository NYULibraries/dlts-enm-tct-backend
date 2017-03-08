from otcore.lex.models import StopWord, Expression, Irregular
from otcore.settings import setting
import codecs


def lines_in_file(filename):

    """
    returns a list, each item is a line in a file.
    """

    file_fo = codecs.open(filename, 'r', 'utf-8')
    lines = file_fo.readlines()
    file_fo.close()

    return lines


def read_stopwords():

    """
    Reads the initial stop word list.
    """
    print('INFO Read Stopwords.')

    stopword_file = setting('INITIAL_FILE_STOPWORDS')
    stopwords = lines_in_file(stopword_file)

    for stop in stopwords:
        if stop.strip():
            StopWord.objects.get_or_create(word=stop.strip())


def read_expressions():
    """
    read the expression list in config/expressions.txt
    """
    print('INFO Read Expressions.')
    expressions_file = setting('INITIAL_FILE_EXPRESSIONS')
    expressions = lines_in_file(expressions_file)

    for expression in expressions:
        Expression.objects.get_or_create(expression=expression.strip())


def read_irregulars():

    """
    Read the word/token list in config/words.txt
    """
    print('INFO Read Irregulars.')
    wordtokens = setting('INITIAL_FILE_IRREGULARS')

    fileFO = open(wordtokens, 'r')
    wordtokenlines = fileFO.readlines()
    fileFO.close()

    for wordtoken in wordtokenlines:
        if not wordtoken.startswith('#'):
            try:
                word, token = wordtoken.split('|')
                Irregular.objects.update_or_create(
                    word=word.strip(),
                    token=token.strip(),
                )
            except ValueError:
                continue
                # print('ERROR while reading irregulars. ValueError for wordtoken={}'.format(wordtoken))


def iterative_bfs(graph, start, path=[]):

    """
    Breadth First Graph Traversal.
    From: http://code.activestate.com/recipes/576723-dfs-and-bfs-graph-traversal/
    Author is probably Bruce Wernick.
    """

    q = [start]
    while q:
        v = q.pop(0)
        if v not in path:
            path = path + [v]
            q = q + graph[v]
    return path
