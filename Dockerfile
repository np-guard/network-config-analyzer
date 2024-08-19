#
# Copyright 2020- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

# Using python:3.9-slim
FROM python@sha256:e3d5b6f95ce66923b5e48a06ee5755abb097de96a8617c3f2f7d431d48e63d35

COPY requirements.txt /nca/
RUN python -m pip install -U pip wheel setuptools && pip install -r /nca/requirements.txt

RUN apt-get update && apt-get install -y curl graphviz && rm -rf /var/lib/apt/lists

RUN curl -L "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" --output /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 && chmod 700 get_helm.sh \
    && ./get_helm.sh

RUN curl -L https://github.com/projectcalico/calicoctl/releases/download/v3.3.1/calicoctl --output /usr/local/bin/calicoctl \
    && chmod +x /usr/local/bin/calicoctl

RUN apt-get purge curl -y && apt-get autoremove -y

COPY nca/ /nca/

USER 9000

WORKDIR "/"
ENTRYPOINT ["python", "-m", "nca"]
