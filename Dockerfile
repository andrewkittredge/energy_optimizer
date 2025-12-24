FROM gurobi/python:13.0.0_3.13
RUN apt-get update -y && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN pip install pyomo notebook black pint ipykernel uvicorn
npm install -g @angular/cli
