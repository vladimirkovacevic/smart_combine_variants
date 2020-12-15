FROM images.sbgenomics.com/vladimirk/python:3.8.1

WORKDIR /opt
COPY . /opt

RUN pip install --upgrade pip
RUN pip install  docopt toolz bgzip
RUN git clone https://github.com/vladimirkovacevic/smart_combine_variants.git
WORKDIR /opt/smart_combine_variants
RUN git checkout -b work da2151d79fa2eaa2619e8da76bffec81d86497f6

