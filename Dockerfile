FROM gurobi/python:13.0.0_3.13
RUN apt-get update -y && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

# Install frontend dependencies and build Angular app for production
# WORKDIR /workspaces/energy_optimizer/app
# RUN ls
#RUN npm install && npm run build --configuration=production

# Return to backend context
#WORKDIR /workspaces/energy_optimizer
# RUN pip install debugpy

