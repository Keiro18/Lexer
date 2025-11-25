FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y

# Herramientas esenciales
RUN apt install -y build-essential git make cmake gdb python3 python3-pip

# Instalar dependencias del compilador
RUN pip3 install rich sly multimethod

# LLVM completo
RUN apt install -y llvm clang lld lldb

# Crear usuario no-root
RUN useradd -ms /bin/bash dev
USER dev
WORKDIR /home/dev/project

CMD ["/bin/bash"]