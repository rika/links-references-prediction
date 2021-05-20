FROM gcr.io/spark-operator/spark-py:v3.1.1

USER root:root
ARG WORKDIR=/workspace
WORKDIR $WORKDIR

# Installing dependencies
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

COPY src src
ENV PYTHONPATH "${PYTHONPATH}:$WORKDIR/src"
ENV PATH "${PATH}:${SPARK_HOME}/bin"

COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["/usr/bin/entrypoint.sh"]