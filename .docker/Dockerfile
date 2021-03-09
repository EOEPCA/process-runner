FROM ubuntu:focal 

ENV SHELL=/bin/bash \
    PATH=/srv/conda/bin:$PATH \
    NB_USER=jovyan \
    NB_UID=1001 \
    NB_GID=101 \
    APP_BASE=/srv 
    
ENV USER=${NB_USER} \ 
    HOME=/home/${NB_USER} \
    CONDA_DIR=${APP_BASE}/conda
    
RUN groupadd --gid ${NB_GID} ${NB_USER} && useradd --comment "Default user" --create-home --gid ${NB_GID} --no-log-init --shell /bin/bash --uid ${NB_UID} ${NB_USER}

RUN usermod -aG sudo jovyan

RUN apt-get -qq update && apt-get -qq install --yes apt-utils           && \
    apt-get -qq update && apt-get -qq install --yes \
    --no-install-recommends wget unzip locales > /dev/null              && \
    apt-get -qq purge                                                   && \
    apt-get -qq clean && rm -rf /var/lib/apt/lists/*                    && \
    echo "LC_ALL=en_US.UTF-8" >> /etc/environment                       && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen                         && \
    echo "LANG=en_US.UTF-8" > /etc/locale.conf                          && \
    locale-gen en_US.UTF-8
    
ENV NB_PYTHON_PREFIX=${CONDA_DIR}/envs/env_process \
    KERNEL_PYTHON_PREFIX=${NB_PYTHON_PREFIX} \
    PATH=${NB_PYTHON_PREFIX}/bin:${CONDA_DIR}/bin:${NPM_DIR}/bin:${PATH}

COPY .docker/activate-conda.sh /etc/profile.d/activate-conda.sh

COPY .docker/install-miniforge.bash /tmp/install-miniforge.bash

# miniforge
RUN bash /tmp/install-miniforge.bash && rm /tmp/install-miniforge.bash 

ADD environment.yml /tmp/environment.yml

RUN mamba env create -p ${NB_PYTHON_PREFIX} -f /tmp/environment.yml                                                                 && \
    mamba clean --all -f -y

COPY --chown=1000:100 . ${HOME}

RUN cd ${HOME} && /srv/conda/envs/env_process/bin/python setup.py install

RUN echo '195.201.250.29  ades-dev.eoepca.terradue.com' >> /etc/hosts

USER ${NB_USER}

WORKDIR ${HOME}



