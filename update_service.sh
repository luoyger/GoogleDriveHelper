#!/bin/bash

# 获取当前目录
current_dir=$(pwd)

# 获取上一层目录
parent_dir=$(dirname "$current_dir")

# 查找最新的 .tar.gz 文件
latest_file=$(ls -t "$current_dir"/*.tar.gz 2>/dev/null | head -n 1)

# 检查是否找到文件
if [ -z "$latest_file" ]; then
  echo "No .tar.gz files found in the current directory."
  exit 1
fi

# 移动文件到上一层目录
mv "$latest_file" "$parent_dir"
echo "Moved $latest_file to $parent_dir"

# 获取文件名
filename=$(basename "$latest_file")

# 解压文件
tar -xzvf "$parent_dir/$filename" -C "$parent_dir"
echo "Extracted $filename in $parent_dir"

sh start.sh
echo "Start service"