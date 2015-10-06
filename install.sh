#!/usr/bin/env bash
bash_dirname=$(cd "$(dirname ${BASH_SOURCE[0]})";pwd)
old_dir=$PWD
cd $bash_dirname;

nosymlink=false
norc=false
nocfg=false

pgm=$0
while (($#)); do
	case $1 in
		--help )
			echo 'usage: '$pgm' [OPTION]...'
			echo 'Install zipSeries CLI on your machine'
			echo ''
			echo '      --nosymlink      dont create a symlink in the folder ~/bin'
			echo '      --norc           dont add code to ~/.bashrc and ~/.zshrc'
			echo '      --nocfg          dont create the folder /etc/zipSeries'
			echo '      --help           display this help and exit'
			exit 0
			;;
		--nosymlink ) nosymlink=true;;
		--norc ) norc=true;;
		--nocfg ) nocfg=true;;
		* ) 
			>&2 echo "$pgm: option '$1' not supported"
			exit 1
			;;
	esac
	shift
done

echo Compiling zipSeries.py to zipSeries
python -m py_compile zipSeries.py
mv zipSeries.pyc zipSeries
chmod +x zipSeries

if [ "$nosymlink" = false ]; then
	echo Creating if not exists ~/bin
	mkdir -p ~/bin

	echo Making symlink to ~/bin/zipSeries for $bash_dirname/zipSeries
#	ln -s "$bash_dirname/zipSeries" ~/bin/zipSeries
fi

if [ "$norc" = false ]; then
	if [[ -f ~/.bashrc ]]; then
		echo "Adding \"source $bash_dirname/.bashrc\" to ~/.bashrc"
		echo '#Added by ZipSeries:' >> ~/.bashrc
#		echo "[[ -f \"$bash_dirname/.bashrc\" ]] && source \"$bash_dirname/.bashrc\"" >> ~/.bashrc
	fi

	if [[ -f ~/.zshrc ]]; then
		echo "Adding \"source $bash_dirname/.zshrc\" to ~/.zshrc"
		echo '#Added by ZipSeries:' >> ~/.zshrc
#		echo "[[ -f \"$bash_dirname/.zshrc\" ]] && source \"$bash_dirname/.zshrc\"" >> ~/.zshrc
	fi
fi

if [ "$nocfg" = false ]; then
	echo Creating if not exists /etc/zipSeries
	sudo mkdir -p /etc/zipSeries

	echo Change mode to 700 for /etc/zipSeries
	sudo chmod 700 /etc/zipSeries
fi

cd $old_dir
