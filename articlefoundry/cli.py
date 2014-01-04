import argparse
from article import Article, MetadataPackage
import logging
logging.basicConfig(level=logging.DEBUG,
                    format=("%(levelname)-8s "
                            "%(message)s"))
logging.getLogger('').setLevel(logging.ERROR)


def get_pdf_page_count(args):
    a = Article(archive_file=args.article_file.name)
    print a.get_pdf_page_count()

def consume_si(args):
    a = Article(archive_file=args.article_file.name)
    si = MetadataPackage(archive_file=args.si_package.name)
    a.consume_si_package(si)
    a.close()

def check_for_dtd_error(args):
    a = Article(archive_file=args.article_file.name)
    error = a.check_for_dtd_error()
    if error:
        if args.format_ariespull:
            print "error: DTD error: %s" % error
        else:
            print error

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
    parser_si.add_argument('si_package',
                           help="file location of the SI package",
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
