## API Overview

In order to make this documentation as flexible as possible, all API endpoints are listed relative to the base domain -- for example, the endpoints to get all topics is listed as:

```
/api/hit/basket/all/
```

If the api were at `http://api.enhanced-network-monographs.com` (just, to be clear, a totally invented url), the full URL to access the above endpoint would be:

```
http://api.enhanced-network-monographs.com/api/hit/basket/all
```

!!!Note 
    This documentation __only__ covers the publicly accessible (i.e. read-only) API Endpoints. API endpoints that actually manipulate the database (such as adding and deleting Topics) require authentication, and can currently only be used via the __Topic Curation Toolkit__.

!!! warning "IDs and Consistency"
    Most objects in the database have an `id` attribute. IDs are guaranteed to be unique for that particular resource in a database: only one `basket` object will have an ID of __10__, for example.  However, the system does __not__ guarantee that IDs will be consistent across databases.  In other words, if an ingest is done from scratch on a new system (rather than importing a database copy), IDs may not match those from a different ingest.

## API Categories

- __[Topics](topics)__: All API endpoints relating to Topics and Names
- __[Sources](sources)__: All API endpoitns relating to Epubs and Pages

