import inspect
import functools
import sys


def cli_args_kwargs(argv=None):
    argv = argv or sys.argv[1:]

    args = []
    kwargs = {}
    for word in argv:
        if "=" in word:
            name, value = word.split("=", 1)
            kwargs[name] = value
        else:
            args.append(word)
    return tuple(args), kwargs


type_cast_registry = {}
def register_type(new_type, cast_func):
    global type_cast_registry
    type_cast_registry[new_type] = cast_func


def cast_types(ba):
    parameters = ba.signature.parameters
    arguments = ba.arguments
    updated = {}
    for name, value in arguments.items():
        ptype = parameters[name].annotation
        if ptype is inspect.Parameter.empty or ptype is str:
            continue

        updated[name] = type_cast_registry.get(ptype, ptype)(value)
    arguments.update(updated)
    return ba


def call_params(func, argv):
    assert callable(func)
    args, kwargs = cli_args_kwargs(argv)
    sig = inspect.signature(func)
    ba = sig.bind(*args, **kwargs)
    ba.apply_defaults()
    cast_types(ba)
    return ba.args, ba.kwargs


def apply_argv(func, argv=None):
    args, kwargs = call_params(func, *cli_args_kwargs(argv))
    return func(*args, **kwargs)


class CLI:
    def __init__(self, func, name=None):
        self.__name__ = func.__name__ if name is None else name


def parse_func(func, name=None):
    assert callable(func)

    name = func.__name__ if name is None else name
    sig = inspect.signature(func)
    return {name: str(sig)}

def parse_class(klass, name=None):
    name = func.__name__ if name is None else name
    inst = klass()
    inst.__name__ = name

    graph = {}
    if callable(inst):
        graph[name] = inst

    default_config = {}
    for name in dir(klass):
        value = getattr(inst, name)
        if name.startswith("_"):
            continue

        if isinstance(value, type):
            graph[name] = parse_class(value)
        elif callable(value):
            graph[name] = parse_func(value)
        else:
            defualt_config[name] = value

    return graph


def parse_obj(obj, name=None):
    if isinstance(obj, type):
        return parse_class(obj, name)

    elif callable(obj):
        return parse_func(obj, name)

def create_cli_graph(cli_obj):
    if isinstance(cli_obj, (tuple, list)):
        return functools.reduce(dict.__or__, map(create_cli_graph, cli_obj))
    elif isinstance(cli_obj, dict):
        return functools.reduce(dict.__or__, create_cli_graph(v, n) for n, v in cli_obj.items())
    else:
        return parse_obj(cli_obj)


def create_graph(stages, stop_stage, flags, overrides):
    graph = {}
    new_stages = {}
    vist = [stages[stop_stage]]
    while vist:
        stage = vist.pop()
        params = func_params(stage)
        stage_name = stage.__name__

        user_defined = func_kwargs_from_flags(stage, flags)
        for dep_arg in params.args:
            if override_value := overrides.get(dep_arg):
                user_defined[dep_arg] = override_value

        stage = partial(stage, **user_defined)
        params = func_params(stage)
        dep_stage_names = [arg for arg in chain(params.args, params.kwargs) if arg not in params.defaults]
        missing_args = set(dep_stage_names) - set(stages)
        assert not missing_args, f"Missing argument for stage {stage_name}: {missing_args}"

        new_stages[stage_name] = stage
        graph[stage_name] = dep_stage_names
        vist.extend(stages[dep_stage_name] for dep_stage_name in dep_stage_names if dep_stage_name not in graph)
    return graph, new_stages


def run(cli_obj, argv=None):
    parse_signature(cli_obj)
