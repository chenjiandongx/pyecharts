import os

from jinja2 import Environment

from ..commons import utils
from ..datasets import EXTRA, FILENAMES
from ..globals import CurrentConfig, NotebookType
from ..types import Any, Optional
from .display import HTML, Javascript


def write_utf8_html_file(file_name: str, html_content: str):
    with open(file_name, "w+", encoding="utf-8") as html_file:
        html_file.write(html_content)


class RenderEngine:
    def __init__(self, env: Optional[Environment] = None):
        self.env = env or CurrentConfig.GLOBAL_ENV

    @staticmethod
    def generate_js_link(chart: Any) -> Any:
        if not chart.js_host:
            chart.js_host = CurrentConfig.ONLINE_HOST
        links = []
        for dep in chart.js_dependencies.items:
            # TODO: if?
            if dep.startswith("http://api.map.baidu.com"):
                links.append(dep)
            if dep in FILENAMES:
                f, ext = FILENAMES[dep]
                links.append("{}{}.{}".format(chart.js_host, f, ext))
            else:
                for url, files in EXTRA.items():
                    if dep in files:
                        f, ext = files[dep]
                        links.append("{}{}.{}".format(url, f, ext))
                        break
        chart.dependencies = links
        return chart

    def render_chart_to_file(self, template_name: str, chart: Any, path: str, **kwargs):
        """
        Render a chart or page to local html files.

        :param chart: A Chart or Page object
        :param path: The destination file which the html code write to
        :param template_name: The name of template file.
        """
        tpl = self.env.get_template(template_name)
        html = utils.replace_placeholder(
            tpl.render(chart=self.generate_js_link(chart), **kwargs)
        )
        write_utf8_html_file(path, html)

    def render_chart_to_template(self, template_name: str, chart: Any, **kwargs) -> str:
        tpl = self.env.get_template(template_name)
        return utils.replace_placeholder(
            tpl.render(chart=self.generate_js_link(chart), **kwargs)
        )

    def render_chart_to_notebook(self, template_name: str, **kwargs) -> str:
        tpl = self.env.get_template(template_name)
        return utils.replace_placeholder(tpl.render(**kwargs))


class Render:
    def __int__(self):
        self.js_host: str = ""
        self.js_functions: utils.OrderedSet = utils.OrderedSet()
        self.js_dependencies = utils.OrderedSet()

    def _prepare_render(self):
        raise NotImplementedError

    def render_embed(self):
        raise NotImplementedError

    def _render(
        self, path: str, template_name: str, env: Optional[Environment], **kwargs
    ) -> str:
        self._prepare_render()
        RenderEngine(env).render_chart_to_file(
            template_name=template_name, chart=self, path=path, **kwargs
        )
        return os.path.abspath(path)

    def _render_embed(
        self, template_name: str, env: Optional[Environment], **kwargs
    ) -> str:
        self._prepare_render()
        return RenderEngine(env).render_chart_to_template(
            template_name=template_name, chart=self, **kwargs
        )

    def _render_notebook(self, notebook_template, lab_template):
        if CurrentConfig.NOTEBOOK_TYPE == NotebookType.JUPYTER_NOTEBOOK:
            require_config = utils.produce_require_dict(
                self.js_dependencies, self.js_host
            )
            return HTML(
                RenderEngine().render_chart_to_notebook(
                    template_name=notebook_template,
                    charts=self,
                    config_items=require_config["config_items"],
                    libraries=require_config["libraries"],
                )
            )

        if CurrentConfig.NOTEBOOK_TYPE == NotebookType.JUPYTER_LAB:
            return HTML(
                RenderEngine().render_chart_to_notebook(
                    template_name=lab_template, charts=self
                )
            )

        if CurrentConfig.NOTEBOOK_TYPE == NotebookType.NTERACT:
            return HTML(self.render_embed())

        if CurrentConfig.NOTEBOOK_TYPE == NotebookType.ZEPPELIN:
            print("%html " + self.render_embed())

    def load_javascript(self):
        scripts = []
        for dep in self.js_dependencies.items:
            f, ext = FILENAMES[dep]
            scripts.append("{}{}.{}".format(CurrentConfig.ONLINE_HOST, f, ext))
        return Javascript(lib=scripts)

    def add_js_funcs(self, *fns):
        for fn in fns:
            self.js_functions.add(fn)
        return self
