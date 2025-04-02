FROM mcr.microsoft.com/devcontainers/base:bookworm

# Install required packages
RUN apt-get update && \
    apt-get install -y libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev gcc

# Install Python and tools
RUN apt-get install -y python3 python3-pip