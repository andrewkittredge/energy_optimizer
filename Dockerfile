FROM gurobi/python:13.0.0_3.13
RUN apt-get update -y && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install pyomo notebook black pint
