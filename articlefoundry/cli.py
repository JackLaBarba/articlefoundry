import os
import argparse
from article import Article, MetadataPackage
from util import find_si_package
import logging
logging.basicConfig(level=logging.DEBUG,
                    format=("%(levelname)-8s "
                            "%(message)s"))
logging.getLogger('').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

SI_DIR = os.path.abspath("/var/local/delivery/")


def get_pdf_page_count(args):
    a = Article(archive_file=args.article_file.name)
    print a.get_pdf_page_count()


def consume_si(args):
    a = Article(archive_file=args.article_file.name)
    if args.si_package:
        si = MetadataPackage(archive_file=args.si_package.name)
    else:
        logger.debug("No metadata package provided in call, trying to find one in AI ...")
        si_package = find_si_package(a.doi) #TODO: add manual directory input
        if not si_package:
            a.close()
            raise IOError("Can't find metadata package for %s" %
                          a.doi)
        try:
            si = MetadataPackage(archive_file=si_package)
        except IOError, e:
            a.close()
            raise IOError("Can't find metadata package for %s at %s" %
                          (a.doi, si_package))
    a.consume_si_package(si)
    a.close()


def check_for_dtd_error(args):
    a = Article(archive_file=args.article_file.name, read_only=True)
    error = a.check_for_dtd_error()
    if error:
        if args.format_ariespull:
            print "error: DTD error: %s" % error
        else:
            print error
    a.close()


def parse_call():
    desc = """
    CLI-based articlefoundry tools for preparing article archives for Ambra
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('article_file', type=argparse.FileType('rw'),
                        help="file location of the article .zip")
    parser.add_argument('-l', '--logging-level', nargs=1, help="logging level (defaults to ERROR",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    subparsers = parser.add_subparsers(help='action dispatcher: define an action to apply to article_file')
    
    # pdf pagecount help
    parser_pdf = subparsers.add_parser('get-pdf-page-count',
                                       help="return the number of pages in the article package's pdf")
    parser_pdf.set_defaults(func=get_pdf_page_count)

    # si consume
    parser_si = subparsers.add_parser('consume-si',
                                       help='merge in SI files found in an external .zip')
    parser_si.add_argument('-s', '--si_package', nargs=1,
                           help="specify file location of the SI package, "
                                "otherwise will default to AI's stored si_guid",
                           type=argparse.FileType('r'))
    parser_si.set_defaults(func=consume_si)

    # dtd check
    parser_dtd = subparsers.add_parser('dtd-check',
                                       help='check xml.orig against its DTD and list any errors')
    parser_dtd.add_argument('-f', '--format-ariespull', action='store_true',
                            help="format output in a way that's easy to incorporate"
                            "with an ariesPull error string")
    parser_dtd.set_defaults(func=check_for_dtd_error)

    args = parser.parse_args()
    if args.logging_level:
        logging.getLogger('').setLevel(getattr(logging, args.logging_level[0]))

    args.func(args)

if __name__ == "__main__":
    parse_call()
