
enhance_methods = [
    ('HD', em.high_degree_enhancement),
    ('BT', em.high_betweenness_enhancement),
    ('CI', em.collective_influence_enhancement),
    ('GND', em.gnd_enhancement_1),
    ('CC', em.closeness_centrality_enhancement),
    ('EC', em.eigenvector_centrality_enhancement),
    ('CFCC', em.current_flow_closeness_centrality_enhancement),
    ('CFBT', em.current_flow_betweenness_centrality_enhancement),
    ('GBT', em.general_betweenness_centrality_enhancement)
]
colors = ['#D80000', '#264653', '#39C5BB', '#FFE211', '#FAAFBE', '#FFA500', "#0D2A8A", "#14DA38", "#D3EB1EDC"]
labels = ['None', 'HD', 'BT', 'CI', 'GND', 'CC', 'EC', 'CFCC', 'CFBT', 'GBT']