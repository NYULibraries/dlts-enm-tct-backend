## Requirements

### Base Software Dependencies

This software is required for proper functioning of the ENM Ingest backend:

- Python >=3.3
- PostgreSQL

!!! note
    The __ENM Topic Curation Backend__ requires several postgres-specific features, including ArrayFields and column-specific distinct queries.  Subbing in another RDBMS such as SQLite or MySQL will likely render the software inoperable

!!! warning
    One of the python packages, psycopg2, requires PostgreSQL to be present before installing. Make sure both the above dependencies are installed __before__ installing the python dependencies below

### Python Dependencies

The main python dependencies can be installed from the `requirements.txt` file, which includes the specific version numbers used in development and production. You can simply install all required python libraries by type:

```
pip install -r requirements.txt
```

In case you need to reference the library list, though, here is the full list of python dependencies:

- Django==1.10.3
- django-allauth==0.27.0
- django-autoslug==1.9.3
- django-cors-headers==1.1.0
- django-debug-toolbar==1.5
- django-extensions==1.7.2
- django-filter==0.14.0
- django-rest-auth==0.8.1
- djangorestframework==3.4.6
- lxml==3.6.4
- psycopg2==2.6.2

This documentation was built with the [MkDocs](http://www.mkdocs.org/) markdown-based documentation library.  If you want to make changes to this documentation, this requires several additional python libraries:

- Markdown==2.6.8
- mkdocs==0.16.1
- mkdocs-material==1.0.3
- Pygments==2.2.0
- pymdown-extensions==1.8

For convenience, this all can be installed via:

```
pip install -r requirements-documentation.txt
```

## Current Production Platform

The following represent the current production environment for running the ENM Topic Curation Backend. These are not required, but have been tested as an effective production system:

- __OS__: Ubuntu 16.04
- __Application Server__: uWSGI
- __Web Server__: nginx
