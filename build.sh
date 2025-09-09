#!/bin/bash

# 获取当前项目的名称
PROJECT_NAME=$(basename "$PWD")

# 获取当前日期和时间
CURRENT_DATETIME=$(date +"%Y%m%d_%H%M%S")

# 构建压缩包的文件名，包含项目名称和当前日期时间
ZIP_FILENAME="${PROJECT_NAME}_${CURRENT_DATETIME}.tar.gz"

TEMP_DIR=$(mktemp -d)

# 定义要排除的目录和文件
EXCLUDE_DIRS=(".git" ".idea" "venv" "__pycache__" "data/temp_link_data/")
EXCLUDE_FILES=(".DS_Store" "build.sh" "output.log" "output.log.*" "pid.txt" "local.yaml" "*.tar.gz")

# 构建排除参数
RSYNC_EXCLUDE_PARAMS=()
for dir in "${EXCLUDE_DIRS[@]}"; do
    RSYNC_EXCLUDE_PARAMS+=("--exclude=${dir}")
done
for file in "${EXCLUDE_FILES[@]}"; do
    RSYNC_EXCLUDE_PARAMS+=("--exclude=${file}")
done

# 创建一个以项目名命名的子目录
mkdir "$TEMP_DIR/$PROJECT_NAME"

# 使用 rsync 复制项目到临时目录的子目录中
rsync -av "${RSYNC_EXCLUDE_PARAMS[@]}" . "$TEMP_DIR/$PROJECT_NAME"

# 在临时目录中创建压缩包
tar -czvf "$ZIP_FILENAME" -C "$TEMP_DIR" "$PROJECT_NAME"

# 删除临时目录
rm -rf "$TEMP_DIR"

echo "Project has been zipped into $ZIP_FILENAME"