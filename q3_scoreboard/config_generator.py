from jinja2 import Template
import random

config_template = Template("""
set bot_minplayers {{bot_minplayers}}
set sv_maxclients {{sv_maxclients}}

fraglimit {{fraglimit}}
cl_allowDownload 1
sv_allowdownload 1
sv_pure 0

{% for map in maps[:-1] %}
set d{{loop.index}} "map {{map}} ; set nextmap vstr d{{loop.index + 1}}" {% endfor %}
set d{{maps|length}} "map {{maps[-1]}} ; set nextmap vstr d1"

vstr d1
""")


def create_cfg_file(out_location, maps, **kwargs):
    cfg_str = create_cfg_str(maps, **kwargs)
    with open(out_location, "w") as f:
        f.write(cfg_str)


def create_cfg_str(maps, fraglimit=20, sv_maxclients=8, bot_minplayers=4,
               randomize=False):
    if randomize:
        random.shuffle(maps)

    cfg = config_template.render(maps=maps, fraglimit=fraglimit,
                                 bot_minplayers=bot_minplayers,
                                 sv_maxclients=sv_maxclients)
    return cfg
