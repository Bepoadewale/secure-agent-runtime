FROM python:3.12-alpine
RUN addgroup -S sandbox && adduser -S -G sandbox -u 65532 sandbox
USER 65532:65532
WORKDIR /workspace
ENTRYPOINT ["/bin/sh", "-lc"]
