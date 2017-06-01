#!/bin/bash
CURDIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
cd $CURDIR
rm -rf build hadoop_optimizer.egg-info
cp -rf ./scripts /home/optimizer
cp -rf ./rpms /home/optimizer
tar -zxvf /home/optimizer/rpms/*.tar.gz -C /home/optimizer/rpms
cd $CURDIR
python setup.py sdist
pip uninstall -y hadoop_optimizer
pip install --force-reinstall dist/*.tar.gz
cp -f ../lenovo-hadoop-optimizer /usr/bin
chmod +x /usr/bin/lenovo-hadoop-optimizer
/usr/bin/lenovo-hadoop-optimizer restart
echo "/usr/bin/lenovo-hadoop-optimizer start" >> /etc/rc.local
