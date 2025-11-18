FROM gurobi/python:latest
RUN apt-get update -y && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install pyomo notebook
