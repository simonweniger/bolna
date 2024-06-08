FROM python:3.10.13-slim

WORKDIR /app

# Install libgomp1
RUN apt-get update && apt-get install -y libgomp1

COPY ./requirements.txt /app
COPY ./local_setup/telephony_server/twilio_api_server.py /app
COPY ./local_setup/agent_config.json /app/local_setup/agent_config.json
COPY ./bolna /app/bolna

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "twilio_api_server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]