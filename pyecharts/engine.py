#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

from jinja2 import Environment, environmentfunction
from pyecharts.utils import json_dumps
from pyecharts import constants
from pyecharts.conf import DEFAULT_CONFIG


class Helpers(object):
    @staticmethod
    def merge_js_dependencies(*args):
        """Merge js dependencies to a list
        :param args:
        :return:
        """
        dependencies = []

        def _add(_x):
            if _x not in dependencies:
                dependencies.append(_x)

        for a in args:
            if hasattr(a, 'js_dependencies'):
                for d in a.js_dependencies:
                    _add(d)
            else:
                _add(a)
        return dependencies

    @staticmethod
    def get_js_file_contents(*paths):
        contents = []
        for path in paths:
            with open(path, 'rb') as f:
                c = f.read()
                contents.append(c.decode('utf8'))
        return contents

    @staticmethod
    def get_local_js_names(dependencies):
        return [
            '{}/{}.js'.format(constants.LOCAL_TEMPLATE_DIR, constants.DEFAULT_JS_LIBRARIES.get(x, x)) for x in
            dependencies
            ]


@environmentfunction
def echarts_js_dependencies(env, *args):
    """
    Render script html nodes in external link mode.
    :param env:
    :param args:
    :return:
    """
    dependencies = Helpers.merge_js_dependencies(*args)

    if DEFAULT_CONFIG.js_embed:
        js_links = Helpers.get_local_js_names(dependencies)
        contents = Helpers.get_js_file_contents(*js_links)
        return '\n'.join(['<script type="text/javascript">\n{}\n</script>'.format(c) for c in contents])
    else:
        js_links = DEFAULT_CONFIG.generate_js_link(dependencies)
        return '\n'.join(['<script type="text/javascript" src="{}"></script>'.format(j) for j in js_links])


@environmentfunction
def echarts_js_dependencies_embed(env, *args):
    """
    Render script html nodes in embed mode,Only used for local files.
    :param env:
    :param args:
    :return:
    """
    dependencies = Helpers.merge_js_dependencies(*args)
    js_links = Helpers.get_local_js_names(dependencies)
    contents = Helpers.get_js_file_contents(*js_links)
    return '\n'.join(['<script type="text/javascript">\n{}\n</script>'.format(c) for c in contents])


@environmentfunction
def echarts_container(env, chart):
    """
    Render a div html element for a chart.
    :param env:
    :param chart: A pyecharts.base.Base object
    :return:
    """

    def ex_wh(x):
        """
        Extend width/height to all values.See http://www.w3school.com.cn/cssref/pr_dim_width.asp
        :param x:
        :return:
        """
        if isinstance(x, (int, float)):
            return '{}px'.format(x)
        else:
            return x

    return '<div id="{chart_id}" style="width:{width};height:{height};"></div>'.format(
        chart_id=chart.chart_id,
        width=ex_wh(chart.width),
        height=ex_wh(chart.height)
    )


@environmentfunction
def echarts_js_content(env, *charts):
    """
    Render script html node for echarts initial code.
    :param env:
    :param chart:
    :return:
    """

    print(charts)
    contents = []
    for chart in charts:
        content_fmt = '''
        var myChart_{chart_id} = echarts.init(document.getElementById('{chart_id}'));
        var option_{chart_id} = {options};
        myChart_{chart_id}.setOption(option_{chart_id});
        '''
        js_content = content_fmt.format(
            chart_id=chart.chart_id,
            options=json_dumps(chart.options, indent=4)
        )
        contents.append(js_content)
    contents = '\n'.join(contents)
    return '<script type="text/javascript">\n{}\n</script>'.format(contents)


@environmentfunction
def echarts_js_content_wrap(env, *charts):
    """
    Render echarts initial code for a chart.
    :param env:
    :param charts:
    :return:
    """
    contents = []
    for chart in charts:
        content_fmt = '''
        var myChart_{chart_id} = echarts.init(document.getElementById('{chart_id}'));
        var option_{chart_id} = {options};
        myChart_{chart_id}.setOption(option_{chart_id});
        '''
        js_content = content_fmt.format(
            chart_id=chart.chart_id,
            options=json_dumps(chart.options, indent=4)
        )
        contents.append(js_content)
    return '\n'.join(contents)


class EchartsEnvironment(Environment):
    """Built-in jinja2 template engine for pyecharts

    """

    def __init__(self, *args, **kwargs):
        super(EchartsEnvironment, self).__init__(
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            *args,
            **kwargs)

        # Add PyEChartsConfig
        self.globals.update({
            'echarts_js_dependencies': echarts_js_dependencies,
            'echarts_js_dependencies_embed': echarts_js_dependencies_embed,
            'echarts_container': echarts_container,
            'echarts_js_content': echarts_js_content,
            'echarts_js_content_wrap': echarts_js_content_wrap
        })


def configure(jshost=None, **kwargs):
    if jshost:
        constants.CONFIGURATION['HOST'] = jshost
        DEFAULT_CONFIG.jshost = jshost