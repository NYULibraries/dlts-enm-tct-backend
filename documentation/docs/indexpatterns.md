Adding new Indexpattern is perhapse the most complicated part of configuring the __ENM TCT Backend__.  This page will explain the various fields in the Indexpattern model and how they might be configured for a new Indexpattern, but be aware that this process is often iterative and may require some trial and error to get the proper values.

## Indexpattern Fields

### id

__Field Type__: Integer

This is a unique, internal id for the Indexpattern.  It is, for the most part, not used by __ENM TCT__, as Indexpatterns are usually fetched by their "name" attribute, which is more likely to be consistent across implementations. However, if adding a new Indexpattern via the `indexpatterns.json` fixture, you __must__ include a value for this field that is not used by a currently existing Indexpattern.

---

### Name

__Field Type__: String

This string field must be unique within the database.  It is the primary means of fetching a specific Indexpattern from the database.

---

### Description

__Field Type__: String

This is a longer, human-readable text description of the IndexPattern. This field does __not__ have an enforced uniqueness, and is merely meant to help the editor choose the proper Indexpattern.

---

### xpath_entry

__Field Type__: String

XPath term used by lxml specifying a __main__ entry nodes in the index.  For example, an EPUB with the following structure for an index entry:

```xml
<p class="indexmain">Washington, George, <a class="nounder" href="ch03.html#page_73">73</a>&#8211;85</p>
```

would have a value of `p[@class="indexmain"]` for __xpath_entry__.

---

### subentry_classes

__Field Type__: Array (string)

A list of classes used to indicate a subentry in the index, specifically for indexes with separate line subentries.  For example, an index with the following subentry:

```xml
<p class="indexsub">Presidency of, <a class="nounder" href="ch04.html#page_109">109</a></p>
```

would have a value of `['indexsub']` for __subentry_classes__.

!!! Note
    This field is only used for indexes in which there are seperate line rather than (or in addition to) inline subentries.  If left blank, the parser will assume that the index __only__ contains inline subentries. 

---

### xpath_see

__Field Type__: String

Tag type that encloses a "see" indicator in the EPUB. For example, an index with the following entry

```xml
<p class="indexmain">First President. <em>See</em> Washington, George</p>
```

would have a value of `em` for __xpath_see__.

---

### xpath_seealso

__Field Type__: String

Tag type that enclose a "see also" indicator in the EPUB.  For example, an index with the following entry:

```xml
<p class="indexmain">Early Presidents, <a class="nounder" href="ch01.html#page_28">28</a>, <a class="nounder" href="ch01.html#page_31">31</a>. <em>See also</em> Washington, George</p>
```

would have a value of `em` for __xpath_seealso__.

---

### pagenumber_pre_strings

__Field Type__: Array (String)

When identifying pages in the text, this is the string used to split an entire page to separate into individual pages. The goal is to have each remaining page string begin with the pagenumber, so the split string should include the tag text that occurs right before the pagenumber.  For example, in an EPUB with the following text:

```xml
<p class="indent">Washington was widely admired for his strong leadership qualities and was unanimously elected president by the Electoral College in the first two national elections. He oversaw the creation of a strong, well-financed national government that maintained neutrality in the French Revolutionary Wars, suppressed the Whiskey Rebellion, and won acceptance among Americans of all types.[3] <a id="page_172"></a>Washington's incumbency established many precedents still in use today, such as the cabinet system, the inaugural address, and the title Mr. President.[4][5] His retirement from office after two terms established a tradition that lasted until 1940 when Franklin Delano Roosevelt won an unprecedented third term. The 22nd Amendment (1951) now limits the president to two elected terms.</p>
```

could have a value of `['id="page_']` for __pagenumber_pre_strings__.

(Example text from Wikipedia)

---

### pagenumber_xpath_pattern

__Field Type__: String

An xpath pattern used to find a particular page using xpath in the original text. Any tool using this pattern will use python's string `format` function to construct the specific xpath pattern for that particular page, and should therefor include the characters `{}` or `{0}` where the pagenumber should be inserted. If the pagenumber should be used multiple times in the string, you must use the second version `{0}`.  So, for example, the text from the [pagenumber_pre_strings example](#pagenumber_pre_strings) would have a value of `a[@id="page_{0}"]` for __pagenumber_xpath_patern__.

---

### pagenumber_css_selector_pattern

__Field Type__: String

