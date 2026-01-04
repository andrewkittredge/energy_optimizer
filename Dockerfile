FROM gurobi/python:13.0.0_3.13
#RUN apt-get update -y && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*
#RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY scripts ./scripts
EXPOSE 5000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "5000"]