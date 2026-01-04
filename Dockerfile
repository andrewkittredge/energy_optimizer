# build stage
FROM node:lts-alpine AS build-stage
WORKDIR /app
COPY app .
RUN npm install
RUN npm run build


FROM gurobi/python:13.0.0_3.13 AS production-stage

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY scripts ./scripts
COPY --from=build-stage /app/dist /app/dist


EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]