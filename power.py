import pyomo.environ as pyo
model = pyo.ConcreteModel()

model.x = pyo.Var([1,2], domain=pyo.PositiveReals)

model.OBJ = pyo.Objective(expr = model.x[1]  - model.x[2])

model.Constraint1 = pyo.Constraint(expr = model.x[1] + model.x[2] >= 10)