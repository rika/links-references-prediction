FROM gcr.io/spark-operator/spark-py:v3.1.1

USER root
ARG WORKDIR=/workspace
WORKDIR $WORKDIR

# Installing dependencies
COPY requirements.txt requirements.txt
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

ENV PATH "${PATH}:${SPARK_HOME}/bin"

COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh

COPY src src
ENV PYTHONPATH "${PYTHONPATH}:$WORKDIR/src"

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
