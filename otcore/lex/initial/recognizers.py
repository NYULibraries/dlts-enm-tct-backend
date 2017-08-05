recognizers = (
    {
        'description': 'Turn en dashes, em dashes, and slashes into separate tokens',
        'recognizer': r'[/—–]', 
        'replacer': '-', 
        'passthrough': True
    },
    {
        'description': 'Remove apostrophes + (and, optionally, s)',
        'recognizer': r'\'s?', 
        'replacer': '', 
        'passthrough': True
    },
    {
        'description': 'Clean remaining punctuation',
        'recognizer': r'[^\w\s-]', 
        'replacer': '', 
        'passthrough': True
    },
)
