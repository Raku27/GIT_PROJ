# Official Python 3.13.18 multi-platform image; update digest deliberately.
ARG PYTHON_BASE=python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
FROM ${PYTHON_BASE} AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp
WORKDIR /workspace
RUN groupadd --gid 10001 runner \
    && useradd --uid 10001 --gid runner --no-create-home --home-dir /tmp runner \
    && mkdir -p /opt/project-runner /reports \
    && chown 10001:10001 /reports
COPY 03-engineering-pipeline-agent/runner/ /opt/project-runner/runner/
COPY 03-engineering-pipeline-agent/run_pipeline.py /opt/project-runner/run_pipeline.py
USER 10001:10001
ENTRYPOINT ["python", "/opt/project-runner/run_pipeline.py", "--workspace", "/workspace", "--output-dir", "/reports"]
CMD ["--help"]

# Runnable demonstration: common runner + locked Matching API environment and source.
FROM runner AS matching
USER 0:0
COPY 02-matching-project/requirements-lock.txt /tmp/matching-requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/matching-requirements.txt \
    && python -m pip check \
    && rm /tmp/matching-requirements.txt
COPY 02-matching-project/ /workspace/02-matching-project/
COPY 03-engineering-pipeline-agent/ /workspace/03-engineering-pipeline-agent/
ENV OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    RUFF_CACHE_DIR=/tmp/ruff-cache \
    COVERAGE_FILE=/tmp/matching.coverage \
    PYTEST_ADDOPTS="-o cache_dir=/tmp/pytest-cache"
USER 10001:10001
CMD ["--config", "/workspace/03-engineering-pipeline-agent/configs/matching.json"]
