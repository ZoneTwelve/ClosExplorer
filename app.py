from flask import Flask, request, render_template
from graphviz import Digraph
from itertools import product
import os

app = Flask(__name__)

# Updated switch catalog with costs
SWITCHES = {
    'a1': {'bandwidth': 20, 'ports': 8, 'cost': 100},
    'a2': {'bandwidth': 60, 'ports': 16, 'cost': 250},
    'A': {'bandwidth': 100, 'ports': 32, 'cost': 500},
    'B': {'bandwidth': 400, 'ports': 32, 'cost': 1500},
    'C': {'bandwidth': 100, 'ports': 64, 'cost': 700},
    'D': {'bandwidth': 400, 'ports': 64, 'cost': 2000},
    'E': {'bandwidth': 800, 'ports': 64, 'cost': 3500}
}

def generate_topology_graph(leaf_switch, leaf_count, spine_switch, spine_count,
                           superspine_switch, superspine_count, servers, servers_per_rack, idx):
    dot = Digraph(comment='Clos Network Topology', format='png')
    dot.attr(rankdir='BT')  # Upside-down as per previous request

    # Servers (grouped by rack)
    for rack in range(leaf_count):
        with dot.subgraph(name=f'cluster_rack{rack}') as rack_sub:
            rack_sub.attr(label=f'Rack {rack+1}')
            for s in range(servers_per_rack if rack < leaf_count - 1 else servers - (leaf_count - 1) * servers_per_rack):
                rack_sub.node(f's{rack}_{s}', f'Server {s+1}', shape='box')

    # Leaf switches
    for i in range(leaf_count):
        dot.node(f'l{i}', f'Leaf {i+1}\n({leaf_switch})', shape='rectangle')
        for s in range(servers_per_rack if i < leaf_count - 1 else servers - (leaf_count - 1) * servers_per_rack):
            dot.edge(f's{i}_{s}', f'l{i}')

    if spine_count > 0:
        for i in range(spine_count):
            dot.node(f'sp{i}', f'Spine {i+1}\n({spine_switch})', shape='rectangle')
            for j in range(leaf_count):
                dot.edge(f'l{j}', f'sp{i}')

        if superspine_count > 0:
            for i in range(superspine_count):
                dot.node(f'ssp{i}', f'Superspine {i+1}\n({superspine_switch})', shape='rectangle')
                for j in range(spine_count):
                    dot.edge(f'sp{j}', f'ssp{i}')

    output_path = f'static/topology_{idx}'
    dot.render(output_path, view=False, cleanup=True)
    return f'topology_{idx}.png'

def calculate_topology(servers, oversub, bw_per_server, tiers, racks=None):
    if racks is None:
        racks = max(1, servers // 24)
    servers_per_rack = (servers + racks - 1) // racks
    leaf_count = racks

    results = []
    idx = 0

    for leaf_switch in SWITCHES.keys():
        leaf = SWITCHES[leaf_switch]
        if leaf['ports'] < servers_per_rack:
            continue
        downlinks = servers_per_rack
        downlink_bw = downlinks * bw_per_server
        if downlink_bw > leaf['bandwidth']:
            continue
        uplinks = leaf['ports'] - downlinks
        uplink_bw = downlink_bw / oversub
        uplink_ports_needed = max(1, int(uplink_bw / bw_per_server))
        if uplinks < uplink_ports_needed:
            continue

        if tiers == 1 and leaf_count == 1:
            img = generate_topology_graph(leaf_switch, 1, None, 0, None, 0, servers, servers, idx)
            total_cost = SWITCHES[leaf_switch]['cost'] * 1
            results.append({'image': img, 'leaf': leaf_switch, 'leaf_count': 1,
                           'spine': None, 'spine_count': 0, 'superspine': None, 'superspine_count': 0,
                           'total_cost': total_cost})
            idx += 1
            continue

        total_spine_ports_needed = leaf_count * uplinks
        for spine_switch in SWITCHES.keys():
            spine = SWITCHES[spine_switch]
            spine_count = max(1, (total_spine_ports_needed + spine['ports'] - 1) // spine['ports'])
            spine_bw = spine_count * spine['ports'] * bw_per_server
            if spine_bw < uplink_bw * leaf_count:
                continue

            if tiers == 2:
                img = generate_topology_graph(leaf_switch, leaf_count, spine_switch, spine_count,
                                             None, 0, servers, servers_per_rack, idx)
                total_cost = (SWITCHES[leaf_switch]['cost'] * leaf_count +
                             SWITCHES[spine_switch]['cost'] * spine_count)
                results.append({'image': img, 'leaf': leaf_switch, 'leaf_count': leaf_count,
                               'spine': spine_switch, 'spine_count': spine_count,
                               'superspine': None, 'superspine_count': 0, 'total_cost': total_cost})
                idx += 1
            elif tiers == 3:
                total_superspine_ports_needed = spine_count * spine['ports']
                for superspine_switch in SWITCHES.keys():
                    superspine = SWITCHES[superspine_switch]
                    superspine_count = max(1, (total_superspine_ports_needed + superspine['ports'] - 1) // superspine['ports'])
                    superspine_bw = superspine_count * superspine['ports'] * bw_per_server
                    if superspine_bw < spine_bw:
                        continue
                    img = generate_topology_graph(leaf_switch, leaf_count, spine_switch, spine_count,
                                                 superspine_switch, superspine_count, servers, servers_per_rack, idx)
                    total_cost = (SWITCHES[leaf_switch]['cost'] * leaf_count +
                                 SWITCHES[spine_switch]['cost'] * spine_count +
                                 SWITCHES[superspine_switch]['cost'] * superspine_count)
                    results.append({'image': img, 'leaf': leaf_switch, 'leaf_count': leaf_count,
                                   'spine': spine_switch, 'spine_count': spine_count,
                                   'superspine': superspine_switch, 'superspine_count': superspine_count,
                                   'total_cost': total_cost})
                    idx += 1

    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        servers = int(request.form['servers'])
        oversub = float(request.form['oversub'])
        bw_per_server = int(request.form['bw_per_server'])
        tiers = int(request.form['tiers'])
        racks = request.form['racks']
        racks = int(racks) if racks else None

        for f in os.listdir('static'):
            if f.startswith('topology_'):
                os.remove(os.path.join('static', f))

        topologies = calculate_topology(servers, oversub, bw_per_server, tiers, racks)
        return render_template('index.html', topologies=topologies)
    return render_template('index.html', topologies=None)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)