##########
# Frontend build stage: compile Angular app once during image build
##########
FROM node:20-slim AS frontend-build
WORKDIR /frontend

# Only copy what the Angular build needs (skip node_modules)
COPY app/package*.json app/angular.json app/tsconfig*.json ./app/
COPY app/src ./app/src
COPY app/public ./app/public

RUN cd app && npm ci && npm run build --configuration=production

##########
# Runtime stage: Python + Gurobi with built static assets
##########
FROM gurobi/python:13.0.0_3.13
WORKDIR /opt/energy_optimizer

# Python dependencies first for better layer caching
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api ./api
COPY scripts ./scripts


# Bring in the built Angular bundle expected by api/app.py
COPY --from=frontend-build /frontend/app/dist ./app/dist

EXPOSE 5000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "5000"]

