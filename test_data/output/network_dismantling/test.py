import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd
import attack_model as am


time_start0 = time.time()

# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构造 test_data 的绝对路径
data_path = os.path.join(script_dir, 'test_data', 'small')
files = os.listdir(data_path)

files = [file for file in files if file[-4:] == '.txt']

decycle_nodes = []
nodes_file = os.path.join(script_dir, 'test_data', 'decycle', 'nodes_only.txt')
if os.path.exists(nodes_file):
    with open(nodes_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                decycle_nodes.append(int(s))
            except ValueError:
                decycle_nodes.append(s)

print(decycle_nodes)
print(len(decycle_nodes))






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
    G = g.copy()
    # Base_line Model
    
    
    lcc_size1 = am.high_degree_attack(g, n, m - 1)
    print("HD attack finished")
    lcc_size2 = am.high_bt_attack(g, n, m - 1)
    print("BT attack finished")
    lcc_size3 = []
    for v in decycle_nodes:
            G.remove_node(v)
            lcc_size3.append(1)
    lcc_size3.append(am.lcc(G)/n)
    print("Decycler attack finished")
    #lcc_size3 = am.MS_attack(g, stop_condition=100,n )
    lcc_size4 = am.gnd(g, n, m - 1)
    print("GND attack finished")
    

    # 目标目录
    target_dir = r"E:\科研\Paper_figure\GCC_Size\png"

    # 创建目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)
    
    # plot
    step = 5
    plt.figure(figsize=(5, 6))
    plt.plot(x[0: len(lcc_size1)], lcc_size1, color='#264653', label='HD', marker='^', markersize=0, linewidth=1.8)
    plt.plot(x[0: len(lcc_size2)], lcc_size2, color='#39C5BB', label='BT', marker='^', markersize=0, linewidth=1.8)
    plt.plot(x[0: len(lcc_size3)], lcc_size3, color='#FFE211', label='MSR', marker='^', markersize=0, linewidth=1.8)
    plt.plot(x[0: len(lcc_size4)], lcc_size4, color='#FAAFBE', label='GND', marker='o', markersize=0, linewidth=1.8)
    '''plt.plot(x[0: len(lcc_size5)], lcc_size5, color='#FFA500', label='CC', marker='o', markersize=0, linewidth=1.8)'''
    '''plt.plot(x[0: len(lcc_size6)], lcc_size6, color='#FAAFBE', label='EC', marker='o', markersize=0, linewidth=1.8)'''
   

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

     # 创建目录（如果不存在）
    os.makedirs(target_png, exist_ok=True)
    os.makedirs(target_svg, exist_ok=True)
    os.makedirs(target_pdf, exist_ok=True)
    os.makedirs(target_excel, exist_ok=True)
    
    plt.savefig(os.path.join(target_png, filename[:-4] + '.png'), format='png', dpi=2000)
    plt.savefig(os.path.join(target_svg, filename[:-4] + '.svg'), format='svg')
    plt.savefig(os.path.join(target_pdf, filename[:-4] + '.pdf'), format='pdf')
    plt.show()
    plt.close()
   
    '''excel_filename = os.path.join(target_excel, filename[:-4] + '.xlsx')
    # Save Data
    # 获取所有lcc_size列表的长度
    attack_lengths = [
        len(lcc_size0),
        len(lcc_size1),
        len(lcc_size2),
        len(lcc_size3),
        len(lcc_size4)
    ]
    max_length = max(attack_lengths)  # 最大长度
    
    # 填充短列表至统一长度（用NaN填充）
    lcc_size0 += [np.nan] * (max_length - len(lcc_size0))
    lcc_size1 += [np.nan] * (max_length - len(lcc_size1))
    lcc_size2 += [np.nan] * (max_length - len(lcc_size2))
    lcc_size3 += [np.nan] * (max_length - len(lcc_size3))
    lcc_size4 += [np.nan] * (max_length - len(lcc_size4))
    
    # 构建数据字典（确保所有值长度一致）
    data_dict = {
        "None": lcc_size0,
        "HD": lcc_size1,
        "HB": lcc_size2,
        "CI": lcc_size3,
        "GND": lcc_size4,
        "Order": [Order] * max_length,       # 扩展元数据到相同长度
        "LCC": [LCC] * max_length,
        "None_Time": [None_Time] * max_length,
        "HD_Time": [HD_Time] * max_length,
        "HB_Time": [BT_Time] * max_length,
        "CI_Time": [CI_Time] * max_length,
        "GND_Time": [GND_Time] * max_length
    }
    
    # 创建DataFrame
    data = pd.DataFrame(data_dict)
    
    # 写入Excel（每个文件独立）
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        data.to_excel(
            writer,
            sheet_name='Attack_Results',
            float_format='%.5f',
            index=False  # 不生成行索引
        )'''
    #Save Data
    '''GCC = [
        lcc_size0,  # None Enhancement的lcc_size
        lcc_size1,  # HD
        lcc_size2,  # HB (BT)
        lcc_size3,  # CI
        lcc_size4,  # GND
        [Order],     # 图的节点数
        [LCC],       # 最大连通组件大小
        [None_Time], # 无增强时间
        [HD_Time],   # HD增强时间
        [BT_Time],   # BT增强时间（对应HB_Time）
        [CI_Time],   # CI增强时间
        [GND_Time]   # GND增强时间
    ]
    
    # 索引顺序必须与GCC元素一一对应
    index_labels = [
        "None",
        "HD",
        "HB",
        "CI",
        "GND",
        "Order",
        "LCC",
        "None_Time",
        "HD_Time",
        "HB_Time",
        "CI_Time",
        "GND_Time"
    ]
    
    # 创建DataFrame，索引按注释要求顺序排列
    data = pd.DataFrame(GCC, index=index_labels)
    
    # 使用ExcelWriter追加模式写入，确保安装openpyxl
    with pd.ExcelWriter('Result_8.10_large.xlsx', mode='a', engine='openpyxl') as writer:
        # 将数据保存到以文件名命名的sheet中，格式保留5位小数
        data.to_excel(writer, sheet_name=filename[:-4], float_format='%.5f')'''