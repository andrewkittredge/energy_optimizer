import pyomo.environ as pyo
model = pyo.ConcreteModel()

model.llamas = pyo.Var(within=pyo.NonNegativeReals)
model.goats = pyo.Var(within=pyo.NonNegativeReals)

model.maximizeProfits = pyo.Objective(expr=200 * model.llamas  + 300 * model.goats, sense=pyo.maximize)

model.LaborConstraint = pyo.Constraint(expr = 3 * model.llamas + 2 * model.goats <= 100)
model.MedialConstraint = pyo.Constraint(expr=2* model.llamas + 4 * model.goats <= 120)
model.LandConstraint  = pyo.Constraint(expr = model.llamas + model.goats <= 45)

optimizer = pyo.SolverFactory('glpk')
optimizer.solve(model)
print(model.display())