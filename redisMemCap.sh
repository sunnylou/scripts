#!/bin/bash
#
#
Rediscli="/usr/local/bin/redis-cli"
Homedir="/software/scripts"
Capfile="$Homedir/redisCheckMem/Warring.txt"
Tmpfile="/tmp/Warring.txt"
#Resultfile="/software/scripts/redisMemCap/capresult.txt"

# Define color
red() {
  echo -e "\033[31m $1 \033[0m"
}
green() {
  echo -e "\033[32m $1 \033[0m"
}
yellow() {
  echo -e "\033[33m $1 \033[0m"
}

# Capacity memory
CapMem() {
awk '{print $1}' $Capfile > $Tmpfile
CapacitySize=$(echo "$1 * 1024 * 1024 * 1024" | bc)

for i in $(cat $Tmpfile)
do
    UnknowRoleHost=$(echo $i | awk -F: '{print $1}')
    UnknowRolePort=$(echo $i | awk -F: '{print $2}')
    Role=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort info | grep role | awk -F: '{print $2}' | sed "s/\r//")
    UnknowRoleMaxmemory=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort config get maxmemory | tail -1)
    if [ "${Role}x" = masterx ]
    then
        SlaveHost=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort info | grep slave0 | awk -F, '{print $1}' | awk -F= '{print $2}' | sed "s/\r//")
        SlavePort=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort info | grep slave0 | awk -F, '{print $2}' | awk -F= '{print $2}' | sed "s/\r//")
        SlaveMaxmemory=$($Rediscli -h $SlaveHost -p $SlavePort config get maxmemory | tail -1)
        if [ ${UnknowRoleMaxmemory}x = ${CapacitySize}x -a ${SlaveMaxmemory}x = ${CapacitySize}x ]
        then
            continue
        else
            ##Capacity
            $Rediscli -h $UnknowRoleHost -p $UnknowRolePort config \set maxmemory $CapacitySize &> /dev/null && $Rediscli -h $SlaveHost -p $SlavePort config \set maxmemory $CapacitySize &> /dev/null
            if [ "$?x" = "0x" ]
            then
                NUnknowRoleMaxmemory=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort config get maxmemory | tail -1)
                NSlaveMaxmemory=$($Rediscli -h $SlaveHost -p $SlavePort config get maxmemory | tail -1)
                yellow "Master instance $UnknowRoleHost:$UnknowRolePort and Slave instance $SlaveHost:$SlavePort capacity successed"
                green "Master instance $UnknowRoleHost:$UnknowRolePort the current maxmemory: $NUnknowRoleMaxmemory"
                green "Slave instance $SlaveHost:$SlavePort the current maxmemory: $NSlaveMaxmemory"
            else
                red "Master instance $UnknowRoleHost:$UnknowRolePort and Slave instance $SlaveHost:$SlavePort capacity failed"
            fi
        fi
    elif [ "${Role}x" = slavex ]
    then
        MasterHost=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort info | grep master_host | awk -F: '{print $2}' | sed "s/\r//")
        MasterPort=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort info | grep master_port | awk -F: '{print $2}' | sed "s/\r//")
        MasterMaxmemory=$($Rediscli -h $MasterHost -p $MasterPort config get maxmemory | tail -1)
        if [ ${UnknowRoleMaxmemory}x = ${CapacitySize}x -a ${MasterMaxmemory}x = ${CapacitySize}x ]
        then
            continue
        else
            ##Capacity
            $Rediscli -h $UnknowRoleHost -p $UnknowRolePort config \set maxmemory $CapacitySize &> /dev/null && $Rediscli -h $MasterHost -p $MasterPort config \set maxmemory $CapacitySize &> /dev/null
            if [ "$?x" = "0x" ]
            then
                NUnknowRoleMaxmemory=$($Rediscli -h $UnknowRoleHost -p $UnknowRolePort config get maxmemory | tail -1)
                NMasterMaxmemory=$($Rediscli -h $MasterHost -p $MasterPort config get maxmemory | tail -1)
                yellow "Master instance $MasterHost:$MasterPort and Slave instance $UnknowRoleHost:$UnknowRolePort capacity successed"
                green "Master instance $MasterHost:$MasterPort the current maxmemory: $NMasterMaxmemory"
                green "Slave instance $UnknowRoleHost:$UnknowRolePort the current maxmemory: $NUnknowRoleMaxmemory"
            else
                red "Master instance $MasterHost:$MasterPort and Slave instance $UnknowRoleHost:$UnknowRolePort capacity failed"
            fi
        fi
    fi
done
}
if [ $# != 1 ]
then
    echo "Useage:" 
    echo -e "\t sh $0 CapacitySize(like:40G)"
    exit 2
fi
CapMem $1
