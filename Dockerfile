FROM ubuntu:focal 
#nestybox/ubuntu-bionic-docker:latest 
#ubuntu-bionic-systemd-docker:latest

#ENV LC_ALL=en_US.UTF-8 \
#    LANG=en_US.UTF-8 \
#    LANGUAGE=en_US.UTF-8 
ENV SHELL=/bin/bash \
    PATH=/srv/conda/bin:$PATH

ENV NB_USER=jovyan \
    NB_UID=1001 \
    NB_GID=101 
    
ENV USER=${NB_USER} \ 
    HOME=/home/${NB_USER}
    
RUN groupadd --gid ${NB_GID} ${NB_USER} && useradd --comment "Default user" --create-home --gid ${NB_GID} --no-log-init --shell /bin/bash --uid ${NB_UID} ${NB_USER}

RUN usermod -aG sudo jovyan

RUN apt-get -qq update && apt-get -qq install --yes apt-utils 

RUN apt-get -qq update && apt-get -qq install --yes --no-install-recommends wget unzip locales > /dev/null && apt-get -qq purge && apt-get -qq clean && rm -rf /var/lib/apt/lists/*

RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen &&  echo "LANG=en_US.UTF-8" > /etc/locale.conf &&  locale-gen en_US.UTF-8

ENV APP_BASE=/srv 

ENV CONDA_DIR=${APP_BASE}/conda 
    
ENV NB_PYTHON_PREFIX=${CONDA_DIR}/envs/env_wps3 

ENV KERNEL_PYTHON_PREFIX=${NB_PYTHON_PREFIX} \
    PATH=${NB_PYTHON_PREFIX}/bin:${CONDA_DIR}/bin:${NPM_DIR}/bin:${PATH}

COPY .docker/activate-conda.sh /etc/profile.d/activate-conda.sh

COPY environment.yml /tmp/environment.yml

COPY .docker/install-miniforge.bash /tmp/install-miniforge.bash

# miniforge
RUN bash /tmp/install-miniforge.bash && rm /tmp/install-miniforge.bash /tmp/environment.yml

COPY --chown=1000:100 . ${HOME}

RUN cd ${HOME} && /srv/conda/envs/env_wps3/bin/python setup.py install

RUN echo '195.201.250.29  ades-dev.eoepca.terradue.com' >> /etc/hosts

USER ${NB_USER}

WORKDIR ${HOME}



