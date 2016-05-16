# -*- coding=utf-8 -*-

from mako.template import Template
from xblock.fragment import Fragment

from .lookup import TemplateLookup  # xblock_ifmo.lookup
from .utils import deep_update


class FragmentMakoChain(Fragment):
    """
    Класс, позволяющий последовательно оборачивать экземпляры Fragment друг в
    друга.

    Для того, чтобы цепочка отработала, шаблон должен наследоваться от шаблона
    ifmo_xblock_base и определять блок block_body.

    Порядок оборачивания не определён.
    """

    base = None
    context = {}
    _content = None
    lookup_dirs = None

    def __init__(self, content=None, base=None, lookup_dirs=None):
        """
        Класс, позволяющий последовательно оборачивать экземпляры Fragment друг
        в друга.

        :param content: Содержимое фрагмента
        :param base: Базовый фрагмент, тот, в который будет обёрнут этот фрагмент;
                     должен быть экземпляром FragmentMakoChain или None
        :param lookup_dirs: Директории поиска шаблонов
        :return:
        """
        assert isinstance(base, FragmentMakoChain) or base is None
        super(FragmentMakoChain, self).__init__(content=content)
        self.base = base
        self.lookup_dirs = lookup_dirs

    def body_html(self):
        template = self.build_chain()
        return template.render(**self.context.get('render_context', {}))

    def add_context(self, new_context):
        deep_update(self.context, new_context)

    def build_chain(self):
        """
        Строит цепочку шаблонов.

        В цепочке каждый шаблон наследуется от одного и того же ifmo_xblock_base,
        поэтому порядок оборачивания не определён (точнее, его вычисляет
        метод super()). Поскольку при рендере шаблона используется исключительно
        lookup от шаблона, над которым он вызван, а не собственный Lookup для
        каждого из шаблона в коллекции, необходимо добавить в коллекцию все
        пути и шаблоны, использующиеся в шаблоне выше по цепочке. Более того,
        необходимо изменить имена шаблонов (ifmo_xblock_base) на уникальные.

        :param lookup: экземпляр TemplateLookup, в который будут записываться
                       новые пути и шаблоны, использующиеся как родительские

        :return: tuple(template, lookup, base_template_id)
            - template -- шаблон, который должен будет стать родителем
            - lookup -- изменённый lookup
        """

        def _build_chain(self, lookup=None):

            old_base_name = "ifmo_xblock_base"
            new_base_name = None

            if self.base is not None:

                import uuid
                new_base_name = "{name}_{rnd}".format(name=old_base_name, rnd=str(uuid.uuid4()))

                if hasattr(self.base, 'build_chain'):
                    base_template, base_lookup = _build_chain(self.base, lookup)
                    lookup.put_template(new_base_name, base_template)
                else:
                    lookup.put_string(new_base_name, self.base.body_html())

                lookup.append_dirs(self.base.lookup_dirs)

            return Template(
                text=self._content.replace(old_base_name, new_base_name) if new_base_name else self._content,
                lookup=lookup
            ), lookup

        lookup = TemplateLookup(directories=self.lookup_dirs)
        template, _ = _build_chain(self, lookup)
        return template

    @property
    def resources(self):
        seen = set()
        parent_res = self.base.resources if self.base else []
        return [x for x in self._resources + parent_res if x not in seen and not seen.add(x)]

    @property
    def content(self):
        return self.body_html()

    @content.setter
    def content(self, value):
        self._content = value
