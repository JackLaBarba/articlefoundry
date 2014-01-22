import os
import shutil
from util import tuplesearch
import zipfile
import uuid

import logging
logging.basicConfig(level=logging.DEBUG,
                    format=("%(levelname)-8s "
                            "%(message)s"))
logger = logging.getLogger(__name__)

TEMP = os.path.abspath('/tmp')


class ArchiveFile():
    read_only = False
    filename = None
    zipfile = None
    unzipped = False
    uuid = None
    working_dir = None

    def __init__(self, filename, read_only=False):
        self.read_only = read_only
        self.filename = filename

    def _get_working_filename(self, filename):
        if not self.working_dir:
            raise RuntimeError("Can't perform this action on an un-unzipped archive")
        return os.path.join(self.working_dir, filename)

    def _check_for_file_existence(self, filename):
        if not self.file_exists(filename):
            logger.debug("archive files: %s" % self.list())
            raise KeyError("Archive (%s) does not contain a file named '%s'." %
                           (self, filename))

    def file_exists(self, filename):
        return filename in self.list()

    def unzip(self):
        self.zipfile = zipfile.ZipFile(self.filename, 'r')
        self.uuid = "af_" + str(uuid.uuid1())
        self.working_dir = os.path.join(TEMP, self.uuid)
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)
        self.zipfile.extractall(path=self.working_dir)
        self.zipfile.close()
        self.unzipped = True

    def close(self):
        logger.debug("Closing %s ..." % self)
        if self.unzipped:
            temp_zip_location = os.path.join(TEMP, self.uuid + '.zip')
            if not self.read_only:
                new_zip = zipfile.ZipFile(temp_zip_location, 'w')
                logger.debug("Zipping files into temp location, %s ..." % temp_zip_location)
                for root, dirs, files in os.walk(self.working_dir):
                    for f in sorted(files, key=lambda s: s.lower()):
                        new_zip.write(os.path.join(root, f), f)
                new_zip.close()

                final_dest = self.filename
                logger.debug("Moving %s to %s ..." % (temp_zip_location, final_dest))
                shutil.move(temp_zip_location, final_dest)

            logger.debug("Cleaning up %s ..." % self.working_dir)
            shutil.rmtree(self.working_dir)
            self.unzipped = False

    def list(self):
        if not self.unzipped:
            self.unzip()
        return sorted(os.listdir(self.working_dir), key=lambda x: x.lower())

    def get(self, filename):
        if not self.unzipped:
            self.unzip()
        self._check_for_file_existence(filename)
        working_filename = os.path.join(self.working_dir, filename)
        f = file(os.path.join(self.working_dir, working_filename), 'rb')
        return f

    def rename(self, before, after):
        if not self.unzipped:
            self.unzip()
        self._check_for_file_existence(before)
        before_filename = self._get_working_filename(before)
        after_filename = self._get_working_filename(after)
        shutil.move(before_filename, after_filename)

    def remove(self, filename, force=False):
        if not self.unzipped:
            self.unzip()
        if self.file_exists(filename):
            os.remove(self._get_working_filename(filename))
            return True
        elif not force:
            self._check_for_file_existence(filename)
        else:
            return False

    def add(self, f, filename):
        logger.debug("Adding %s to %s as '%s ...'" % (f, self, filename))
        if not self.unzipped:
            self.unzip()
        f.seek(0)
        with open(self._get_working_filename(filename), 'wb') as new_f:
            logger.debug("Writing into %s ..." % self._get_working_filename(filename))
            for chunk in f:
                new_f.write(chunk)

    def __repr__(self):
        return os.path.split(self.filename)[1]