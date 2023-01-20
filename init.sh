# if is ubuntu
if [ -f /etc/lsb-release ]; then
    # install ipatool
    if [ ! -f /usr/local/bin/ipatool ]; then
        wget https://github.com/majd/ipatool/releases/download/v2.0.1/ipatool-2.0.1-linux-arm64.tar.gz
        tar -xvf ipatool-2.0.1-linux-arm64.tar.gz
        chmod +x bin/ipatool-2.0.1-linux-arm64
        sudo mv bin/ipatool-2.0.1-linux-arm64 /usr/local/bin/ipatool
    fi
fi

# install requirements
pip3 install -r requirements.txt