This field functions much like the [pagenumber_xpath_pattern](#pagenumber_xpath_pattern), but for CSS Selectors instead of Xpath. For example, the same text from the [pagenumber_pre_strings example](#pagenumber_pre_strings) would have a value of `#page_{0}` for __pagenumber_css_selector_pattern__.

---

### pagenumber_tag_pattern

__Field Type__: String

This field functions much like the [pagenumber_xpath_pattern](#pagenumber_xpath_pattern), but instead reconstructs the original pagenumber locator tag as it existed in the original text. For example, the same text from the [pagenumber_pre_strings example](#pagenumber_pre_strings) would have a value of `<a id="page_{0}">` for __pagenumber_tag__pattern__.

---

### separator_between_entry_and_occurrences

__Field Type__: String

Punctuation used to separate entry text from its occurrences (page numbers). For example, the index entry:

```xml
<p class="indexmain">Washington, George, <a class="nounder" href="ch03.html#page_73">73</a>&#8211;85</p>
```

Would have a value of `,` for __separator_between_entry_and_occurrences__.

---

### xpath_occurrence_link

__Field Type__: String

Xpath used to find occurence (page number) links within an entry. For example, the index entry:

```xml
<p class="indexmain">Washington, George, <a class="nounder" href="ch03.html#page_73">73</a>&#8211;85</p>
```

would have a value of `a[@href]` for __xpath_occurence_link__.

---

### separator_before_first_subentry

__Field Type__: String

Some indexes with separate line subentries will put the first subentry on the same line as the main entry (particularly if the main entry itself has no occurrences). The punctuation mark in __separator_before_first_subentry__ is used to separate between the main entry text and the first subentry text in these instances. For example, the entry

```xml
<p class="indexmain"><em>Washington, George</em>: and Cherry Tree, <a class="nounder" href="ch02.html#page_74">74</a>&#8211;5;</p>
```

would have a value of `:` for __separator_before_first_subentry__.

---

### separator_between_subentries

__Field Type__: String

Inline subentries use punctation to separate between different subentries on the same line: this field holds the punctuation that demarkates a new subentry. For example, the following index text:

```xml
 <p class="in">Adams, Henry, <a class="xref" href="ump-taylor02-0013.html#p211">211n83</a>; 
    apocalyptic view of the future, <a class="xref" href="ump-taylor02-0008.html#p60">60</a>, <a class="xref" href="ump-taylor02-0008.html#p65">65</a>;
    boundary of life and death blurred in, <a class="xref" href="ump-taylor02-0008.html#p57">57</a>.
</p>
```

would have a value of `:` for __separator_between_subentries__.

!!! Note
    This field is __only__ used in indexes with inline subentries.  If this value is left blank, the parser will assume that the index contains only separate line subentires

---

### separator_between_sees

__Field Type__: String

Punctuation used to separate multiple "see" targets in an index. For example, the entry 

```xml
<p class="indexsub">Washington, George, <a class="nounder" href="ch02.html#page_39">39</a>&#8211;41. 
    <em>See</em> American Presidency; Founding Fathers; Cannot Tell a Lie
</p>
```

would have a value of `;` for __separator_between_sees__.

---

### separator_see_subentry

__Field Type__: String

A "see" relation might point to a subentry, rather than the main entry of a text.  In those cases, this punctuation is used to indicate the difference between the main entry and subentry text in the target subentry.  For example, in the entry:

```xml
<p class="indexmain">Truthfulness in politics, <a class="nounder" href="ch02.html#page_51">51</a>&#8211;52. <em>See also</em> Washington, and Cherry Tree</p>
```

the target is not the main topic __Washington, and Cherry Tree__ but the subentry __and Cherry Tree__ of the main entry __Washington__. In this case, the value of __separator_see_subentry__ would be `,`.

---

### separator_between_seealsos

__Field Type__: String

Functions similarly to [separator_between_sees](#separator_between_sees), but with "see also" relations instead of "see" relations.

---

### inline_see_start

__Field Type__: String

Some inline subenty indexes include both multiple subentries _and_ multiple see relations in a single line.  Even worse, sometimes these are separated by exactly the same punctuation. In those situations, the index will wrap the see in certain punctuation, such as parenthesis. When parsing these situations, the index extractor is looking at the content _stripped of tags_, so for an index with text that looks like this:

```
Washington, George, 8, 9, 18, 24, 89, 94, 101, 102, 172, 180n7, 250n29; and Cherry Tree, 68, 77; Presidency of (see American Presidency; Founding Fathers; Constitution), 7, 20, 101, 110, 164, 169. 
```

the value of __inline_see_start__ would be `(see`.

---

### inline_see_end 

__Field Type__: String

This field marks the end of a series of see relations in an inline subentry index.  Using the same example from [inline_see_start](#inline_see_start) above, the value of __inline_see_end__ would be `)`.

---

### inline_see_also_start

__Field Type__: String

Functionally equivalent to [inline_see_start](#inline_see_start) above, but for "see also" relations.

---

### inline_see_also_end

__Field Type__: String

Functionally equivalent to [inline_see_end](#inline_see_end) above, but for "see also" relations.

---

### indicators_of_occurence_range

__Field Type__: Array (String)

Indexes may express occurrences as a range rather than a single page.  __OTL TCT__ extraction, however, only captures the first page, and so this field helps tell the parser to ignore the number at the end of the occurrence range.  Howeer, due to inconsistent formatting, an index may use multiple punctuation types to express a range (for example, both hyphens and em dashes). For such an index, the value of __indicators_of_occurrence_range__ might be `["-", "–"]`.

---

### see_split_string

__Field Type__: Array (String)

String that indicates the beginning of a See relation.  Because there can be multiple punctuation styles within a given document, the split strings are an array rather than a single option. Like with [inline_see_start](#inline_see_start), the See items are extracted with tags removed, just looking at the entry as plain text. So, for an entry with the following text:

```
First President. See Washington, George
```

the value of __see_split_string__ would be `. See`.  Note the inclusion of the leading period, which is important for separating a See relation from an entry that has the word "See" in it (such as "The Holy See").

---

### see_also_split_string

Same as [see_split_string](#see_split_string), but for "See Also" relations instead of "See" relations.
