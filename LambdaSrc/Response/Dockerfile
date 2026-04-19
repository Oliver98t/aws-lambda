# Lambda Python 3.12 container for SpeechToText
FROM public.ecr.aws/lambda/python:3.12


# Copy function code and requirements to $LAMBDA_TASK_ROOT
COPY Index.py requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies into $LAMBDA_TASK_ROOT
RUN pip install --upgrade pip \
    && pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}"

# (Optional) If you have other source files, copy them as well
# COPY other_module.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (file.function)
CMD ["Index.handler"]
