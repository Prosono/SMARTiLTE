status=`ifconfig eth0 | grep RUNNING`

if [ -z "$status" ];then
	/usr/bin/dswrapper bg96
fi
