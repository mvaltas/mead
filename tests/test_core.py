from mead.core import Constant, Element, Auxiliary, Delay
from mead.stock import Stock
import pytest

# A dummy context for testing compute methods
dummy_context = {
    'state': {'stock_val': 10, 'other_stock': 20},
    'time': 0.0,
    'history_lookup': lambda name, time_ago: 5.0 # Always returns 5.0 for simplicity
}

def test_element_compute():
    e = Element("stock_val")
    assert e.compute(dummy_context) == 10

def test_constant_compute():
    c = Constant("c", 10)
    assert c.compute(dummy_context) == 10

def test_simple_addition():
    c1 = Constant("c1", 5)
    c2 = Constant("c2", 10)
    eq = c1 + c2
    assert eq.compute(dummy_context) == 15

def test_simple_subtraction():
    c1 = Constant("c1", 10)
    c2 = Constant("c2", 3)
    eq = c1 - c2
    assert eq.compute(dummy_context) == 7

def test_simple_multiplication():
    c1 = Constant("c1", 5)
    c2 = Constant("c2", 4)
    eq = c1 * c2
    assert eq.compute(dummy_context) == 20

def test_simple_division():
    c1 = Constant("c1", 20)
    c2 = Constant("c2", 5)
    eq = c1 / c2
    assert eq.compute(dummy_context) == 4

def test_division_by_zero():
    c1 = Constant("c1", 20)
    c2 = Constant("c2", 0)
    eq = c1 / c2
    assert eq.compute(dummy_context) == 0

def test_mixed_operations_with_literals():
    c1 = Constant("c1", 10)
    # (10 * 2) + 5
    eq = (c1 * 2) + 5
    assert eq.compute(dummy_context) == 25

def test_element_in_equation():
    stock_element = Element("stock_val")
    c1 = Constant("c1", 10)
    eq = stock_element * c1
    
    # Compute with stock_val = 10
    assert eq.compute(dummy_context) == 100

def test_auxiliary_compute():
    c1 = Constant("c1", 5)
    c2 = Constant("c2", 10)
    aux_eq = c1 + c2
    aux = Auxiliary("my_aux", aux_eq)
    assert aux.compute(dummy_context) == 15

def test_auxiliary_dependencies():
    c1 = Constant("c1", 5)
    c2 = Constant("c2", 10)
    aux_eq = c1 + c2
    aux = Auxiliary("my_aux", aux_eq)
    deps = aux.dependencies # Should return [aux_eq]
    assert aux_eq in deps
    assert c1 not in deps # c1 is not a direct dependency of aux, only of aux_eq

def test_equation_dependencies_direct():
    s1 = Element("s1")
    s2 = Element("s2")
    c1 = Constant("c1", 10)
    aux = Auxiliary("aux1", s1 * c1)
    
    # complex_eq = (aux + s2) * 2
    eq1 = aux + s2
    eq2 = eq1 * 2

    # Test eq1 direct dependencies
    deps1 = eq1.dependencies
    assert aux in deps1
    assert s2 in deps1
    assert len(deps1) == 2

    # Test eq2 direct dependencies
    deps2 = eq2.dependencies
    assert eq1 in deps2 # Direct dependency is eq1
    assert len(deps2) == 1 # Only eq1 (literal 2 is excluded)

