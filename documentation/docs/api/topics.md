## API Overview

Description                         | Endpoint                                                    | Extra Parameters
----------------------------------  | ---------------------------------------------------------   | ----------------
List of All Topics                  | [/api/hit/basket/all/](#all-topics)                         |
List of Subset of Topics            | [/api/hit/basket/search/](#topic-subset)                    | letter, document
Topic Detail                        | [/api/hit/basket/BASKET_ID/](#topic-detail)                 | 
All Topics (with review data)       | [/api/review/baskets/all](#topics-with-review)              | 
Subset of Topics (with review data) | [/api/review/baskets/search](#reviewed-topics-subset)       | letter, document
List of All Names                   | [/api/hit/hits/all/](#all-names)                            | 
List of Subset of Names             | [/api/hit/hits/search/](#names-subset)                      | name, letter, scope, ttype
List of All Scopes                  | [/api/hit/scope/all/](#all-scopes)                          | 
List of All Topic Types             | [/api/topic/ttype/all/](#all-topic-types)                   | 

!!! note "A Note on Terminology"
    You may notice the terms __basket__ and __hit__ a lot on this page.  Internally, this is how our topic mapping software refers to __topics__ and __names__, respectively.  In almost all cases, mentally replacing __basket__ with __topic__ and __hit__ with __name__ will work perfectly.

---

## All Topics

Gives a list of all topics in the system:

```
/api/hit/basket/all/
```

### Example response

```json
[
    {
        "id": 3037,
        "display_name": "17 U.S.C. §120(a)"
    },
    {
        "id": 30823,
        "display_name": "1950s"
    },
    ...
    {
        "id": 22291,
        "display_name": "Zwerdling, Alex"
    },
    {
        "id": 25992,
        "display_name": "Zwingli, Huldreich"
    }
]
```

### Field Descriptions

Field         | Type    | Description
------------- | ------- | -----------
id            | Integer | Internal id and primary identifier for each topic
display_name  | String  | Primary name for the topic. Can be changed by hiding, deleting, editing, or preferring names on the topic in question.

---

## Topic Subset

This endpoints allows you to get lists of topics by either starting letter or document. For example:

```
/api/hit/basket/search/?letter=B
```

Will give all topics whose `display_name` starts with the letter 'B'.  In order to get all topics that start with a number or symbol, us the '#' sign:

```
/api/hit/basket/search/?letter=#
```

To get a list of topics in a given document, use:

```
/api/hit/basket/search/?document=DOCUMENT_ID
```

to get the id of a given document, use the [sources API](sources.md) or the editorial interface.  The structure/fields of the response are the same as the [All Topics](#all-topics) endpoint.

---

## Topic Detail

Gives all data for a single topic, including all names, occurrences, and relations:

```
/api/hit/basket/BASKET_ID
```

### Example response

```json
{
    "relations": [
        {
            "id": 32255,
            "relationtype": {
                "id": 6,
                "rtype": "Containment",
                "role_from": "contained by",
                "role_to": "contains",
                "symmetrical": false
            },
            "basket": {
                "display_name": "games",
                "id": 90
            },
            "direction": "source"
        },
        {
            "id": 122665,
            "relationtype": {
                "id": 4,
                "rtype": "Subentry",
                "role_from": "Main Entry of",
                "role_to": "Subentry of",
                "symmetrical": false
            },
            "basket": {
                "display_name": "video games -- in science education",
                "id": 209
            },
            "direction": "destination"
        }
    ],
    "basket": {
        "id": 7399,
        "topic_hits": [
            {
                "id": 10210,
                "name": "Video game",
                "scope": {
                    "id": 2,
                    "scope": "Generic"
                },
                "bypass": false,
                "hidden": false,
                "preferred": false
            },
            {
                "id": 8758,
                "name": "video -- \"games\"",
                "scope": {
                    "id": 2,
                    "scope": "Generic"
                },
                "bypass": false,
                "hidden": false,
                "preferred": false
            }
        ],
        "occurs": [
            {
                "id": 28663,
                "location": {
                    "id": 6418,
                    "document": {
                        "title": "Making News at The New York Times",
                        "author": "Usher, Nikki"
                    },
                    "localid": "page_150"
                }
            },
            {
                "id": 31986,
                "location": {
                    "id": 6907,
                    "document": {
                        "title": "The Hyperlinked Society: Questioning Connections in the Digital Age",
                        "author": "Turrow, Joseph; Tsui, Lokman"
                    },
                    "localid": "page_132"
                }
            }
        ],
        "weblinks": [
            {
                "id": 56,
                "content": "Library of Congress (exactMatch)",
                "url": "http://id.loc.gov/authorities/names/someFakeId"
            },
            {
                "id": 112,
                "content": "Wikidata (exactMatch)",
                "url": "https://www.wikidata.org/entity/someFakeId"
            },
        ],
        "types": [
            {
                "ttype": "skos:Concept",
                "id": 6
            },
            {
                "ttype": "schema:CreativeWork",
                "id": 1
            }
        ]
        "display_name": "video -- \"games\""
    }
}
```

### Field Descriptions

Field                                       |  Type   | Description
------------------------------------------- | ------- | -----------
basket.id                                   | Integer | Same as the `id` in the [All Topics](#all-topics) API enpoint
basket.display_name                         | String  | Same as the `display_name` in the [All Topics](#all-topics) API endpoint
basket.topic_hits                           | List    | List of names on the topic
basket.topic_hits[...].id                   | Integer | Internal id of that particular name. Like the Topic ID, it's stable within a database, but not guaranteed to be consistent across databases or re-ingests
basket.topic_hits[...].name                 | String  | Name string of a single topic name
basket.topic_hits[...].scope.id             | Integer | Internal ID of the scope
basket.topic_hits[...].scope.scope          | String  | String/text representation of the scope of that name.  Default scope is "Generic"
basket.topic_hits[...].bypass               | Boolean | If set to True, this prevents a name from being reprocessed when re-ingesting material. Used for certain kinds of automatic processing, but it's not used in the current iteration of _Enhanced Network Monographs_
basket.topic_hits[...].hidden               | Boolean | If set to True, this name is saved on a topic but is not displayed in output.  Not currrently used in this iteration of _Enhanced Network Monographs_
basket.topic_hits[...].preferred            | Boolean | Indicates whether this hit should be used for the current topics `display_name`. If not name as `preferred=True`, then the longest name will be used as the `display_name` for that topic
basket.occurs                               | List    | List of all occurrences of a given topic
basket.occurs[...].id                       | Integer | Internal ID of the occurrence
basket.occurs[...].location                 | Dict    | Information on the original location (in this case, the particular book/page) of the occurrence
basket.occurs[...].location.id              | Integer | Internal ID of that page
basket.occurs[...].location.document.title  | String  | Title of the original source that this occurrence is in
basket.occurs[...].location.document.author | String  | Author of the original source that this occurrence is in
basket.occurs[...].location.localid         | String  | Identifier for this particular location (relative to the document).  This __is__ guaranteed to be stable across ingests
basket.weblinks[...].id                     | Integer | Internal ID of the weblink
basket.weblinks[...].content                | String  | Human-readable description of the weblink. Is often, but is not required to be, the title of the linked webpage
basket.weblinks[...].url                    | String  | Full URL of the weblink. Must start with http or https
basket.types[...].id                        | Integer | Internal ID of the Topic Type
basket.types[...].ttype                     | String  | Human-readable name of the Topic Type
relations                                   | List    | List/Description of all related topics
relations[...].ids                          | Integer | Internal ID of this particular relation
relations[...].basket.id                    | Integer | ID of the related topic
relations[...].basket.display_name          | String  | `display_name` of the related topic
relations[...].relationtype.rtype           | String  | Description of the _kind_ of relation between this topic and the related topic
relations[...].relationtype.id              | Integer | Internal ID of this particular RelationType
relations[...].relationtype.role_from       | String  | Description of the role from the source topic to the destination topic. E.g. for a "parent" relationship this might be "parent of"
relations[...].relationtype.role_to         | String  | Description of the from the destination topic to the source topic.  E.g. for a "parent" relationship this might be "child of"
relations[...].relationtype.symmetrical     | Boolean | Indicates whether or not this RelationType is symmetrical.  Another way of saying that "role_to" and "role_form" (described above) are equivalent.
relations[...].direction                    | String  | Describes whether the current topic is the "source" (e.g. uses the "role_to" description above) or the "destination" (e.g. uses the "role_from" description above) of the given relationship. Important for noting the directionality of non-symmetrical relationships

--- 
## Topics With Review

Similar to the [All Topics](#all-topics) API Endpoint, except that it also includes information on whether or not the topic has been reviewed (and by whom):

```
/api/review/basket/all/
```

### Example Response

```json
[
    {
        "id": 3037,
        "display_name": "17 U.S.C. §120(a)",
        "review": {
            "reviewer": null,
            "time": null,
            "reviewed": false,
            "changed": false
        }
    },
    {
        "id": 30823,
        "display_name": "1950s",
        "review": {
            "reviewer": null,
            "time": null,
            "reviewed": false,
            "changed": false
        }
    },
    ...
   {
        "id": 25992,
        "display_name": "Zwingli, Huldreich",
        "review": {
            "reviewer": "Alex",
            "time": "2017-01-05T21:16:03.377185Z",
            "reviewed": true,
            "changed": false
        }
    }
]
```

### Field Descriptions

Field            | Type    | Description
---------------- | ------- | -----------
id               | Integer | Internal id and primary identifier for each topic
display_name     | String  | Primary name for the topic. Can be changed by hiding, deleting, editing, or preferring names on the topic in question.
review.reviewer  | String  | Username of person who last changed the review status of topic
review.time      | String  | Date/Time of last change of review status, in UTC format
review.reviewed  | Boolean | Whether or not the topic was reviewed
review.changed   | Boolean | Whether the topic was changed (if reviewed)

---

### Reviewed Topic Subset

Provides the same subsets of topics as the [regular Topic Subset](#topic-subset) list, except also includes review information. Query string parameters work exactly the same way -- for example, requesting all topics that start with letter 'D' (along with their review status) would be:

```
/api/review/basket/search/?letter=D
```

Field data is exactly the same as the [All Topics with Reviewed Data](#topics-with-review) API endpoint

---

## All Names

Returns a list of all names in the database:

```
/api/hit/hits/all/
```

### Example Response

```json
[
    {
        "name": "10 Percent",
        "basket": 38574,
        "scope": "Generic",
        "preferred": false,
        "hidden": false,
        "id": 40302
    },
    {
        "name": "17 U.S.C. §120(a)",
        "basket": 3037,
        "scope": "Generic",
        "preferred": false,
        "hidden": false,
        "id": 3109
    },
    ...
    {
        "name": "Zwingli, Huldreich",
        "basket": 25992,
        "scope": "Generic",
        "preferred": false,
        "hidden": false,
        "id": 26982
    }
]
```

### Field Descriptions

Field            | Type    | Description
---------------- | ------- | -----------
name             | String  | full, human-readable name
basket           | Integer | ID of the topic that this name is attached to
scope            | String  | scope name of the name
preferred        | Boolean | Indicates whether this is the preferred name of its topic
hidden           | Boolean | Indicates whether the name is hidden
id               | Integer | Internal ID of the name

---

## Names Subset

Get a list of names by certain characteristics, including starting letter, containing a search term, filtered by type, or filtered by scope.  This works very similar to the filtering [by topic](#topic-subset), so getting all names that start with a number or symbol would be:

```
/api/hit/hits/search/?letter=#
```

However, the name filtering also includes a few additional options, including finding any case-insensitive substring within the name. For example, the query

```
/api/hit/hists/search/?name="adams"
```

Would include all names that contain _adams_, whether or not it was at the begining (e.g. it would return both _Henry Adams_ and _adams apple_).

!!! Note 
    In its current iteration, this endpoint requires exact string matches.  So while the above request would include _adams apple_, it would __not__ return _adam's apple_, due to the apostrophe preventing the exact string match.  

The Names Subset enpoints can also filter names by scope, so any name with a given scope can be found with 

```
/api/hit/hits/search/?scope=SCOPE_ID
```

Where __SCOPE_ID__ is the internal id of the given scope.  It's also worth noting that these various filters can be chained together, so the API query

```
/api/hit/hits/search/?letter=A&name=justice
```

Would return all names that start with the letter A and contains the (case-insensitive) string "justice".

For the structure of the response, see the [All Names](#all-names) API endpoint.

---

## All Scopes

Gives a list of all scopes in the system:

```
/api/hit/scope/all/
```

### Example response

```json
[
    {
        "id": 2,
        "scope": "Generic"
    },
    {
        "id": 3,
        "scope": "musical group"
    },
    ...
    {
        "id": 88,
        "scope": "Internet"
    }
]
```

### Field Descriptions

Field         | Type    | Description
------------- | ------- | -----------
id            | Integer | Internal id and primary identifier for each topic
scope         | String  | Human-readable description of the scope

---

## All Topic Types

Gives a list of all Topic Types in the system:

```
/api/topic/ttype/all/
```

### Example response

```json
[
    {
        "ttype": "schema:CreativeWork",
        "id": 1
    },
    {
        "ttype": "schema:Intangible",
        "id": 2
    },
    ...
    {
        "ttype": "Native Americans",
        "id": 21
    },
    {
        "ttype": "pto:Pseudonym",
        "id": 22
    }
]
```

### Field Descriptions

Field         | Type    | Description
------------- | ------- | -----------
id            | Integer | Internal id and primary identifier for each topic
ttype         | String  | Human-readable description of the Topic type
