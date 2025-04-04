import pytest
import treeli


def full_spec(arg, /, arg_kwarg, darg_kwarg="default-darg_kwarg", *vargs, kwarg, dkwarg="default-dkwarg", **kwargs):
    assert "kwargs" in locals()
    return locals()


@pytest.mark.parametrize(
    "cli_params, expected",
    [
        (
            ["v1", "v2", "kwarg=v4", "v3", "kwargs=v5"],
            (("v1", "v2", "v3"), {"kwarg": "v4", "kwargs": "v5"})
        )
    ]
)
def test_cli_args_kwargs(cli_params, expected):
    assert treeli.cli_args_kwargs(cli_params) == expected



@pytest.mark.parametrize(
    "cli_params, expected",
    [
        (
            ["arg", "arg_kwarg", "kwarg=kwarg"],
            (
                ("arg", "arg_kwarg", "default-darg_kwarg"),
                {"dkwarg": "default-dkwarg", "kwarg": "kwarg"}
            )
        ),
        (
            ["arg", "arg_kwarg=arg_kwarg", "kwarg=kwarg"],
            (
                ("arg", "arg_kwarg", "default-darg_kwarg"),
                {"dkwarg": "default-dkwarg", "kwarg": "kwarg"}
            )
        ),
        (
            ["arg", "arg_kwarg", "darg_kwarg", "vargs", "kwarg=kwarg"],
            (
                ("arg", "arg_kwarg", "darg_kwarg", "vargs"),
                {"kwarg": "kwarg", "dkwarg": "default-dkwarg"}
            )
        ),
        (
            ["arg", "arg_kwarg=arg_kwarg", "darg_kwarg=darg_kwarg", "kwarg=kwarg", "dkwarg=dkwarg", "kwargs=kwargs"],
            (
                ("arg", "arg_kwarg", "darg_kwarg"),
                {"dkwarg": "dkwarg", "kwarg": "kwarg", "kwargs": "kwargs"}
            )
        )
    ]
)
def test_call_params_spec(cli_params, expected):
    assert treeli.call_params(full_spec, cli_params) == expected


def typed_param(num: int):
    assert isinstance(num, int)


def test_call_params_type():
    assert treeli.call_params(typed_param, ["1"]) == ((1,), {})
    assert treeli.call_params(typed_param, ["num=1"]) == ((1,), {})


def test_parse_obj():
    val = treeli.parse_obj(full_spec)
    breakpoint()
