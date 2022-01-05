FROM registry.centos.org/centos:8

# pipeline dependecies
RUN yum -y install git python3 python3-flask python3-requests python3-libxml2 python3-yaml
# pipeline tests dependecies
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm; \
    yum -y install make python3-pylint diffutils
# pipeline plugins dependecies
RUN yum -y install yum-utils; \
    yum-config-manager --add-repo https://beaker-project.org/yum/beaker-client-RedHatEnterpriseLinux.repo; \
    yum-config-manager --enable beaker-client; \
    yum -y install python3-bugzilla beaker-client python3-productmd

# fetch other libraries and tools
WORKDIR /root
RUN git clone https://github.com/rhinstaller/tclib.git

# set up git
RUN git config --global user.email "nobody@example.com"; \
    git config --global user.name "Nobody"
