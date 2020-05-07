FROM python:3.8

WORKDIR /app

RUN pip install requests chessterm-sdk

COPY config.ini luqi.py luqi.txt luqi_env.py zhuobie.txt /app/

CMD ["python", "luqi_env.py"]
