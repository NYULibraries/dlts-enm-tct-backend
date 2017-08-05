## API Overview

Description                         | Endpoint                                                    | Extra Parameters
----------------------------------  | ---------------------------------------------------------   | ----------------
List of RelationTypes               | [/api/relation/rtype/all/](#all-relationtypes)              |

---

## All RelationTypes

Gives a list of all RelationTyes in the system:

```
/api/relation/rtype/all/
```

### Example response

```json
[
 {
        "id": 6,
        "rtype": "Containment",
        "role_from": "contained by",
        "role_to": "contains",
        "symmetrical": false
    },
    {
        "id": 5,
        "rtype": "Generic",
        "role_from": "Generic",
        "role_to": "Generic",
        "symmetrical": true
    },
    ...
    {
        "id": 4,
        "rtype": "Subentry",
        "role_from": "Main Entry of",
        "role_to": "Subentry of",
        "symmetrical": false
    }
]
```

### Field Descriptions

Field         | Type    | Description
------------- | ------- | -----------
id            | Integer | Internal id and primary identifier for each RelationType
rtype         | String  | Description of the RelationType. Only used internally, not seen by the end user
role_from     | String  | Description of a single direction of a basket relationship: displays when the basket direction is "destination". E.g., in the `Main Entry/Subentry` relationship above, if the relation on the basket says "destination", the relation will display as `Main Entry of TARGET_TOPIC`
role_to       | String  | Description of a single direction of a basket relationship: same as above, but for relations labeled "source"
symmetrical   | Boolean | Tracks whether the role_to and role_from are identical for that topic type
