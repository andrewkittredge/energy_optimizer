FROM gurobi/python:latest
RUN pip install pyomo notebook

CMD python -m notebook --allow-root --ip 0.0.0.0 --no-browser