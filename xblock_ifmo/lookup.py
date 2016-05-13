from mako.lookup import TemplateLookup as TemplateLookupBase
from mako import util

import posixpath


class TemplateLookup(TemplateLookupBase):

    def append_dirs(self, directories):
        self.directories = [posixpath.normpath(d) for d in
                            util.to_list(directories, ())
                            ] + self.directories
