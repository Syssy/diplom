#!/bin/sh

DESKTOP_PATH=$HOME/.local/share/applications/
DESKTOP_FILE=$DESKTOP_PATH/mendeleydesktop.desktop
MENDELEYDESKTOP_BIN=$HOME/.local/share/mendeleydesktop
GCONF_TOOL=`which gconftool-2`

if [ $? -ne 0 ]; then
	echo "Unable to find gconftool-2.  The mendeley:// link handler may not be installed correctly." >&2
fi
if [ ! -d "$DESKTOP_PATH" ]; then
	mkdir -p "$DESKTOP_PATH"
fi

while getopts "u" flag
do
	case $flag in
	u)
		# Uninstall the link handler
		rm -f $DESKTOP_FILE
		update-desktop-database $DESKTOP_PATH
		$GCONF_TOOL -u /desktop/gnome/url-handlers/mendeley

		exit 0
		;;
	\?)
		echo "Unknown option: -$OPTARG" >&2
		;;
  	esac
done

shift $(($OPTIND - 1))
if [ $# -ne 1 ]; then
	echo "Usage: "`basename $0`" [options] <path>"
	echo " -u : Uninstall the mendeley:// link handler"
	echo ""
	echo "Install the mendeley:// link handler to launch <path>"
	echo ""
	exit 1
fi

if [ ! -f "$1" ]; then
	echo "Mendeley Desktop binary '$1' does not exist"
	exit 1
fi

# create symlink from fixed location to last-used Mendeley Desktop
# binary
MENDELEYDESKTOP_REAL_BIN=$1
ln -fs $MENDELEYDESKTOP_REAL_BIN $MENDELEYDESKTOP_BIN

# install .desktop file and re-build mime cache to enable
# mendeley:// link handler.
# If the contents of the .desktop file are changed, the X-Mendeley-Version
# key needs to be incremented
cat > $DESKTOP_PATH/mendeleydesktop.desktop <<EOF
[Desktop Entry]
Name=Mendeley Desktop
GenericName=Research Paper Manager
Comment=Mendeley Desktop is software for managing and sharing research papers
Exec=$MENDELEYDESKTOP_BIN %u
Icon=mendeleydesktop
Terminal=false
Type=Application
Categories=Education;Literature;Qt;
X-SuSE-translate=false;
MimeType=x-scheme-handler/mendeley;application/pdf;text/x-bibtex;
X-Mendeley-Version=1
EOF

update-desktop-database $DESKTOP_PATH

# install the gnome link handler
$GCONF_TOOL -s /desktop/gnome/url-handlers/mendeley/command "$MENDELEYDESKTOP_BIN %s" --type String
$GCONF_TOOL -s /desktop/gnome/url-handlers/mendeley/enabled --type Boolean true

