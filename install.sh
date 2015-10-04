#!/usr/bin/env bash
bash_dirname=$(cd "$(dirname ${BASH_SOURCE[0]})";pwd)

echo Creating if not exists ~/bin
mkdir -p ~/bin

echo Making symlink to ~/bin/zipSeries for ~bash_dirname/zipSeries
ln -s "$bash_dirname/zipSeries" ~/bin/zipSeries

if [[ -f ~/.bashrc ]]; then
	echo "Adding \"source $bash_dirname/.bashrc\" to ~/.bashrc"
	echo '#Added by ZipSeries:' >> ~/.bashrc
	echo "source \"$bash_dirname/.bashrc\"" >> ~/.bashrc
fi

if [[ -f ~/.zshrc ]]; then
	echo "Adding \"source $bash_dirname/.zshrc\" to ~/.zshrc"
	echo '#Added by ZipSeries:' >> ~/.zshrc
	echo "source \"$bash_dirname/.zshrc\"" >> ~/.zshrc
fi

echo Creating if not exists /etc/zipSeries
sudo mkdir -p /etc/zipSeries

echo Change mode to 700 for /etc/zipSeries
sudo chmod 700 /etc/zipSeries
