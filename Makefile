#!make
all:
	cp hunter.py /usr/local/bin/hunter
	cp hunter /usr/local/share/man/man1/hunter.1
	echo "\033[0;32mHunter installed successfully\033[0m"

uninstall:
	rm /usr/local/bin/hunter
	rm /usr/local/share/man/man1/hunter.1
	echo "\033[0;32mHunter uninstalled successfully"\033[0m
