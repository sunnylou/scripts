#!/bin/bash
###########################################
#
# 检查集群里面每个实例的内存使用入库
#
###########################################

STARTPORT=6381
ENDPORT=6404
WORKDIR="/software/scripts/redisCheckMem"
REDIS_HOST_FILE="$WORKDIR/kv3HostList"
REDIS_CLI='/usr/local/bin/redis-cli'
TMP_DB_FILE="$WORKDIR/DBfile.txt"
WARR_FILE="$WORKDIR/Warring.txt"

# 定义内存使用比例的阀值
W_NUM='94'

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

AutoCheck() {
    datetime=`date +%Y%m%d%H`
    >$TMP_DB_FILE
    >$WARR_FILE
    for host in `cat $REDIS_HOST_FILE`
        do
	   echo "------------------------------------------------"
           for port in `seq $STARTPORT $ENDPORT`
	    do
	    Max_mem=$($REDIS_CLI -h $host -p $port config get maxmemory|tail -1|awk '{printf "%.4f\n", ($1 / 1024 /1024 /1024)}')
	    Used_mem=$($REDIS_CLI -h $host -p $port info memory|awk -F : '/used_memory:/ {printf "%.4f\n", ($2 /1024/1024/1024)}') 
	    P_used_mem=$(awk "BEGIN{print $Used_mem/$Max_mem*100 }")

	    yellow "Server:[$host:$port] MemoryInfo : "
	    echo -e "\t Max_memory: $Max_mem G"
	    echo -e "\t Used_memory: $Used_mem G"

	    num=$(echo $P_used_mem|awk -F . '{print $1}')
	    if [[ $num -gt $W_NUM ]];then
		echo "$host:$port $Max_mem $Used_mem $P_used_mem" >> $WARR_FILE
	        red "\t Percentage used: $P_used_mem"
		red "\t Warring: 内存使用率过高，请关注!!!"
	    else
		green "\t Percentage used: $P_used_mem"
	    fi

	    echo -n "insert into bdcsc2_clustermonitor_kv (date,ip,port,mem_use,kv) values " >> $TMP_DB_FILE
            echo "('$datetime','$host','$port','$Used_mem','kv3');" >> $TMP_DB_FILE

	    sleep 0.5
	done
    done
}

#Report2db() {

#mysql -hXX.XX.XX.XX -uroot -p{yourpasswd} -D bdcsc2_report < $TMP_DB_FILE

#}


case "$1" in
check)
	AutoCheck
        ;;
report2db)
	AutoCheck
        # Report2db
        ;;
*)
        echo "Usage: $0 check"
esac

