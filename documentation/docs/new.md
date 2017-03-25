This guide assumes that you have already batch ingest a number of EPUBs, and are looking to manually add an additional EPUB.  It will take you through the steps of adding a new EPUB into the system.  If you want to know how to do an initial batch import, please refer to that [section of the setup guide](setup#importing-data).

## Place the EPUB in the EPUB_SOURCES folder

The new EPUB should be place in the folder  specified by the attribute `EPUB_SOURCES_FOLDER` in `nyu.production_settings`. Once placed, run the following command:

```bash
python manage.py add_new_epub EPUB_FILENAME
```

make sure that you only provide the base EPUB filename, not the full path.  Note that this will merely decompressed the EPUB and load its metadata, it will __not__ extract Topics, Names, or Locations.

## Choose an Indexpattern for the Epub or create a new one

The new, decompressed EPUB can be found in the folder specified by the `EPUB_DECOMPRESSED_FOLDER`.  Open the xhtml files in the EPUB and see if its xhtml structure and index structure match any of the existing Indexpatterns.  

If you need to create a new Indexpattern to match the current structure, please see [our separate guide](indexpatterns).  Once the new Indexpatterns is created, be sure to add it to the `indexpatterns.json` file, and then rerun Indexpattern ingest:

```bash
python manage.py loaddata indexpatterns
```

Whether you are creating a new Indexpattern or re-using the older, once you have selected an Indexpattern, add it to the python dictionary in `initial/pattern_mapping.py`. Make sure the key matches the filename (without the .epub) and the value matches the name of the Indexpattern.  So, for example, for an epub with a filename _0123456789999.epub_ and using the _nyup1_ indexpattern, you'd add the following line to the pattern_mapping dictionary:

```python
    '0123456789999': 'nyup1',
```

## Locate the Index ID in the manifest

Inside the unzipped Epub document, locate the _EPUB manifest_. This file, usually (but not exclusively) a .opf file, will list the contents and ordering of the EPUB document. Locate the index(es) in the list of `<item>` tags, and note the id attribute on that tag. That id must be added to the `initial/index_ids.py` dictionary. The structure is much like that on the `pattern_mapping` dictionary, so an epub with the filename _0123456789999.epub_ and an index id of _ch09index.html_ would require the following line to the index_ids dictionary:

```python
    '0123456789999': 'ch09index.html',
```

Some books may have separate index files (for example, a subject index and an author index). In those cases, add the multiple indexes as a single comma-separate string, e.g.:

```python
    '0123456789999': 'ch09s_index.html,ch10a_index.html',
```

## Parse the index

The following command will run extract the Locations, Content, Names, Topics, and Occurrences from the index:

```bash
    python manage.py parse_epub EPUB_FILENAME
```
