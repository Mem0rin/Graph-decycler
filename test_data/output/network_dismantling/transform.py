import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd
#import attack_model as am
#import enhancement_model as em

time_start0 = time.time()

# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构造 test_data 的绝对路径
data_path = os.path.join(script_dir, 'test_data', 'small')
files = os.listdir(data_path)

files = [file for file in files if file[-4:] == '.txt']

# 创建graph文件夹用于保存转换后的文件
graph_output_dir = os.path.join(script_dir, 'test_data', 'small', 'graph')
os.makedirs(graph_output_dir, exist_ok=True)  # 确保graph文件夹存在


def detect_graph_type(input_file):
    """
    自动检测图是有向还是无向
    逻辑：如果存在 i->j 且 j->i，则为无向图；否则为有向图
    """
    edges = set()
    reverse_edges = set()
    
    try:
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    source, target = parts[0], parts[1]
                    if source != target:
                        edges.add((source, target))
                        reverse_edges.add((target, source))
        
        # 检查是否为无向图（双向边）
        bidirectional_count = len(edges & reverse_edges)
        total_edges = len(edges)
        
        # 如果超过 50% 的边都有反向边，认为是无向图
        if total_edges > 0 and bidirectional_count / total_edges > 0.5:
            return 'E'  # 无向图
        else:
            return 'D'  # 有向图
    except Exception as e:
        print(f"检测图类型时出错: {e}")
        return 'D'  # 默认为有向图

def convert_to_decycler_format(input_file, output_file):
    """
    将图文件转换为decycler所需的格式（参考gnp.py格式）
    输入：每行 source target
    输出：每行 [D|E] source target
           D 表示有向边，E 表示无向边
    """
    try:
        # 首先读取所有边并收集节点集合
        raw_edges = []
        nodes = set()
        with open(input_file, 'r') as f_in:
            for line in f_in:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    s, t = parts[0], parts[1]
                    if s == t:
                        continue
                    raw_edges.append((s, t))
                    nodes.add(s); nodes.add(t)

        if len(raw_edges) == 0:
            print(f"警告: 输入文件 {input_file} 没有有效边")
            return False

        # 重新索引节点为 0..N-1（保持原标签的顺序为升序字符串->int 若可能）
        try:
            # 尝试按整数排序，如果原标签是数字字符串
            sorted_nodes = sorted(nodes, key=lambda x: int(x))
        except Exception:
            sorted_nodes = sorted(nodes)
        node_map = {orig: str(i) for i, orig in enumerate(sorted_nodes)}

        # 检测是否为无向图（如果多数边都有反向边）
        edge_set = set(raw_edges)
        reverse_count = sum(1 for (a, b) in raw_edges if (b, a) in edge_set)
        is_undirected = (reverse_count / len(raw_edges)) > 0.5

        # 为兼容 deccycler/gpn 输出，始终使用 'D' 作为前缀（gnp.py 使用 'D'）
        out_prefix = 'D'

        processed = set()
        with open(output_file, 'w') as f_out:
            for s, t in raw_edges:
                if is_undirected:
                    a, b = sorted([s, t], key=lambda x: int(x) if x.isdigit() else x)
                    pair = (a, b)
                    if pair in processed:
                        continue
                    processed.add(pair)
                    ns = node_map[a]; nt = node_map[b]
                else:
                    ns = node_map[s]; nt = node_map[t]
                    pair = (ns, nt)
                f_out.write(f"{out_prefix} {ns} {nt}\n")

        print(f"  原节点数: {len(nodes)}, 重新索引后节点数: {len(node_map)}")
        print(f"  检测到图类型: {'无向图' if is_undirected else '有向图'}, 输出前缀: {out_prefix}")
        return True
    except Exception as e:
        print(f"转换文件时出错 {input_file}: {e}")
        return False
def batch_convert_graphs(file_list, input_dir, output_dir):
    """
    批量转换图文件
    """
    converted_files = []
    
    for filename in file_list:
        input_file = os.path.join(input_dir, filename)
        
        # 生成输出文件名（保持原文件名，添加路径）
        output_filename = f"decycler_{filename}"
        output_file = os.path.join(output_dir, output_filename)
        
        # 转换文件
        if convert_to_decycler_format(input_file, output_file):
            converted_files.append(output_filename)
            print(f"已转换: {filename} -> {output_filename}")
        else:
            print(f"转换失败: {filename}")
    
    return converted_files

# 批量转换所有图文件
print("开始批量转换图文件...")
converted_files = batch_convert_graphs(files, data_path, graph_output_dir)
print(f"批量转换完成！共转换 {len(converted_files)} 个文件")
print(f"输出目录: {graph_output_dir}")