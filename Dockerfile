FROM condaforge/miniforge3:24.11.3-2
WORKDIR /app

# ENV
ENV CONDA_ENV_NAME=cTENOR
ENV PATH=/opt/conda/envs/$CONDA_ENV_NAME/bin:$PATH

# conda environment
COPY environment.yml /app/
RUN mamba env create -f environment.yml

# Clone apps and settings
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/LiLabAtVT/DeepTE.git && \
    git clone https://github.com/kim2039/cTENOR.git && \
    echo "/app/DeepTE/" > /app/cTENOR/cTENOR_configure && \
    echo "/opt/conda/envs/$CONDA_ENV_NAME/bin/transposon_classifier_RFSB" >> /app/cTENOR/cTENOR_configure

WORKDIR /app/cTENOR
RUN echo "source activate $CONDA_ENV_NAME" >> /root/.bashrc
CMD ["/bin/bash"]