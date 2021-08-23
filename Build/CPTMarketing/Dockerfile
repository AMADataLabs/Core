# Build Example:
#     docker build \
#     -t cpt-marketing \
#     -f ./Build/CPTMarketing/Dockerfile \
#     --build-arg template_vars='eft_username=user,eft_password=pwd,minio_access_key=accs,minio_secret_access_key=scrt' \
#     ./
# Run Example:
#     docker run -e DOTENV_PATH=valid.env -ti cpt-marketing python task.py

FROM python:3.9.5
ENV CLASSPATH=/CPTMarketing
ENV PYTHONPATH=/CPTMarketing:/CPTMarketing/site-packages
WORKDIR /CPTMarketing

COPY ./Build/CPTMarketing/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/CPTMarketing ./Build/CPTMarketing
COPY ./Source/Python/datalabs ./Source/Python/datalabs

ARG template_vars
COPY ./Build/CPTMarketing/?*.env ./

RUN find ./ -name "*.env" -exec \
    ./Script/render-template \
    --template {} \
    --file {} \
    --vars pythonpath=/CPTMarketing,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ CPTMarketing


RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source