from importlib.machinery import PathFinder

import functools
import sys

memoize = functools.lru_cache()

class ProfilerError(Exception):
    pass


@memoize
def make_loader_wrapper_class(loader_type):
    class ProfilerLoaderWrapper(loader_type):
        def __init__(self, base_loader):
            self.base_loader = base_loader


        def __getattr__(self, key):
            return getattr(self.base_loader, key)


        def exec_module(self, module):
            out = self.base_loader.exec_module(module)

            for listener in post_module_exec_listeners:
                listener(module)

            return out

    return ProfilerLoaderWrapper


def wrap_loader(loader):
    cls = make_loader_wrapper_class(type(loader))
    return cls(loader)


class ProfilerPathFinder(PathFinder):
    def find_spec(fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)

        if spec:
            spec.loader = wrap_loader(spec.loader)

        return spec


post_module_exec_listeners = set()

def register_post_exec_listener(listener):
    register_import_hooks()
    post_module_exec_listeners.add(listener)


@memoize
def register_import_hooks():
    sys.meta_path.insert(0, ProfilerPathFinder)


@memoize
class ProfilerContext(object):
    def __init__(self, config_path=None):
        self.__set_config_path(config_path)

        self.enter_count = 0

        if self.get_config():
            register_post_exec_listener(self.try_patching)


    def __set_config_path(self, path):
        from pathlib import Path

        if path is not None:
            path = Path(path)
        else:
            import os

            path = os.environ.get('PROFILER_CONFIG_PATH', './profiler_config.json')
            path = Path(path)

        self.config_path = path.absolute()


    @memoize
    def get_config(self):
        if not self.config_path.exists():
            return { }

        import json

        with open(str(self.config_path), 'r') as fd:
            return json.load(fd)


    @memoize
    def line_profiler(self):
        import line_profiler
        return line_profiler.LineProfiler()


    @memoize
    def lp_targets(self):
        lp_config = self.get_config().get('line_profiler')

        if not lp_config:
            return { }

        return { target : False for target in lp_config }


    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


    def __enter__(self):
        register_import_hooks()
        self.try_patching()

        self.enter_count += 1

        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.enter_count -= 1

        if self.enter_count == 0:
            self.check_patching()
            self.save_profiling_data()


    def try_patching(self, module=None):
        targets = self.lp_targets()
        modules = sys.modules

        # TODO: Don't iterate over target set every time since this happens on
        # every module import.  This function can be implicitly called recursively
        # due to being part of the import hooks.

        for target in targets:
            if targets[target]:
                continue

            module_name, _, func_name = target.rpartition('.')

            if not func_name:
                raise ProfilerError('invalid line_profiler target in file',
                    { 'target' : target, 'path' : str(self.config_path) })

            try:
                module = modules[module_name]
                func = getattr(module, func_name)
                setattr(module, func_name, self.line_profiler()(func))

                targets[target] = True
                continue
            except (AttributeError, KeyError):
                pass


            module_name, _, class_name = module_name.rpartition('.')

            try:
                module = modules[module_name]
                cls = getattr(module, class_name)
                func = getattr(cls, func_name)
                setattr(cls, func_name, self.line_profiler()(func))

                targets[target] = True
                continue
            except (AttributeError, KeyError):
                pass


    def check_patching(self):
        if self.lp_targets():
            assert all(self.lp_targets().values())


    def save_profiling_data(self):
        if not self.lp_targets():
            return

        #TODO: Counter needs to tied to enter_count hitting 0.  The line_profiler
        # needs to be reset after each time it does.

        counter = 0
        suffix = '.{}.lprof'.format(counter)

        output_path = self.config_path.with_suffix(suffix)
        self.line_profiler().dump_stats(str(output_path))


# TODO: At least one ProfilerContext needs to be instantiated to ensure
# ProfilerPathFinder is registered and post_module_exec hooks run, but if other
# other contexts are instantiated after symbols they're interested in have been
# imported they'll silently miss profiling.

ProfilerContext()
