from lxml import etree
import urlparse
import os

from util import download_file, get_single, ordinal_format, PLOSDoi

import logging
logger = logging.getLogger(__name__)


class CustomResolver(etree.Resolver):
    cache = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dtd-cache'))
    last_url = None

    def resolve(self, URL, id, context):
        logger.debug("Fetching %s ..." % URL)
        #determine cache path
        url = urlparse.urlparse(URL)
        # Handle relative paths for network locations
        if url.netloc:
            self.last_url = url
        else:
            if not self.last_url:
                raise ValueError("Invalid URL provided for DTD: %s" % URL)
            url = urlparse.urlparse(urlparse.urljoin(self.last_url.geturl(), URL))

        local_base_directory = os.path.join(self.cache, url.netloc)
        local_file = local_base_directory + url.path

        #cache if necessary
        if not os.path.exists(local_file):
            if not os.path.exists(os.path.split(local_file)[0]):
                os.makedirs(os.path.split(local_file)[0])
            download_file(url.geturl(), local_file)

        #resolve the cached file
        return self.resolve_file(open(local_file), context, base_url=URL)


class XMLObject(object):
    root = None
    self_ref_name = "XML document"
    filename = None

    def __init__(self, xml_string):
        try:
            main_parser = XMLObject.get_parser()
            self.root = etree.XML(xml_string, main_parser)
        except (etree.XMLSyntaxError, ValueError), e:
            logger.debug("Unable to parse %s due to the following syntax error: %s" %
                           (self.self_ref_name, unicode(e)))
            logger.debug("Falling back to more relaxed parser ...")
            fallback_parser = XMLObject.get_fallback_parser()
            try:
                self.root = etree.XML(xml_string, fallback_parser)
            except etree.XMLSyntaxError, ee:
                logger.error("Unable to parse XML file, %s: %s" % (self.self_ref_name, ee))
                raise ee

        logger.debug("Root: %s" % self.root)

    @staticmethod
    def get_parser():
        parser = etree.XMLParser(dtd_validation=True, no_network=False)
        parser.resolvers.add(CustomResolver())
        return parser

    @staticmethod
    def get_fallback_parser():
        parser = etree.XMLParser(recover=True, dtd_validation=False, no_network=True)
        return parser

    @staticmethod
    def check_for_dtd_error(xml_string):
        try:
            xmltree = etree.XML(xml_string, XMLObject.get_parser())
        except etree.XMLSyntaxError, e:
            return unicode(e)
        return ""

    def etree_to_string(self):
        etree.tostring(self.root, xml_declaration=True, encoding='UTF-8')

    def etree_to_file(self, filename=None):
        if filename:
            etree.write(filename, encoding='utf-8')
        else:
            etree.write(self.filename, encoding='utf-8')



class GOXMLObject(XMLObject):
    """
    def __init__(self, xml_file):
        parser = etree.XMLParser(recover=True)
        self.root = etree.parse(xml_file, parser)
        super(GOXMLObject, self).__init__(xml_file)
        self.self_ref_name = "GO XML Document"
    """
    def get_production_task_id(self):
        prod_ids = self.root.xpath("//header/parameters/parameter[@name='production-task-id']")
        prod_id = get_single(prod_ids, "guid")
        return prod_id.attrib['value']

    def get_production_task_name(self):
        production_task_names = self.root.xpath("//header/parameters/parameter[@name='production-task-name']")
        production_task_name = get_single(production_task_names, "production task name")
        return production_task_name.attrib['value']

    def get_metadata_filename(self):
        prod_ids = self.root.xpath("//filegroup/metadata-file")
        prod_id = get_single(prod_ids, "guid")
        return prod_id.attrib['name']

    def get_doi(self):
        dois = self.root.xpath("//header/parameters/parameter[@name='DOI']")
        doi = get_single(dois, "DOI")
        return PLOSDoi(doi.attrib['value'])

    def get_files(self):
        files = self.root.xpath("//filegroup/file")
        return [f.attrib['name'] for f in files]


class NLMXMLObject(XMLObject):

    def __init__(self, xml_file):
        self.self_ref_name = "NLM XML Document"
        super(NLMXMLObject, self).__init__(xml_file)

    def get_si_links(self):
        si_links = []
        for i, si in enumerate(self.root.xpath("//supplementary-material")):
            si_elem = {}
            try:
                si_elem['label'] = si.xpath("label")[0].text
            except IndexError:
                logger.error("%s %s SI entry is missing a label" %
                             (ordinal_format(i), self.self_ref_name))
                continue

            try:
                si_elem['link'] = si.attrib['{http://www.w3.org/1999/xlink}href']
            except KeyError:
                logger.error("%s %s SI entry, '%s', is missing an href" %
                             (ordinal_format(i), self.self_ref_name, si_elem['label']))

            si_links.append(si_elem)

        return sorted(si_links, key=lambda x: x.get('label'))

    def get_fig_links(self):
        fig_links = []
        for i, fig in enumerate(self.root.xpath("//fig")):
            fig_elem = {}
            try:
                fig_elem['label'] = fig.xpath("label")[0].text
            except IndexError:
                logger.error("%s figure in %s is missing a label" %
                             (ordinal_format(i), self.self_ref_name))
                continue

            try:
                graphic = fig.xpath("graphic")[0]
                fig_elem['link'] = graphic.attrib['{http://www.w3.org/1999/xlink}href']
            except IndexError:
                logger.error("%s figure in %s, '%s', is missing a graphic entry" %
                             (ordinal_format(i), self.self_ref_name, fig_elem['label']))
            except KeyError:
                logger.error("%s figure in %s, '%s', is missing an href" %
                             (ordinal_format(i), self.self_ref_name, fig_elem['label']))

            fig_links.append(fig_elem)

        return fig_links


class ArticleXMLObject(NLMXMLObject):
    def __init__(self, *args):
        self.self_ref_name = "article xml.orig"
        super(ArticleXMLObject, self).__init__(*args)


class MetadataXMLObject(NLMXMLObject):
    def __init__(self, *args):
        self.self_ref_name = "metadata xml"
        super(MetadataXMLObject, self).__init__(*args)

    def get_parser(self):
        return etree.XMLParser(recover=True)
