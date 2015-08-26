import game_vars
import threading
import pluginmanager
import itertools


class StageMachine(object):
    def __init__(self, config, transport):
        """
        'server':(ip, port, password)
        'stages': [],
        'plugins':[],
        'config':{
            'stages':{
                'stagename':{
                    'optname':value,
                    'plugin_config':{
                        'pluginname':{
                        'optname':value
                        }
                    }
                }
            }
            'plugins':{
                'pluginname':{
                    'optname':value
                }
            }
        }
        Private configs will everytime overwrite global configs"""

        self.lock = threading.Lock()
        self._game_vars = game_vars.GameVars()
        self._transport = transport
        self._pluginmanager = pluginmanager.Pluginmanager(self.transport, self._game_vars)
        self._config = config
        self._current_stage_index = 0
        _current_stage_module = __import__('stages.' + self._config['stages'][self._current_stage_index].split('.')[0])
        self._current_stage = getattr(_current_stage_module, self._config['stage'][self._current_stage_index].split('.')[1])
        for plugin in self._current_stage.PLUGINS:
            self._pluginmanager.load_plugin(plugin, self._pluginconfig_dep(plugin))
        self._current_stage.start(**self._config['config']['stages'][self._config['stages'][self._current_stage_index]])

    def _pluginconfig_dep(self, plugin):
        pluginconfig = {}
        if plugin in self._config['config']['plugins']:
            pluginconfig.update(self._config['config']['plugins'][plugin])
        if plugin in self._config['config']['stages'][self._config['stages'][self._current_stage_index]['plugin_config']]:
            pluginconfig.update(self._config['config']['stages'][self._config['stages'][self._current_stage_index]]['plugin_config'][plugin])
        return pluginconfig if pluginconfig else None

    def tick(self, event):
            with self.lock:
                self._pluginmanager._eventhandler.deploy_event(event)
                if self._current_stage.finished:
                    self._load_next_stage()

    def _load_next_stage(self):
        old_plugins = self._current_stage.PLUGINS
        self._current_stage_index += 1
        _current_stage_module = __import__('stages.' + self._config['stages'][self._current_stage_index].split('.')[0])
        self._current_stage = getattr(_current_stage_module, self._config['stage'][self._current_stage_index].split('.')[1])
        for plugin in old_plugins:
            if plugin in self._current_stage.PLUGINS:
                self._pluginmanager.reload_plugin(self._pluginconfig_dep(plugin))
            else:
                self._pluginmanager.unload_plugin(plugin)
        for plugin in self._current_stage.PLUGINS:
            if plugin not in old_plugins:
                self._eventhandler.load_plugin(plugin, self._pluginconfig_dep(plugin))
        if self._current_stage.finished:
            self._load_next_stage()

    @property
    def game_vars(self):
        with self.lock:
            return self._game_vars.__dict__.copy()
