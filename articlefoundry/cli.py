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

def parse_call():
    desc = """
    CLI-based articlefoundry tools for preparing article archives for Ambra
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('article_file', type=argparse.FileType('rw'),
                        help="file location of the article .zip")
    parser.add_argument('-l', '--logging-level', nargs=1, help="logging level (defaults to ERROR",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    subparsers = parser.add_subparsers(help='action dispatcher')
    
    # pdf pagecount help
    parser_pdf = subparsers.add_parser('get-pdf-page-count',
                                       help="return the number of pages in the article package's pdf")
    parser_pdf.set_defaults(func=get_pdf_page_count)

    # si consume
    parser_si = subparsers. add_parser('consume-si',
                                       help='merge in SI files found in an external .zip')
    parser_si.add_argument('si_package',
                           help="file location of the SI package",
                           type=argparse.FileType('r'))
    parser_si.set_defaults(func=consume_si)

    args = parser.parse_args()
    if args.logging_level:
        logging.getLogger('').setLevel(getattr(logging, args.logging_level[0]))

    args.func(args)

if __name__ == "__main__":
    parse_call()
