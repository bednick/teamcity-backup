FROM python:3.7-stretch AS build

COPY teamcity_backup/requirements.txt /build/requirements.txt

RUN mkdir -p /build/wheels/ && pip wheel -r /build/requirements.txt --wheel-dir /build/wheels

COPY teamcity_backup /build/src/teamcity_backup
RUN pip wheel --wheel-dir=/build/wheels --no-index --find-links=/build/wheels /build/src/teamcity_backup


#
# Production image
#
FROM python:3.7-slim-stretch

COPY --from=build /build/wheels /build/wheels
RUN ls /build/wheels
RUN pip install --find-links=/build/wheels --no-index teamcity_backup

CMD ["python", "-m", "teamcity_backup"]
