# -*- coding=utf-8 -*-


from xqueue_api.xobject import XObjectResult


class AjaxHandlerMixin(object):
    """
    Когда приходит callback от xqueue, вызывается метод handle_ajax. Однако,
    метод XBlock.handle_ajax не имеет никакого отношения к реализации этого
    метода, поэтому обычные XBlock-и не имеют такого атрибута в принципе. Чтобы
    ловить хендлеры от xqueue, нужно его реализовать. Этот миксин несёт
    минимальную реализацию, которая позволит просто замаскировать методы под
    хендлеры.
    """

    @staticmethod
    def pseudo_ajax_handler(func):
        assert hasattr(func, '__call__') and hasattr(func, 'func_name')
        func._is_pseudo_ajax_handler = True
        return func

    @staticmethod
    def xqueue_callback(target_class_or_func):

        def wrapped(func):
            assert hasattr(func, '__call__') and hasattr(func, 'func_name')
            setattr(func, '_is_xqueue_callback', True)
            setattr(func, '_xqueue_result_class', target_class)
            return func

        if not isinstance(target_class_or_func, type):
            target_class = XObjectResult
            return wrapped(target_class_or_func)
        else:
            target_class = target_class_or_func
            return wrapped

    def handle_ajax(self, dispatch, data):

        method = getattr(self, dispatch, None)
        if getattr(method, '_is_pseudo_ajax_handler', False):
            method(data)

        elif getattr(method, '_is_xqueue_callback', False):
            submission_result = getattr(method, '_xqueue_result_class', XObjectResult)(data)
            method(submission_result)

        else:
            raise AttributeError("Attribute %s not found" % dispatch)

        self.save()


