## Software configuration

### Database setup

By default, __ENM Topic Curation Toolkit Backend__ expects PostgreSQL to have a user `postgres` with the password `cFHg*Liw45(`, and a database called `nyuotl_db`. If different settings are required, you can change the `DATABASES` value in `nyu/production_settings.py`, which is just a python dictionary of expected database settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nyuotl_db',
        'USER': 'postgres',
        'PASSWORD': 'cFHg*Liw45(',
        'HOST': 'localhost',
    }
}
```

### Secret Keys

__ENM Topic Curation Toolkit Backend__ requires a file `nyu/secret_keys.json` with the following structure:

```json
{
  "SECRET_KEY": "some_long_random_string_of_letters_numbers_and_symbols"
}
```

The secret key is primarily used for hashing passwords, and for security reasons is therefore not kept in the repo.  If you transfer a database with user information (such as from a full .sql dump of a database), you _must_ also transfer the `secretkeys.json` file to the new installation, or the password hashes will no longer work and user passwords will all have to be manually reset.

## Importing Data

There are two ways of getting data into the __ENM Topic Curation Toolkit Backend__:

1. [Importing an existing database dump](#database-import)
2. [Run a batch ingest from scratch](#batch-ingest)

### Database Import

Assuming you have a .sql file which is a full database dump of a currently existing database, import the data means simply running

```bash
sudo psql nyuotl_db < DUMP_FILE_NAME.sql
```

If you have changed the name of the database in the settings file, make sure to use the new database name instead of `nyuotl_db`.

### Batch Ingest

Ingesting a set of EPUBs from scratch requires a little more setup and configuration.  If you are starting with a fresh database, you'll first need to create the requisite tables with the following command (run from the folder in which the software was installed):

```bash
python manage.py migrate
```

If you are using the existing set of EPUBs, you'll need to load the IndexPattern data with the following command:

```bash
python manage.py loaddata indexpatterns.json
```

If you are __not__ using the existing set of EPUBs, please see the [adding a new EPUB](new.md) section for instructions on how to configure the system to accept a new EPUB.

Lastly, ensure that the EPUB files to be ingested are in the proper place. That depends on two settings in the `nyu/production_settings.py` folder:

```python
MEDIA_ROOT = '/www/nyu.infoloom.nyc/media/'
EPUB_SOURCES_FOLDER = os.path.join(MEDIA_ROOT, 'epubs')
```

The `MEDIA_ROOT` folder specifies where __all__ user provided files should be placed on the server, and the `EPUB_SOURCES_FOLDER` is a subfolder inside that where all EPUBS to be processed should be placed. Change the folders to whatever location on the server you would like to store the EPUBS, make sure that the application has write-access to those files (for unzipping the EPUBs), and then run the following command:

```bash
python3 manage.py runscript full_batch
```
