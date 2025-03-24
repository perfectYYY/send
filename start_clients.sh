#!/bin/bash  

# 强制重建镜像（带错误处理）  
if ! docker build -t drone-client . --no-cache; then  
    echo "镜像构建失败，请检查 Dockerfile"  
    exit 1  
fi  

CLIENT_COUNT=${1:-5}  
EXTRA_ARGS=""  

# 仅 Linux 需要特殊参数  
if [ "$(uname)" = "Linux" ]; then  
    EXTRA_ARGS="--add-host=host.docker.internal:host-gateway"  
fi  

for i in $(seq -f "%04g" 1 $CLIENT_COUNT); do  
    USERNAME="user$i"  
    CONTAINER_NAME="drone-client-$i"  
    
    # 修正换行格式（确保行尾反斜杠后无空格）  
    docker run -d \
        $EXTRA_ARGS \
        --name "$CONTAINER_NAME" \
        -e SERVER_HOST=host.docker.internal \
        -e DRONE_USERNAME="$USERNAME" \
        -e DRONE_PASSWORD="user123" \
        drone-client || echo "启动容器 $CONTAINER_NAME 失败"  
    
    echo "启动客户端: $CONTAINER_NAME (用户名: $USERNAME)"  
done  