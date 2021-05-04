FROM aquariumbio/pfish:1.2.0

# create directories within container
# /script is where the package lives
ENV SCRIPT_DIR=/script
WORKDIR ${SCRIPT_DIR}

# copy script into container
COPY ./push_and_test/ .

# run script by default
ENTRYPOINT ["python3", "/script/push_and_test.py"]