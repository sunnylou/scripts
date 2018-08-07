#!/bin/bash
#####################################
PD (){
mkdir /{data01,data02,data03,data04,data05,data06,data07,data08,data09,data10,data11,data12}
i=2
nu=1
while [ $i -lt 14 ]
do
j=`echo $i|awk '{printf "%c",96+$i}'`
parted /dev/sd${j} -s mklabel gpt
parted /dev/sd${j} -s -- mkpart primary 0 -1
mkfs.ext4 -T largefile /dev/sd${j}1
 if [ $nu -lt 10 ]
   then
uuid=`blkid /dev/sd${j}1 | awk '/dev/{print $2}'|sed 's/"//g'`
echo "$uuid /data0${nu} ext4 defaults  0 0" >> /etc/fstab
   else
uuid=`blkid /dev/sd${j}1 | awk '/dev/{print $2}'|sed 's/"//g'`
echo "$uuid /data${nu} ext4 defaults  0 0" >> /etc/fstab
 fi
tune2fs -m 1 $uuid
((nu=nu+1))
let i+=1
done
mount -a
}
PD
