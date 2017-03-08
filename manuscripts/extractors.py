import os
import re
import copy

from lxml import etree
from django.utils.html import strip_tags
from django.db.utils import IntegrityError
from django.conf import settings
from html import unescape

from otcore.occurrence.loaders import ByteLoader
from otcore.occurrence.models import Content, Location, Occurrence
from otcore.relation.models import RelatedBasket, RelationType
from otcore.hit.models import Hit
from otcore.hit.processing import merge_baskets
from otx_epub.extractors import EpubExtractor
from otx_xml.extractors import XMLExtractor

from .models import IndexPattern, Index
from initial.index_ids import index_ids
from initial.pattern_mapping import pattern_mapping


namespaces = {
    'dc': 'http://purl.org/dc/elements/1.1',
    'opf': 'http://www.idpf.org/2007/opf',
    'html': 'http://www.w3.org/1999/xhtml',
    'epub': 'http://www.idpf.org/2007/ops',
}


EXCLUDED_PAGE_IDS = ('ump-taylor02-0004' )


class IndexExtractor(XMLExtractor):
    """
    IndexExtractor is meant to be run AFTER the EpubExtractor, and passed the Epub document.
    This allows the extractor to use the Epub document to determine which IndexPattern to use
    """
    extract_document=False
    default_pattern_model = IndexPattern
    default_loader = ByteLoader

    def __init__(self, epub, **kwargs):
        self.document=epub

        self.locations=epub.locations.all()

        pattern = pattern_mapping[os.path.basename(epub.contents)]

        # overrides if you want to only do part of the extraction
        self.extract_hits = kwargs.get('extract_hits', True)
        self.extract_locations = kwargs.get('extract_locations', True)

        # Set properties for use later
        self.see_rtype = RelationType.objects.get(rtype='See')
        self.seealso_rtype = RelationType.objects.get(rtype='See Also')
        self.subentry_rtype = RelationType.objects.get(rtype='Subentry')

        super(IndexExtractor, self).__init__(source=epub.manifest, pattern_name=pattern)

    def create_locations(self):
        """
        Iterates through all the html files listed in the epub manifest,
        extract locations and content
        """

        xpath_string = '//*[@media-type="application/xhtml+xml" and not(@id="' + str(EXCLUDED_PAGE_IDS) + '")]/@href'
        xml_files = self.tree.xpath(xpath_string)

        sequence_number = 1
        locations = []

        for xml in xml_files:
            full_path = os.path.join(self.document.oebps_folder, xml)

            # for versions with repeat OEBPS dirs
            if not os.path.isfile(full_path):
                full_path = os.path.join(os.path.dirname(self.document.oebps_folder), xml)

            with open(full_path, 'r') as f:
                xml_as_string = f.read()

            pages = self.get_pages(xml_as_string)

            for page in pages:
                location = self.create_location(page, full_path, sequence_number)
                
                sequence_number +=1
                locations.append(location)

        return locations

    def get_pages(self, xml_string):
        """
        Check all possible pagenumber_pre_strings in the xml document.
        If the string is found in the xml document, split on that string.
        Otherwise, returns an empty list (which then skips Location/Content creation).
        """
        pages = []
        i = 0
        while i < len(self.pattern.pagenumber_pre_strings) and not pages:
            splitter = self.pattern.pagenumber_pre_strings[i]

            if splitter in xml_string:
                pages = xml_string.split(splitter)[1:]
            i += 1

        return pages

    def create_location(self, page, full_path, sequence_number):
        """
        Expects a string of text which starts with the page number.  Then removes the page number 
        (and the rest of the tag that contains it) and uses that to create Content and Locations.
        """
        number_end = page.find('"')
        tag_end = page.find('>')
   
        page_number = page[:number_end]
        page_text = unescape(strip_tags(page[tag_end+1:]))

        open_tag_location = page_text.find('<')
        if open_tag_location > -1:
            page_text = page_text[:open_tag_location]

        content, created = Content.objects.get_or_create(
            content_unique_indicator='{0}-page_{1}'.format(self.document.id, page_number),
            defaults={
                'text': page_text,
                'content_descriptor': 'page {}'.format(page_number)
            }
        )

        if not created:
            content.text += page_text
            content.save()

        location, _ = Location.objects.get_or_create(
            localid='page_{}'.format(page_number),
            filepath='{0}'.format(full_path),
            document=self.document,
            defaults = {
                'content': content,
                'sequence_number': sequence_number
            }
        )

        return location

    def create_hits(self):
        indexes = self.get_indexes()

        occurrences = []
        for index in indexes:
            local_occurrences = self.parse_index(index)
            occurrences.append(local_occurrences)

        return occurrences

    def get_indexes(self):
        manifest_index_ids = index_ids[os.path.basename(self.document.contents)].split(',')

        indexes = []
        for index_id in manifest_index_ids:
            if index_id:
                xpath_argument = "//opf:item[contains(@id,'{}')]/@href".format(index_id)
                relative_path = self.tree.xpath(xpath_argument, namespaces=namespaces)[0]
                full_path = os.path.join(self.document.oebps_folder, relative_path)

                # for versions with repeat OEBPS dirs
                if not os.path.isfile(full_path):
                    full_path = os.path.join(os.path.dirname(self.document.oebps_folder), relative_path)

                index = etree.parse(full_path).getroot()
                indexes.append(index)

                Index.objects.get_or_create(
                    epub = self.document,
                    indexpattern = self.pattern,
                    relative_location = full_path.split(settings.MEDIA_ROOT)[1]
                )

        return indexes

    def parse_index(self, index):
        main_entries = index.xpath('//html:{}'.format(self.pattern.xpath_entry), namespaces=namespaces)

        self.pg_regex = re.compile(self.pattern.separator_between_entry_and_occurrences + '["”]? [0-9vxin–—-]+$')

        occurrences = [] 
       
        for entry in main_entries:
            local_occurrences = self.process_entry(entry)
            occurrences += local_occurrences

        return occurrences

    def process_entry(self, entry):
        """
        Breaks an entry into its entries and subentries (if they exist)
        Then parses the entry into hits and occurrences using the appropriate pattern
        """
        subentries = []
        occurrences = []
        so_subentries = []
        if self.pattern.subentry_classes:
            entry, subentries = self.get_separate_line_subentries(entry)

            # parsing second-order subentries
            if self.pattern.separator_between_subentries:
                so_subentries = [self.get_inline_subentries(subentry) for subentry in subentries]

        if self.pattern.separator_between_subentries:
            entry, inline_subentries = self.get_inline_subentries(entry)
            subentries = inline_subentries
        
        # process entry
        hit, local_occurrences = self.parse_entry(entry, "", bool(subentries) or bool(so_subentries))
        occurrences += local_occurrences

        # process subentries
        for subentry in subentries:
            sub_hit, local_occurrences = self.parse_entry(subentry, hit, False)
            occurrences += local_occurrences

        # process second-order subentries
        for sub_pair in so_subentries:
            sub_hit, local_occurences = self.parse_entry(sub_pair[0], hit, bool(sub_pair[1]))

            for subentry in sub_pair[1]:
                if self.pattern.separator_before_first_subentry in sub_pair[0].xpath('string()'):
                    _, local_occurrences = self.parse_entry(subentry, sub_hit, False)
                else:
                    _, local_occurrences = self.parse_entry(subentry, hit, False)

                occurrences += local_occurrences

        return occurrences

    def get_inline_subentries(self, entry):
        """
        Fetches an entry and its subentries for indexes in which the subentries
        are in the same element as the main entries
        """
        separator = self.pattern.separator_between_subentries
        if separator and separator in entry.xpath('string()'):
            # replace xpath_seealso tags with their text equivalents
            etree.strip_tags(entry, '{{http://www.w3.org/1999/xhtml}}{}'.format(self.pattern.xpath_seealso))

            elem_as_string = etree.tostring(entry, encoding="unicode")

            # strip wrapping tags from string
            stripped_elem_as_string = elem_as_string.split('>', 1)[1]
            last_tag = stripped_elem_as_string.rfind('<')
            stripped_elem_as_string = stripped_elem_as_string[:last_tag]

            # clean string
            stripped_elem_as_string = stripped_elem_as_string.replace('&amp;', '&')

            new_entry = ""
            subentries = []

            # Remove See Also strings
            see_also = ""
            for splitter in self.pattern.see_also_split_strings:
                if splitter in stripped_elem_as_string:
                    stripped_elem_as_string, see_also = stripped_elem_as_string.split(splitter)

            see = ""
            for see_splitter in self.pattern.see_split_strings:
                if see_splitter in stripped_elem_as_string:
                    stripped_elem_as_string, see = stripped_elem_as_string.split(see_splitter)

            # Separate main entries and subentries into individual strings
            nodes = []
            while separator in stripped_elem_as_string:
                entry_text, stripped_elem_as_string = self.separate_inline_elements(stripped_elem_as_string)
                nodes.append(entry_text)
            if stripped_elem_as_string:
                nodes.append(stripped_elem_as_string)

            if see_also != "":
                try:
                    nodes[0] = '{0}<{1}>{2}</{1}>{3}'.format(nodes[0], self.pattern.xpath_seealso, splitter, see_also)
                except IndexError:
                    nodes.append('<{0}>{1}</{0}>{2}'.format(self.pattern.xpath_seealso, splitter, see_also))

            elif see != "":
                try:
                    nodes[0] = '{0}<{1}>{2}</{1}>{3}'.format(nodes[0], self.pattern.xpath_see, see_splitter, see)
                except IndexError:
                    nodes.append('<{0}>{1}</{0}>{2}'.format(self.pattern.xpath_see, see_splitter, see))

            nodes = [self.inline_string_to_node(node) for node in nodes]

            return nodes[0], nodes[1:]
        else:
            return entry, []

    def separate_inline_elements(self, entry_text):
        """
        If an embedded see or see also are in the next subentry, this splits on that.
        Otherwise, splits on the next avaialble subentry separator
        """
        separator = self.pattern.separator_between_subentries
        main_separator_location = entry_text.index(separator)

        if self.pattern.inline_see_also_start and self.pattern.inline_see_also_start in entry_text:
            see_also_start = entry_text.index(self.pattern.inline_see_also_start)
            see_also_end = entry_text.index(self.pattern.inline_see_also_end, see_also_start)

            if see_also_start < main_separator_location and see_also_end > main_separator_location:
                try:
                    next_separator = entry_text.index(separator, see_also_end)
                    return entry_text[:next_separator], entry_text[next_separator + len(separator):]
                except ValueError:
                    return entry_text, []

        if self.pattern.inline_see_start and self.pattern.inline_see_start in entry_text:
            see_start = entry_text.index(self.pattern.inline_see_start)
            see_end = entry_text.index(self.pattern.inline_see_end)

            if see_start < main_separator_location and see_end > main_separator_location:
                try:
                    next_separator = entry_text.index(separator, see_end)
                    return entry_text[:next_separator], entry_text[next_separator + len(separator):]
                except ValueError:
                    return entry_text, []

        return entry_text.split(self.pattern.separator_between_subentries, 1)

    def inline_string_to_node(self, node_text):
        elem = node_text.replace('&', '&amp;')
        full_elem = '<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">{}</p>'.format(elem)
        node = etree.fromstring(full_elem)
        return node

    def get_separate_line_subentries(self, entry):
        """
        Fetches an entry and its subentries for indexes in which
        subentries are separate elements
        """
        subentries = []
        next_entry = entry.getnext()

        # Skip non entries
        if next_entry is not None and len(next_entry.xpath('@class')) == 0:
            next_entry = next_entry.getnext()
        
        while next_entry is not None and next_entry.xpath('@class')[0] in self.pattern.subentry_classes:
            subentries.append(next_entry)
            next_entry = next_entry.getnext()

            # skip non entries
            if next_entry is not None and len(next_entry.xpath('@class')) == 0:
                next_entry = next_entry.getnext()

        return entry, subentries

    def parse_entry(self, entry, main_hit, has_subentries):
        """
        Creates an entries hit and occurrences from a given lxml node
        """
        old_entry = copy.deepcopy(entry)
        entry, pagenumbers = self.get_pagenumbers(entry)

        # Get the full entry text, minus pagenumbers
        # Will also include full See and See Also text
        entry_text = entry.xpath('string()').strip()
        
        # Gets and removes See Also text
        seealsos = []
        patterns = list(self.pattern.see_also_split_strings) # copy to prevent altering original list
        if self.pattern.inline_see_also_start:
            patterns.append(self.pattern.inline_see_also_start)
        for pattern in patterns:
            entry_text, seealso_set = self.split_on_pattern(
                entry_text, 
                pattern,
                self.pattern.separator_between_seealsos
            )
            seealsos += seealso_set

        # Gets and removes See text
        sees = []
        patterns = list(self.pattern.see_split_strings) # copy to prevent altering original list 
        if self.pattern.inline_see_start:
            patterns.append(self.pattern.inline_see_start)
        for pattern in patterns:
            entry_text, see_set = self.split_on_pattern(
                entry_text, 
                pattern,
                self.pattern.separator_between_sees
            )
            sees += see_set
    
        # remove lingering separator text
        entry_text = entry_text.strip()

        if not entry_text and not main_hit:
            print(old_entry.xpath('string()'))
            print("NO entry")
            return entry_text, []

        subentry = ""
        if entry_text:
            if entry_text[len(entry_text)-1] == self.pattern.separator_between_entry_and_occurrences:
                entry_text = entry_text[:len(entry_text)-1]

            # An entry sometimes contains its first subentry on its line
            # This extracts that entry
            separator = self.pattern.separator_before_first_subentry
            if separator and separator in entry_text and has_subentries:
                split_point = entry_text.rfind(separator)
                subentry = entry_text[split_point+1:].strip()
                entry_text = entry_text[:split_point].strip()

                subentry, pagenumbers = self.extract_pagenumbers_from_text(
                    subentry, pagenumbers, self.pg_regex
                )

            # Check for non-hyperlinked occurrences (ie. pagenumbers in the occurrence text)
            entry_text, pagenumbers = self.extract_pagenumbers_from_text(
                    entry_text, pagenumbers, self.pg_regex
            )

            if main_hit:
                entry_text = "{} -- {}".format(main_hit.name, entry_text)

            # Get/Create hit
            hit, _ = Hit.objects.get_or_create(name=entry_text)
            hit.create_basket_if_needed()

            # If the entry currently being parsed is a subentry,
            # create a relation to the main entry
            if main_hit:
                RelatedBasket.objects.get_or_create(
                    relationtype=self.subentry_rtype,
                    source=main_hit.basket,
                    destination=hit.basket
                )

            if subentry:
                subentry_hit, _ = Hit.objects.get_or_create(name="{} -- {}".format(entry_text, subentry))
                subentry_hit.create_basket_if_needed()
                RelatedBasket.objects.get_or_create(
                    relationtype=self.subentry_rtype,
                    source=hit.basket,
                    destination=subentry_hit.basket
                )
        else:
            # If a subentry is only a See/See Also, there won't be any given entry text
            # In those situations, treat the main_hit as the found hit
            hit = main_hit

        # Get/Create all see hits, make synonym of entry
        for see in sees:
            # Check for subentry
            if self.pattern.separator_see_subentry and self.pattern.separator_see_subentry in see:
                see = see.replace(self.pattern.separator_see_subentry, ' --')
            see_hit, _ = Hit.objects.get_or_create(name=see)
            see_hit.create_basket_if_needed()
            try:
                RelatedBasket.objects.create(
                   source=hit.basket,
                    destination=see_hit.basket,
                    relationtype=self.see_rtype
                )
            except IntegrityError:
                pass

        # Get/create all see also hits, make relation to entry basket
        for seealso in seealsos:
            if seealso:
                seealso_hit, _ = Hit.objects.get_or_create(name=seealso)
                seealso_hit.create_basket_if_needed()
                try:
                    RelatedBasket.objects.create(
                       source=hit.basket,
                        destination=seealso_hit.basket,
                        relationtype=self.seealso_rtype
                    )
                except IntegrityError:
                    pass

        # Create occurrences
        entry_occurrences = []
        basket_to_attach = hit.basket if not subentry else subentry_hit.basket
        for pg in pagenumbers:
            try:
                location = next(l for l in self.locations if l.localid == 'page_{}'.format(pg))
            except StopIteration:
                print("No location found at: {}".format(pg))
            else:
                occurrence = Occurrence.objects.create(
                    location=location, basket=basket_to_attach
                )
                entry_occurrences.append(occurrence)

        return hit, entry_occurrences

    def split_on_pattern(self, text, pattern, indicator):
        """
        Used for splitting an entry string into the actual entry and sees/see alsos
        Returns the processed entry string and a list of see or see also strings
        """
        remaining = []
        new_text = text

        if pattern in text:
            combined = text.split(pattern)
            new_text = combined[0]
            remaining = [s.strip() for s in combined[1].split(indicator)]

        return new_text, remaining

    def get_pagenumbers(self, entry):
        """
        Extracts and cleans the pagenumbers from a given entry.
        Then removes the pagenumber text from the entry, for easier Hit extractions
        """
        page_number_elements = entry.xpath(
            './/html:{}'.format(self.pattern.xpath_occurrence_link), 
            namespaces=namespaces
        )

        pagenumbers = []
        for pg in page_number_elements:
            if pg.text and re.match('[0-9vxi]', pg.text):
                num = pg.text
               
                # Strip non-numeric characters.  If it's a range or note, 
                # only take the first number
                num = re.split('[^0-9vxi]', num, 1)[0] 

                pagenumbers.append(num)

            pg.getparent().remove(pg)

        return entry, pagenumbers

    def extract_pagenumbers_from_text(self, entry_text, pagenumbers, match_pattern):
        """
        When pagenumbers aren't hyperlinked, the normal pagenumber extractor won't catch them.  
        This function extracts pagenumbers from the actual entry text, rather than from 
        embedded anchor tags
        """
        results = match_pattern.search(entry_text)

        while results:
            # Get and clean the matched pagenumber
            # (remove range markers and beginning separator/whitespace)
            numbers = results.group(0)
            has_quotes = '"' in numbers or '”' in numbers
            stripped_numbers = numbers.split(' ')[1]
            num = re.split('[^0-9vxi]', stripped_numbers, 1)[0] 
            
            pagenumbers.append(num)
            entry_text = entry_text.split(numbers, 1)[0]
            entry_text = entry_text + '"' if has_quotes else entry_text

            results = match_pattern.search(entry_text)

        return entry_text, pagenumbers
