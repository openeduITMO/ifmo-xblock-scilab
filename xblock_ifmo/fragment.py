from mako.lookup import TemplateLookup
from mako.template import Template
from xblock.fragment import Fragment


class FragmentMakoChain(Fragment):

    base = None
    template = None
    context = {}
    _content = None
    lookup_dirs = None

    def __init__(self, content=None, base=None, lookup_dirs=None):
        assert base, FragmentMakoChain
        super(FragmentMakoChain, self).__init__(content=content)
        self.base = base
        self.lookup_dirs = lookup_dirs

    def body_html(self):

        if self.context is None:
            self.context = {}

        self.build_chain()
        return self.template.render(**self.context)

    def build_chain(self):

        lookup = None

        if self.base is not None:

            lookup = TemplateLookup(directories=self.lookup_dirs)

            if hasattr(self.base, 'build_chain'):
                self.base.build_chain()
                lookup.put_template('ifmo_xblock_base', self.base.template)
            else:
                lookup.put_string('ifmo_xblock_base', self.base.body_html())

        self.template = Template(text=self._content, lookup=lookup)

    @property
    def resources(self):
        seen = set()
        parent_res = self.base.resources or []
        return [x for x in self._resources + parent_res if x not in seen and not seen.add(x)]

    @property
    def content(self):
        return self.body_html()

    @content.setter
    def content(self, value):
        self._content = value



