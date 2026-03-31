import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd
import attack_model as am
import enhancement_model as em

time_start0 = time.time()

# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构造 test_data 的绝对路径
data_path = os.path.join(script_dir, 'test_data', 'small')
graph_file_path = os.path.join(script_dir, 'test_data', 'graph')
files = os.listdir(data_path)

files = [file for file in files if file[-4:] == '.txt']


for i, filename in enumerate(files):
    
    print('-' * 60, i, '\nWhich file to attack: ', filename)

    file = os.path.join(data_path, filename)
    
    g = nx.read_edgelist(file, nodetype=int)
    
    Order = g.order()
    print('The order of graph: ', Order)
    
    # if Order <= 10000 or Order > 30000:
    #     continue
    
    LCC = am.lcc(g)
    print("Largest connected component: ", LCC)

    if not nx.is_connected(g):
        g = g.subgraph(max(nx.connected_components(g), key=len))#如果不是全部联通就取最大的部分
    
    n = g.order()  #节点总数
    m = int(0.8 * n)  #攻击节点数目
    x = np.linspace(1.0 / n, 1, n)[:m]
    enhance_ratio=0.1
    #选择增强节点
    num_enhance_nodes = int(n * enhance_ratio)
    r=nx.diameter(g)
    print('Diameter of graph: ', r)
    enhance_methods = [
        ('HD', em.high_degree_enhancement),
        ('GBT', em.general_betweenness_centrality_enhancement),
        ('GND', em.gnd_enhancement_1),
        ('BT', em.high_betweenness_enhancement)
    ]
    
    enhance_nodes = {} #保护节点
    time_data = {}  #保护时间
    
    for prefix, func in enhance_methods:
        result, time_val = func(g, n, m)
        enhance_nodes[prefix] = result[:num_enhance_nodes]
        time_data[f"{prefix}_Time"] = time_val
    lcc_sizes = {}
    lcc_sizes[0] = am.gnd(g, n, m-1)  # None

    for i, prefix in enumerate(enhance_nodes.keys(), start=1):
        lcc_sizes[i] = am.gnd_with_enhancement_1(g, n, m-1, enhance_nodes[prefix])
    
    # 目标目录
    target_dir = r"E:\科研\Paper_figure\GCC_Size\png"

    # 创建目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)
    
    # plot
    step = 5
    plt.figure(figsize=(5, 6))
    colors = ['#D80000', '#264653', '#39C5BB', '#FFE211', '#FAAFBE']
    labels = ['None', 'HD', 'GBT',  'GND', 'BT']
    for i in range(5):
        plt.plot(x[:len(lcc_sizes[i])], lcc_sizes[i], 
        color=colors[i], label=labels[i],
        marker='^' if i < 4 else 'o', 
        markersize=0, linewidth=1.8)
    plt.legend(fontsize='large')

    # plt.title(filename[1:-4])
    plt.xlabel('Attack Ratio', fontsize=16)
    plt.ylabel('GCC Size', fontsize=16)
   
    plt.xticks(np.around(np.linspace(0, 1, 5, endpoint=True), 2))
    plt.yticks(np.linspace(0, 1, 11, endpoint=True))
    plt.tick_params(labelsize=13)
    plt.grid(axis='x', linestyle='-', linewidth=0.7, color='black', alpha=0.1)
    plt.grid(axis='y', linestyle='-', linewidth=0.7, color='black', alpha=0.1)
    plt.xlim(0, 0.5)
    plt.ylim(0, 1)
    plt.subplots_adjust(top=0.96, bottom=0.1, left=0.15, right=0.93)
     # 目标目录
    target_png = r"E:\科研\Paper_figure\GCC_Size\png"
    target_svg = r"E:\科研\Paper_figure\GCC_Size\svg"
    target_pdf = r"E:\科研\Paper_figure\GCC_Size\pdf"
    target_excel = r"E:\科研\Paper_figure\GCC_Size\excel"

     # 创建目录
    os.makedirs(target_png, exist_ok=True)
    os.makedirs(target_svg, exist_ok=True)
    os.makedirs(target_pdf, exist_ok=True)
    os.makedirs(target_excel, exist_ok=True)
    
    plt.savefig(os.path.join(target_png, filename[:-4] + '.png'), format='png', dpi=2000)
    plt.savefig(os.path.join(target_svg, filename[:-4] + '.svg'), format='svg')
    plt.savefig(os.path.join(target_pdf, filename[:-4] + '.pdf'), format='pdf')
    plt.show()
    plt.close()
    
    excel_filename = os.path.join(target_excel, filename[:-4] + '.xlsx')
    # Save Data
    # 获取所有lcc_size列表的长度
    # 填充短列表至统一长度（用NaN填充）
    max_len = max(len(lst) for lst in lcc_sizes.values())
    for i in lcc_sizes:
        lcc_sizes[i] += [np.nan] * (max_len - len(lcc_sizes[i]))  # 最大长度
    
    
    data_dict = {
        "Order": [Order] * max_len,
        "LCC": [LCC] * max_len
    }
    
        
    for i, label in enumerate(labels):
        data_dict[label] = lcc_sizes[i]
        
    for time_key, time_val in time_data.items():
        # 只有第一个元素有值，其余为NaN
        time_list = [time_val] + [np.nan] * (max_len - 1)
        data_dict[time_key] = time_list
        
    
    # 创建DataFrame
    data = pd.DataFrame(data_dict)
    
    # 写入Excel（每个文件独立）
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        data.to_excel(
            writer,
            sheet_name='Attack_Results',
            float_format='%.5f',
            index=False  # 不生成行索引
        )
    