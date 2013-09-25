import os
import shutil
import zipfile


def tuplesearch(s, t):
    f_ed = filter(lambda x: s == x[0], t)
    if f_ed:
        return map(lambda x: x[1], f_ed)
    raise KeyError("%s not found" % s)


class MZipFile():

    def __init__(self, filename):
        self.filename = filename
        self.zipfile = zipfile.ZipFile(self.filename, 'a')

    def __del__(self):
        pass

    def mv(self, mv_list):
        """
        mv_list is a list of 2-tuples: (<orig_filename>, <new_filename>)
          use <new_filename> = "" to delete an item
        destructive. make sure to close all open zip files first
        """
        temp_filename = "%s.tmp" % self.filename
        temp_zip = zipfile.ZipFile(temp_filename, 'w')
        for f in self.zipfile.namelist():
            try:
                new = tuplesearch(f, mv_list)[0]
            except KeyError:
                new = f

            if new:
                temp_zip.writestr(new, self.zipfile.read(f))

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

    def close(self):
        self.zipfile.close()
