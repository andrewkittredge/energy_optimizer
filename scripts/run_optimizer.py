#!/usr/bin/env python3
"""Runnable conversion of `power.ipynb`.

Usage examples:
  python -m scripts.run_optimizer --solver gurobi
  python -m scripts.run_optimizer --solver cbc

The script preserves unit checks and the GDP disjunction transformation from the notebook.
If the requested solver is not available, the script will try to fall back to `cbc`.
"""
from __future__ import annotations

import argparse
import sys
import pyomo.environ as pyo
from pyomo.util.check_units import assert_units_consistent
from pyomo.environ import units
import pyomo.gdp as gdp
from pyomo.core import TransformationFactory


def build_model(params: dict | None = None) -> pyo.ConcreteModel:
    """Build the optimization model.

    Optional `params` dictionary can override the default constants. Supported keys:
      - peak_price
      - off_peak_price
      - battery_cost_per_kw
      - peak_consumption
      - off_peak_consumption
      - solar_installation_sizes (dict mapping size->cost)
    """
    # Defaults (from the notebook)
    defaults = {
        "peak_price": 0.5,
        "off_peak_price": 0.4,
        "battery_cost_per_kw": 0.15,
        "peak_consumption": 10,
        "off_peak_consumption": 20,
        "solar_installation_sizes": {
            3: 0.282,
            5: 0.250,
            6: 0.230,
            8: 0.210,
            10: 0.190,
            12: 0.117,
        },
    }

    if params:
        # shallow merge: override any defaults provided in params
        defaults.update(params)

    PEAK_PRICE = defaults["peak_price"]
    OFF_PEAK_PRICE = defaults["off_peak_price"]
    BATTERY_COST_PER_KW = defaults["battery_cost_per_kw"]
    PEAK_CONSUMPTION = defaults["peak_consumption"]
    OFF_PEAK_CONSUMPTION = defaults["off_peak_consumption"]

    SOLAR_INSTALLATION_SIZES = defaults["solar_installation_sizes"]

    model = pyo.ConcreteModel()

    units.load_definitions_from_strings(["USD = [currency]"])

    model.peak_load = pyo.Param(initialize=PEAK_CONSUMPTION, units=units.kWh)
    model.off_peak_load = pyo.Param(initialize=OFF_PEAK_CONSUMPTION, units=units.kWh)
    model.peak_grid_price = pyo.Param(
        initialize=PEAK_PRICE, units=units.USD / units.kWh
    )
    model.off_peak_grid_price = pyo.Param(
        initialize=OFF_PEAK_PRICE, units=units.USD / units.kWh
    )
    model.battery_cost_per_kw = pyo.Param(
        initialize=BATTERY_COST_PER_KW, units=units.USD / units.kWh
    )

    model.SOLAR_SIZES = pyo.Set(initialize=SOLAR_INSTALLATION_SIZES.keys())
    model.solar_size_flags = pyo.Var(model.SOLAR_SIZES, within=pyo.Binary)
    model.solar_capacity = pyo.Var(
        within=pyo.NonNegativeReals, units=units.kWh, bounds=(1, 100)
    )
    model.solar_cost = pyo.Var(within=pyo.NonNegativeReals, units=units.USD / units.kWh)

    model.peak_grid_consumption = pyo.Var(within=pyo.NonNegativeReals, units=units.kWh)
    model.off_peak_grid_usage = pyo.Var(within=pyo.NonNegativeReals, units=units.kWh)
    model.battery_capacity = pyo.Var(
        within=pyo.NonNegativeReals, bounds=(0, 4), units=units.kWh
    )

    model.minimize_cost = pyo.Objective(
        expr=(model.peak_grid_price * model.peak_grid_consumption)
        + (model.off_peak_grid_price * model.off_peak_grid_usage)
        + (model.solar_capacity * model.solar_cost)
        + (model.battery_cost_per_kw * model.battery_capacity),
        sense=pyo.minimize,
    )

    model.off_peak_constraint = pyo.Constraint(
        expr=model.off_peak_load <= model.off_peak_grid_usage + model.battery_capacity
    )

    model.peak_constraint = pyo.Constraint(
        expr=model.peak_load <= model.peak_grid_consumption + model.solar_capacity
    )

    def solar_cost_constraint(m):
        sum_term = sum(
            SOLAR_INSTALLATION_SIZES[i] * m.solar_size_flags[i] for i in m.SOLAR_SIZES
        )
        return m.solar_cost == sum_term

    model.solar_cost_constraint = pyo.Constraint(rule=solar_cost_constraint)

    def solar_capacity_constraint(m):
        return m.solar_capacity == sum(
            size * m.solar_size_flags[size] for size in m.SOLAR_SIZES
        )

    model.solar_capacity_constraint = pyo.Constraint(rule=solar_capacity_constraint)

    model.sos1_constraint = pyo.SOSConstraint(var=model.solar_size_flags, sos=1)

    # GDP disjuncts for battery sizing (copied from notebook)
    model.battery_capacity_disjunct = gdp.Disjunct()
    model.battery_capacity_disjunct.solar_less_than_peak = pyo.Constraint(
        expr=model.solar_capacity >= model.peak_load
    )
    model.battery_capacity_disjunct.battery_less_than_excess_solar = pyo.Constraint(
        expr=model.battery_capacity <= model.solar_capacity - model.peak_load
    )

    model.battery_capacity_Zero_disjunct = gdp.Disjunct()
    model.battery_capacity_Zero_disjunct.battery_Zero = pyo.Constraint(
        expr=model.battery_capacity == 0
    )

    model.either_or_disjunction = gdp.Disjunction(
        expr=[model.battery_capacity_disjunct, model.battery_capacity_Zero_disjunct]
    )

    # Keep unit assertions to catch mismatches during refactors
    assert_units_consistent(model.off_peak_constraint)
    assert_units_consistent(model.solar_cost_constraint)
    assert_units_consistent(model.peak_constraint)
    assert_units_consistent(model.either_or_disjunction)
    assert_units_consistent(model.minimize_cost)

    # Apply GDP transformation (same as notebook)
    TransformationFactory("gdp.bigm").apply_to(model)

    return model


def solve_model(model: pyo.ConcreteModel, solver_name: str = "gurobi") -> None:
    solver = pyo.SolverFactory(solver_name)
    if not solver.available(exception_flag=False):
        print(f"Solver '{solver_name}' not available. Trying 'cbc' fallback.")
        solver = pyo.SolverFactory("cbc")
        if not solver.available(exception_flag=False):
            print(
                "No solver available (tried requested and 'cbc'). Install a solver and try again."
            )
            sys.exit(1)

    print(f"Using solver: {solver.name}")
    results = solver.solve(model, tee=True)
    # results handling can be expanded as needed
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run energy optimizer model")
    parser.add_argument(
        "--solver", default="gurobi", help="Solver to use (default: gurobi)"
    )
    args = parser.parse_args(argv)

    model = build_model()

    try:
        solve_model(model, solver_name=args.solver)
    except (
        Exception
    ) as exc:  # noqa: BLE001 - allow general error capture for user clarity
        print("Solver run failed:", exc)
        return 2

    # Print a succinct summary like the notebook
    print(
        f"solar capacity: {model.solar_capacity.value} kW, battery capacity: {model.battery_capacity.value} kWh, "
        f"off peak grid usage: {model.off_peak_grid_usage.value} kW, peak grid consumption: {model.peak_grid_consumption.value} kW"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
