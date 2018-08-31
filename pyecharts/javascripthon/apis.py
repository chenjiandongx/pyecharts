# coding=utf8
"""
A core api for python-to-javascript translator.
"""

from __future__ import unicode_literals

import datetime
import json
import types
from collections import OrderedDict
from contextlib import contextmanager

from pyecharts.javascripthon.compat import TranslatorCompatAPI

__all__ = ['EChartsTranslator']


class JsSnippetMixin(object):
    def to_js_snippet(self):
        pass


class TranslatorMixin(object):
    """A Interface for state-machine translator
    """

    @contextmanager
    def new_task(self):
        try:
            self.reset()
            yield
        finally:
            self.reset()

    def reset(self):
        pass

    def translate(self):
        """Main process
        """
        pass


class FunctionStore(OrderedDict, JsSnippetMixin):
    """
    A OrderedDict which stores translated function.
    {<func_name>:<func>}
    """

    def to_js_snippet(self):
        return ''.join(self.values())


class TranslateResult(JsSnippetMixin):
    def __init__(self, options, options_snippet, function_store):
        self._options = options
        self._options_snippet = options_snippet
        self._function_store = function_store

    @property
    def options_snippet(self):
        return self._options_snippet

    @property
    def function_snippet(self):
        return self._function_store.to_js_snippet()

    @property
    def has_function(self):
        return len(self._function_store) > 0

    def to_js_snippet(self):
        return '\n'.join([
            self.function_snippet,
            self._options_snippet
        ])


class FunctionTranslator(TranslatorMixin):
    """A translator for function,a FunctionStore object will be generated.
    """

    def __init__(self):
        self._shared_function_snippet = FunctionStore()

        # Tmp Data for a render process
        self._func_store = {}  # {<name>:<func>}
        self._replace_items = []

    def reset(self):
        self._func_store = {}
        self._replace_items = []

    def feed(self, func, name=None, reference=False):
        name = name or func.__name__
        self._func_store.update({name: func})
        if reference:
            ref_str = FunctionTranslator.encode_function(
                func=None,
                func_name=name
            )
            replaced_str = '"{}"'.format(ref_str)
            self._replace_items.append((replaced_str, name))
            return ref_str

    def translate(self):
        fs = FunctionStore()
        for name, func in self._func_store.items():
            if name in self._shared_function_snippet:
                snippet = self._shared_function_snippet[name]
            else:
                snippet = TranslatorCompatAPI.translate_function(func)
                self._shared_function_snippet.update({name: snippet})
            fs.update({name: snippet})
        return fs

    def handle_options(self, options_snippet):
        for src, dest in self._replace_items:
            options_snippet = options_snippet.replace(src, dest)
        return options_snippet

    @staticmethod
    def encode_function(func, func_name=None):
        if func:
            func_name = func.__name__
        else:
            func_name = func_name
        return '-=>{}<=-'.format(func_name)


class MyJSONEncoder(json.JSONEncoder):
    """My custom JsonEncoder.
    1. Support datetime/date/numpy.ndarray object
    2. Support Function object
    3. My Json Encoder Protocol: __json__
    """

    def __init__(self, *args, **kwargs):
        """
        Value choices of function_encoder
        1. False / None : disable encode function
        2. True : encode function to the default value
        3. Callable : encode function to a custom value
        """
        self._function_encoder = kwargs.pop('function_encoder', False)
        super(MyJSONEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, types.FunctionType) and self._function_encoder:
            if callable(self._function_encoder):
                return self._function_encoder(obj)
            else:
                # self._function_encoder = True
                return FunctionTranslator.encode_function(obj)

        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        # Pandas and Numpy lists
        if obj.__class__.__name__ == 'ndarray':
            try:
                return obj.astype(float).tolist()
            except ValueError:
                try:
                    return obj.astype(str).tolist()
                except ValueError:
                    pass

        if hasattr(obj, '__json__'):
            return obj.__json__()
        return super(MyJSONEncoder, self).default(obj)


class EChartsTranslator(TranslatorMixin):
    def __init__(self):
        self.json_encoder = MyJSONEncoder(
            indent=4,
            function_encoder=self._feed_func_in_options
        )
        self._function_translator = FunctionTranslator()
        self._cache = {}

    def reset(self):
        self._function_translator.reset()
        self._cache = {}

    def _feed_func_in_options(self, func):
        return self._function_translator.feed(func, reference=True)

    # ------ Public API - Translator -----

    def feed_event(self, func, name=None):
        """Add a event function
        :param func: Event function object
        :param name: The name of function
        :return: None
        """
        return self._function_translator.feed(func, name=name, reference=False)

    def feed_options(self, options):
        """Add options dict
        :param options: A dictionary for options
        :return:
        """
        self._cache['options'] = options
        return self

    def translate(self):
        """Translate a options,a TranslateResult object is returned
        :return: a TranslateResult
        """
        option_snippet = self.json_encoder.encode(self._cache['options'])
        function_store = self._function_translator.translate()
        option_snippet = self._function_translator.handle_options(
            option_snippet)
        return TranslateResult(
            options=self._cache['options'],
            options_snippet=option_snippet,
            function_store=function_store
        )

    # ------ Tools ------

    @staticmethod
    def dumps(obj, function_encoder=False, **kwargs):
        """A simple wrapper for json.dumps
        :param obj:
        :param function_encoder:
        :param kwargs:
        :return:
        """
        encoder = MyJSONEncoder(
            function_encoder=function_encoder,
            **kwargs
        )
        return encoder.encode(obj)