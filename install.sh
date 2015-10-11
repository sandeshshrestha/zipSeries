#!/usr/bin/env bash
bash_dirname=$(cd "$(dirname ${BASH_SOURCE[0]})";pwd)
old_dir=$PWD
cd $bash_dirname;

nosymlink=false
norc=false
nocfg=false


is_windows() { [[ -n "$WINDIR" ]]; }

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

if [ "$nosymlink" = false ]; then
	echo $pgm: creating if not exists ~/bin
	mkdir -p ~/bin

	# Remove old zipSeries
	[[ -f ~/bin/zipSeries ]] && echo $pgm: removing ~/bin/zipSeries && rm ~/bin/zipSeries

	link="$(cd ~/bin;pwd)/zipSeries"
	target="$bash_dirname/zipSeries.py"
	link2="$(cd ~/bin;pwd)/zipSeriesPrompt"
	target2="$bash_dirname/zipSeriesPrompt.pl"

	# Remove current link so we can handle updates
	rm $link 2> /dev/null
	rm $link2 2> /dev/null

	# Support zipSeries in git bash
	# Source: https://stackoverflow.com/questions/18641864/git-bash-shell-fails-to-create-symbolic-links
	if is_windows; then
		echo $pgm: creating wrapper command for $link
		echo "#!/usr/bin/env bash" > $link
		echo "python \"$target\" \$@" >> $link
		
		echo $pgm: creating wrapper command for $link2
		echo "#!/usr/bin/env bash" > $link2
		echo "perl \"$target2\" \$@" >> $link2
	else
		echo $pgm: making symlink to $link for $target
		ln -s "$target" "$link"
		
		echo $pgm: making symlink to $link2 for $target2
		ln -s "$target2" "$link2"
	fi

	if [[ "$?" != "0" ]]; then
		>&2 echo $pgm: error: cannot create symlink to $link for $target
		exit 1
	fi
	chmod +x $link
	chmod +x $link2
fi

if [ "$norc" = false ]; then
	if [[ -f ~/.bashrc ]]; then
		echo "$pgm: adding \"source $bash_dirname/.bashrc\" to ~/.bashrc"
		echo '#Added by ZipSeries:' >> ~/.bashrc
		echo "[[ -f \"$bash_dirname/.bashrc\" ]] && source \"$bash_dirname/.bashrc\"" >> ~/.bashrc
	fi

	if [[ -f ~/.zshrc ]]; then
		echo "$pgm: adding \"source $bash_dirname/.zshrc\" to ~/.zshrc"
		echo '#Added by ZipSeries:' >> ~/.zshrc
		echo "[[ -f \"$bash_dirname/.zshrc\" ]] && source \"$bash_dirname/.zshrc\"" >> ~/.zshrc
	fi
fi

if [ "$nocfg" = false ]; then
	echo $pgm: creating if not exists /etc/zipSeries

	mkdir -p /etc/zipSeries

	if [[ "$?" != "0" ]]; then
		>&2 echo $pgm: error: cannot create /etc/zipSeries
		exit 1
	fi

	echo $pgm: change mode to 700 for /etc/zipSeries
	chmod 700 /etc/zipSeries
	
	if [[ ! -f "(/etc/zipSeries/zipSeries.conf" ]]; then
		echo $pgm: creating example file zipSeries.conf in /etc/zipSeries
		cat "$bash_dirname/examples/zipSeries.conf" > /etc/zipSeries/zipSeries.conf
		chmod 600 /etc/zipSeries/zipSeries.conf
	fi
fi

cd $old_dir
