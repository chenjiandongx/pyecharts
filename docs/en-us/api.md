# API

This document describes the public API for *pyecharts* library and it will be read by developers.

## Charts Classes

Charts classes is the core component of this library.Each charts class represents the one kind of chart in [Echarts](http://echarts.baidu.com/) .

This lists the inherit tree for these charts classes.

- pyecharts.base.Base
  - pyecharts.chart.Chart
    - pyecharts.charts.foo_chart.FOO_CHART
  - pyecharts.custom.grid.Grid
  - pyecharts.custom.overlap.Overlap
  - pyecharts.custom.timeline.Timeline
- pyecharts.custom.page.Page

### Properties

This table list properties for these chart classes.

| Properites/Charts | Base | Chart/FOO_CHART | Grid | Overlap | Timeline | Page |
| ----------------- | ---- | --------------- | ---- | ------- | -------- | ---- |
| chart_id          | ✓    | ✓               | ✓    | ✓       | ✓        |      |
| width             | ✓    | ✓               | ✓    | ✓       | ✓        |      |
| heigth            | ✓    | ✓               | ✓    | ✓       | ✓        |      |
| options           | ✓    | ✓               | ✓    | ✓       | ✓        |      |
| js_dependencies   | ✓    | ✓               | ✓    | ✓       | ✓        | ✓    |
| chart             |      |                 |      |         |          |      |
| charts            |      |                 |      |         |          | ✓    |

**chart_id**

Data type:str.The identifier string for a chart. E.g.`'d2d9dcc4e28247518186c0882d356ba8'` 。

**width**

Data type:number.The width(px) of div container for a chart.

**height**

Data type:number.The height(px) of div container for a chart.

**options**

Data type:dict.The config options for a chart。Each chart has its own format and value.Please see more detail at ECharts document。

**js_dependencies**

Data type:set.The js filename collections for a chart's dependencies.Every element do not contain the filename extension(.js).E.g `{'echarts.min', 'fujian'}` 。

**chart**

The origin chart object in some composite charts.It can be a instance of the subclass of `pyecharts.base.Base` .

This property is available in the following classes:

- `pyecharts.custom.grid.Grid`
- `pyecharts.custom.overlap.Overlap`
- `pyecharts.custom.timeline.Timeline`

**charts**

The origin chart  list in the class `pyecharts.custom.page.Page` .Each element can be a instance of the subclass of `pyecharts.base.Base` .

### Methods

**add(self)**

Add options and data to a chart.See the source code for more detail.

| Chart Class | Function Sign                            |
| ----------- | ---------------------------------------- |
| Base        | `add(self, **echarts_options)`           |
| Grid        | `add(self, grid_width=None, grid_height=None, grid_top=None, grid_bottom=None, grid_left=None, grid_right=None)` |
| Overlap     | `add(self, chart, xaix_index=0, yaix_index=0, id_add_xaxis=False, is_add_yaxis=False)` |
| Timeline    | `add(self, chart, time_point)`           |
| Page        | `add(self, achart_or_charts)`            |

**get_js_dependencies(self)**

Gert the javascript dependencies of a chart.

**render(self, path='render.html')**

Render to a HTML page.

**render_embed(self)**

Render javascript code fragment including options.

**show_config(self)**

Print the options using `pprint` .

## Data Hanlder Methods

These methods are tool methods for data handlers.

**cast**

`pyecharts.base.Base.cast(seq)`

Class method for formating and converting data.It can convert your origin data to the corresponding data for pyecharts library.

Example:

```python
o_data = [('A', '34'), ('B', '45'), ('C', '12')]
x, y = Base.cast(o_data)
print(x) # ['A', 'B', 'C']
print(y) # ['34', '45', '12']
```

**json_dumps**

`pyecharts.base.json_dumps(data, indent=0)`

Convert *data* to json string, and add encoding for some specified data type:

- Convert Datetime and Time objects to ISO8601 format string.
- Cast numpy arrays. See the document of  [astype](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html) and [tolist](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.tolist.html) .

## Chart Rendering

**JINJA2_ENV**

`pyecharts.templates.JINJA2_ENV`

Data type `jinja2.Environment`。pyecharts provides a build-in environment object for rendering using Jinja2 engine。

- This environment  use *pyecharts/templates* as its base directory to store HTML and  javascript files.