## Sources API Overview

Description                         | Endpoint                                                    | Extra Parameters
----------------------------------  | ---------------------------------------------------------   | ----------------
List of All EPUBs                   | [/api/epub/document/all/](#all-epubs)                       |
EPUB Detail                         | [/api/epub/document/DOCUMENT_ID/](#epub-detail)             | withOccurrences
Single Page                         | [/api/epub/location/LOCATION_ID/](#single-page)             |
List of All Indexpatterns           | [/api/epub/index-pattern/all/](#all-indexpatterns)          |

---

## All EPUBs

Lists all EPUBs in the system.  Note that this includes any EPUB in the system that has no index (and therefore no topics) or no page marker indicators in the original text (and therefore no pages in our system).

```
/api/epub/document/all/
```

### Example Response

```json
[
    {
        "title": "Black Rage Confronts the Law",
        "author": "Paul Harris",
        "publisher": "New York University",
        "id": 95,
        "isbn": "9780814735923"
    },
    {
        "title": "Negrophobia and Reasonable Racism",
        "author": "Jody David Armour",
        "publisher": "New york University Press",
        "id": 67,
        "isbn": "9780814706404"
    },
    ...
    {
        "title": "Teaching What You’re Not",
        "author": "Katherine J. Mayberry",
        "publisher": "York University Press",
        "id": 88,
        "isbn": "9780814755471"
    }
]
```

### Field Descriptions

Field          | Type    | Description
-------------  | ------- | -----------
id             | Integer | Internal id and primary identifier for each EPUB 
title          | String  | Title of the EPUB
author         | String  | Author of the EPUB
publisher      | String  | Publisher of the EPUB. See our [note](overview) about ISBN numbers on the Overview page
isbn           | String  | ISBN number for the book. Note that this is extracted from the EPUB filename, not extracted from any metadata from the book itself. Be aware of this limitation in future ingests

---

## EPUB Detail

Lists all Pages in a given EPUB.

```
/api/epub/document/DOCUMENT_ID/
```

For expanded location information, you can set the query parameter `withOccurrences` to `True`:

```
/api/epub/document/DOCUMENT_ID/?withOccurrences=True
```

That will give expanded location information, including occurrences and page numbers. The location data for this response is identical to that from the [Location Detail](#single-page), just as an array of every page for that particular book. Refer to the [single page](#single-page) endpoint for a description of the response structure and fields.  

### Example Response

```json
{
    "title": "Originality, Imitation, and Plagiarism",
    "author": "Eisner, Caroline; Vicinus, Martha",
    "id": 12,
    "publisher": "University of Michigan Press and University of Michigan Library",
    "isbn": "9780472024445",
    "locations": [
        {
            "id": 2220,
            "localid": "page_i",
            "sequence_number": 1,
            "content": ""
        },
        {
            "id": 2221,
            "localid": "page_ii",
            "sequence_number": 2,
            "content": ""
        },
        ...
        {
            "id": 2495,
            "localid": "page_268",
            "sequence_number": 276,
            "content": "\nSony Corp of America v. Universal Studios, Inc., 149, 150, 154\nSouter, David H., 150\nSponsoring Con..."
        },
        {
            "id": 2496,
            "localid": "page_269",
            "sequence_number": 277,
            "content": "\nWikiWikiWeb, 45n1\nWimmer, Warren, 66, 67\nWinter, Richard, 183\nWollheim, Richard, 117\nWoodmansee, Ma..."
        }
    ]
}
```

### Field Descriptions

Field                           | Type    | Description
------------------------------- | ------- | -----------
id                              | Integer | Internal id and primary identifier for each EPUB 
title                           | String  | Title of the EPUB
author                          | String  | Author of the EPUB 
epub                            | String  | Publisher of the EPUB. See [All EPUBs](#all-epubs) for note about consistency.
isbn                            | String  | ISBN number for the book. See [the API Overview](overview) for note about sourcing
locations[...].id               | Integer | Internal id and primary identifier for each page. [Usual caveats](overview) regarding IDs apply
locations[...].localid          | String  | Human-readable representation of the page number
locations[...].sequence_number  | Integer | Number used for properly ordering pages in a book 
locations[...].content          | String  | Excerpt of the content from the page (roughly the first 100 characters) 

---

## Single Page

Contents information on a single page, including the pages full textual content and all occurrences at that particular page.

```
/api/epub/location/LOCATION_ID/
```

### Example Response

```json
[
    {
        "id": 2410,
        "content": {
            "content_unique_indicator": "12-page_183",
            "content_descriptor": "page 183",
            "text": "Plagiarism, a Turnitin Trial, and an Experience of Cultural Disorientation\nLisa Emerson\nIn October 2003, all faculty at Massey University, a research university in New Zealand, were invited to join a university-wide trial of Turnitin.com, a plagiarism detection system being considered for widespread use to combat a perceived “plagiarism epidemic.” The university framed the Turnitin trial as an investigation into issues of academic integrity and a step in strengthening academic misconduct procedures, with no reference to plagiarism as an issue of academic writing. This is not, perhaps, surprising since rhetoric and composition is an emerging discipline in New Zealand and is not yet fully established as part of the curriculum. As the only full-time faculty member employed at this time to teach academic writing at the university, I joined the trial, hoping to bring a different perspective on the issue.\nThe purpose of this essay is to consider the value of Turnitin primarily from the context of reflecting, as a writing teacher, on what the trial taught me about writing, about my role as a writing teacher, about students and learning, and on the gaps that exist in our understanding of and relationship with one another in the student-teacher relationship. To deepen my reflection, I have used a form of reflective practice established by Donald Schön and developed by the British school of action research (see, for example, Whitehead and McNiff). This reflective paradigm, as described by Richard Winter, Alyson Buck, and Paula Sobiechowska, “requires more than observation. It requires us to engage in a process of introspection leading to self-clarification” (186). This essay summarizes the process of observation and self-clarification I engaged in as part of the university trial.\n"
        },
        "document": {
            "title": "Originality, Imitation, and Plagiarism",
            "author": "Eisner, Caroline; Vicinus, Martha",
            "publisher": "University of Michigan Press and University of Michigan Library",
            "id": 12,
            "isbn": "9780472024445"
        },
        "context": null,
        "occurrences": [
            {
                "basket": {
                    "id": 2559,
                    "display_name": "Buck, Alyson"
                },
                "id": 8591,
                "ring_next": null,
                "ring_prev": null
            },
            {
                "basket": {
                    "id": 2859,
                    "display_name": "Massey University"
                },
                "id": 9409,
                "ring_next": 2419,
                "ring_prev": 2419
            },
            ...
            {
                "basket": {
                    "id": 3118,
                    "display_name": "Winter, Richard"
                },
                "id": 10083,
                "ring_next": null,
                "ring_prev": null
            }
        ],
        "pagenumber": {
            "filepath": "OEBPS/24_chap16.xhtml",
            "pagenumber_tag": "<a id=\"page_183\">",
            "css_selector": "#page_183",
            "xpath": "a[@id=\"page_183\"]"
        },
        "localid": "page_183",
        "next_location_id": 2411,
        "previous_location_id": 2409
    }
]
```

### Field Descriptions

Field                                 | Type    | Description
------------------------------------- | ------- | -----------
id                                    | Integer | Internal id and primary identifier of this page
content.content_unique_indicator      | String  | Human readable identifier of this content block. Usually a combination of the EPUB's internal ID and the Page's 'localid'.  Used internally for deduplication.
content.content_descriptor            | String  | Human readable description of the content's location
content.text                          | String  | Full text of the page
document.id                           | Integer | Internal id and primary identifier for each EPUB
document.title                        | String  | Title of the EPUB
document.author                       | String  | Author of the EPUB
document.epub                         | String  | Publisher of the EPUB. See [All EPUBs](#all-epubs) for note about consistency.
document.isbn                         | String  | ISBN number for the book. See [the API Overview](overview) for note about sourcing
context                               | String  | Not used in Enhanced Network Monographs
occurrences                           | List    | All the topics on this page
occurrences[...].id                   | Integer | Internal id for this occurrence
occurrences[...].basket.id            | Integer | Internal id for this topic
occurrences[...].basket.display_name  | Integer | display_name for given topic. See [All Topics](topics/#all-topics) for more information
occurrences[...].ring_next            | Integer | Location ID (i.e. internal id of the page) of the next occurrence of this topic.  If `null`, then this is the only instance of this topic
occurrences[...].ring_previous        | Integer | Location ID (i.e. internal id of the page) of the previous occurrence of this topic.  If `null`, then this is the only instance of this topic
pagenumber.filepath                   | String  | Location of the specific xml file in which this location is found, relative to the root folder of the unzipped EPUB
pagenumber.pagenumber_tag             | String  | Reconstructed page number identifier tag as it appears in the EPUB 
pagenumber.css_selector               | String  | CSS Selector for finding the location within the original xml file
pagenumber.xpath                      | String  | xpath for finding the location within the original xml file
localid                               | String  | Human-readable representation of the page number
next_location_id                      | Integer | Id of the next location (page) in this EPUB
previous_location_id                  | Integer | Id of the previous location (page) in this EPUB

---

## All IndexPatterns

A list of all IndexPattern objects. Indexpatterns are primarily used for extraction, but are also used for conforming the `localid` attribute (which is essentially just a stored page number) to the css selectors/xpath/tag necessary for finding the location in the original EPUB file.

```
/api/epub/index-pattern/all/
```

## Example Response

```json
[
    {
        "id": 5,
        "name": "nyup1",
        "description": "NYUP as of Spring 2015",
        "pagenumber_pre_strings": [
            "id=\"page_"
        ],
        "pagenumber_css_selector_pattern": "#page_{}",
        "pagenumber_xpath_pattern": "a[@id=\"page_{}\"]",
        "xpath_entry": "p[@class='indexmain' or @class='indexmain1']",
        "see_split_strings": [
            ". See",
            ", See",
            ", see",
            "(see"
        ],
        "see_also_split_strings": [
            ", See also",
            ". See also",
            "See also",
            " see also",
            ", also",
            "(see also"
        ],
        "xpath_see": "em",
        "xpath_seealso": "em",
        "separator_between_sees": ";",
        "separator_between_seealsos": ";",
        "separator_see_subentry": ",",
        "inline_see_start": "",
        "inline_see_also_start": "",
        "inline_see_end": "",
        "inline_see_also_end": "",
        "subentry_classes": [
            "indexsub"
        ],
        "separator_between_subentries": "",
        "separator_between_entry_and_occurrences": ",",
        "separator_before_first_subentry": ":",
        "xpath_occurrence_link": "a[@href]",
        "indicators_of_occurrence_range": [
            "–",
            "—"
        ],
        "documents": [
            {
                "title": "Busting the Mob",
                "id": 464
            },
            {
                "title": "The Transformation of Rage",
                "id": 465
            },
            ...
            {
                "title": "Bird-Self Accumulated",
                "id": 463
            }
        ]
    },
    ...
]
```

### Field Descriptions

Field                                   | Type           | Description
--------------------------------------- | -------------- | -----------
id                                      | Integer        | Internal id and primary identifier of this indexpattern
name                                    | String         | Unique string representation of indexpattern. Primary means of fetching a pattern from the database
description                             | String         | Longer, human-readable text description of the IndexPattern. __Note:__ Descriptions are _not_ guaranteed to be unique by the database, and are merely meant to contain supplemental information.
pagenumber_pre_strings                  | Array (String) | When locating page numbers, this is a list of patterns to look for and split the text on. After this processing is done, the result should be a list of strings with the page number at the beginning of the string, followed by the content of the page. Used for extracting both locations and content from an EPUB
pagenumber_css_selector_pattern         | String         | Pattern used to conform a page number (as stored in localid) to a css selector. All patterns must contain "{}" where the page number should go, as python string formatting is used to add the page number from any given location
pagenumber_xpath_pattern                | String         | Pattern used to conform a page number (as stored in localid) to an xpath. All patterns must contain "{}" where the page number should go, as python string formatting is used to add the page number from any given location
xpath_entry                             | String         | xpath used to locate main entries in the index
see_split_strings                       | Array (String) | When parsing an entry, split on these strings to separate a "See" from the main entry (Sees are not always reliably enclosed in tags, and therefore require string processing)
see_also_split_strings                  | Array (String) | Same as above, but with See Also
xpath_see                               | String         | Tag generally (but not always) used to enclose a "See". Used for locating "see" objects in inline subentry index entries.
xpath_see_also                          | String         | Same as above, but with See Also
separator_between_sees                  | String         | When an entry has multiple See references, this is the character used to separate them.  For example, in the entry _Clinton, William. See Clinton, Hillary; Presidency_, the semicolon would be the separator between multiple Sees
separator_between_seealsos              | String         | Same as above, but with See Also
separator_see_subentry                  | String         | When a see/see also points to a subentry instead of a main topic, this separator is used.  For example, in the entry _The Raven. See Poe, works by_, the comma might indicate that 'works by' is a subentry of 'Poe', and that this see is pointing to that particular subentry, rather than the main entry 'Poe'
inline_see_start                        | String         | In inline subentries, multiple Sees are usually enclosed in wrapping punctuation, to demarcate the difference between multiple sees on one subentry and different subentries. For example, take this monster of an entry: _humanism, 8, 9, 18, 24, 89, 94, 101, 102, 172, 180n7, 250n29; humanist resistance to Adams’s works, 68, 77; humanist self (see also self; subjectivity; subject–object relation), 7, 20, 101, 110, 164, 169. See also anthropocentrism; human rights_. In this case, the separator between subentries and multiple see also relationships are __exactly the same__ (a semicolon). However, the parenthesis allow us to tell when the list of see/see also relations ends, so we can distinguish them from separate subentries
inline_see_also_start                   | String         | Same as above, but wtih See Also
inline_see_end                          | String         | Separator ending a list of See items in an inline subentry.  See `inline_see_start` for a fuller explanation
subentry_classes                        | Array (String) | CSS Classes used to locate subentries.  __Note__: This is __only__ used for separate line subentry indexes. An empty value for this property means that the index in questions uses only inline, rather than separate line, subentries
separator_between_subentries            | String         | For inline subentries, the separator used to distinguish different subentries.  For example, in the entry example used in `inline_see_start`, the semicolon is used to separate different subentries.  __Note__: This is __only__ used for inline subentry indexes. An empty value for this property means that this index only has separate line subentries
separator_between_entry_and_occurrences | String         | Separator between an entry and its occurrences/page numbers
separator_before_first_subentry         | String         | Indexes sometimes collapse an entry and the first subentry into a single line.  For example, the entry _Clinton, William: presidency of_ is actually a main entry (_Clinton, William_) and the first subentry (_presidency of_).  In this case, the `separator_before_first_subentry` would be the colon (:)
xpath_occurrence_link                   | String         | xpath to find occurrences in an entry
indicators_of_occurrence_range          | Array (String) | Character(s) used to indicate a range of pages in an index, e.g. 145-54. Needs to be an array because indexes are inconsistent in their use of punctation (sometimes using a mixture of hyphens, em dashes, and en dahses)
documents                               | Array          | List of EPUBs associated with that particular indexpattern
documents[...].id                       | Integer        | Internal id and primary identifier for each EPUB
documents[...].title                    | String         | Title of the EPUB
