# В известных мне пакетах opencv собран без поддержки rtsp, поэтому собираю сам
FROM python:3.6-jessie

RUN apt-get update &&  apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python-dev \
    python-numpy \
    python-protobuf\
    software-properties-common \
    zip \
    cmake \
    libboost-all-dev \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*


RUN pip install numpy

WORKDIR /
RUN wget https://github.com/opencv/opencv/archive/3.3.0.zip \
&& unzip 3.3.0.zip \
&& mkdir /opencv-3.3.0/cmake_binary \
&& cd /opencv-3.3.0/cmake_binary \
&& cmake -DBUILD_TIFF=ON \
  -DBUILD_opencv_java=OFF \
  -DWITH_CUDA=OFF \
  # -DENABLE_AVX=ON \
  -DCPU_BASELINE_REQUIRE=SSE3 \
  -DWITH_OPENGL=ON \
  -DWITH_OPENCL=ON \
  -DWITH_IPP=ON \
  -DWITH_TBB=ON \
  -DWITH_EIGEN=ON \
  -DWITH_V4L=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=RELEASE \
  -DWITH_FFMPEG=ON \
  -DINSTALL_PYTHON_EXAMPLES=ON \
  -DBUILD_opencv_python3=ON \
  -DCMAKE_INSTALL_PREFIX=$(python3.6 -c "import sys; print(sys.prefix)") \
  -DPYTHON3_EXECUTABLE=$(which python3.6) \
  -DPYTHON3_INCLUDE_DIR=$(python3.6 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
  -DPYTHON3_PACKAGES_PATH=$(python3.6 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") .. \
&& make -j4 install \
&& rm -rf /opencv-3.3.0

RUN apt-get update && apt-get install -y --fix-missing locales && apt-get clean && rm -rf /tmp/* /var/tmp/*

ENV PYTHONPATH /app:$PYTHONPATH
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

RUN locale-gen ru_RU.UTF-8
RUN localedef -i ru_RU -f UTF-8 ru_RU.UTF-8

RUN pip install opencv-python imutils click requests django-environ
RUN pip install raven

EXPOSE 8000
ADD src /app
ADD requirements.txt /app/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
