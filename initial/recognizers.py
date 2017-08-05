recognizers = (
    {
        'description': 'Turn en dashes, em dashes, and slashes into separate tokens',
        'recognizer': r'[/—–]', 
        'replacer': '-', 
        'passthrough': True
    },
    {
        'description': 'Remove apostrophes + (and, optionally, s)',
        'recognizer': r'\'s?$', 
        'replacer': '', 
        'passthrough': True
    },
    {
        'description': 'Clean remaining punctuation',
        'recognizer': r'[^\w\s-]', 
        'replacer': '', 
        'passthrough': True
    },
    {
        'description': 'Skip words that end with uis',
        'recognizer': r'(uis)$', 
        'replacer': r'\1', 
        'passthrough': False
    },
    {
        'description': 'replace "ies" with y',
        'recognizer': r'ies$', 
        'replacer': 'y', 
        'passthrough': False
    },
    {
        'description': '"ves" words become f',
        'recognizer': r'ves$', 
        'replacer': 'f', 
        'passthrough': False
    },
    {
        'description': 'detect "es" words that end with e, e.g. castes -> caste',
        'recognizer': r'([cednglstump])es$', 
        'replacer': r'\1e', 
        'passthrough': False
    },
    {
        'description': 'otherwise, "es" words just remove the "es"',
        'recognizer': r'es$', 
        'replacer': '', 
        'passthrough': False
    },
    {
        'description': 'Remove remaining "s" ends',
        'recognizer': r's$', 
        'replacer': '', 
        'passthrough': False
    },
    {
        'description': 'Remove "ing", leaving "e" for appropriate words, e.g. gaming -> game',
        'recognizer': r'([gvsm])ing$', 
        'replacer': r'\1e', 
        'passthrough': False
    },
    {
        'description': 'dding becomes d',
        'recognizer': r'dding$', 
        'replacer': 'd', 
        'passthrough': False
    },
    {
        'description': 'Remove remaining "ing" words',
        'recognizer': r'ing$', 
        'replacer': '', 
        'passthrough': False
    },
    {
        'description': 'Three letter or smaller words should just be returned as is',
        'recognizer': r'^(.?ed)$', 
        'replacer': r'\1', 
        'passthrough': False
    },
    {
        'description': '"pped" should just become p',
        'recognizer': r'pped$', 
        'replacer': 'p', 
        'passthrough': False
    },
    {
        'description': '"rred" should just become r',
        'recognizer': r'rred$', 
        'replacer': 'r', 
        'passthrough': False
    },
    {
        'description': '"ied" should be replaced with y',
        'recognizer': r'ied$', 
        'replacer': 'y', 
        'passthrough': False
    },
    {
        'description': 'some "ed" words should just change to e, e.g. changed -> change',
        'recognizer': r'([cgrszv])ed$', 
        'replacer': r'\1e', 
        'passthrough': False
    },
    {
        'description': 'Otherwise, remove the "ed" from remaining names',
        'recognizer': r'ed$', 
        'replacer': '', 
        'passthrough': False
    },
)
