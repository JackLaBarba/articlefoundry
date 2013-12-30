import os
import shutil
from util import tuplesearch
import zipfile


class MZipFile():

    def __init__(self, filename):
        self.filename = filename
        self.zipfile = zipfile.ZipFile(self.filename, 'a')

    def __del__(self):
        pass

    def mv(self, mv_list, normalizer=None):
        """
        mv_list is a list of 2-tuples: (<orig_filename>, <new_filename>)
          use <new_filename> = "" to delete an item.
        Destructive. make sure to close all open zip files first
        """
        temp_filename = "%s.tmp" % self.filename
        temp_zip = zipfile.ZipFile(temp_filename, 'w')
        for f in self.zipfile.namelist():
            try:
                new_name = tuplesearch(f, mv_list, normalizer)[0]
            except KeyError:
                new_name = f

            if new_name:
                temp_zip.writestr(new_name, self.zipfile.read(f))

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in temp_zip.filelist:
            zfile.create_system = 0

        # shuffle archives around
        self.zipfile.close()
        temp_zip.close()

        os.remove(self.filename)
        shutil.move(temp_filename, self.filename)
        self.zipfile = zipfile.ZipFile(self.filename, 'a')

        return self

    def add(self, file, filename):
        self.zipfile.writestr(filename, self.zipfile.read(file))
        for zfile in self.zipfile:
            zfile.create_system = 0

    def close(self):
        self.zipfile.close()
