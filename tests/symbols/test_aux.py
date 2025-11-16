from mead.symbols import Auxiliary


def test_auxiliary_just_compute_formula():
    aux = Auxiliary("birth rate", formula=lambda: 0.12)
    assert aux.compute() == 0.12
