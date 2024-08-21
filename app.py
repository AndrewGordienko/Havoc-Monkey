import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import plotly.graph_objs as go
import threading
import random
import os
import time
import netifaces
from scapy.all import sniff, AsyncSniffer

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Chaos Monkey Network Visualization"

# Global variables to store packet counts, logs, and metrics
packet_data = {'tcp': 0, 'udp': 0, 'other': 0}
chaos_log = []
network_latency = []
packet_loss = []

# Define layout of the dashboard
app.layout = html.Div([
    html.H1("Chaos Monkey Network Visualization", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        html.P("Welcome to the Chaos Monkey Network Visualization. This tool simulates network disturbances and tracks their impact in real-time. Below, you can choose a network interface, inject chaos, and observe the effects."),
        html.P("Use the network diagram below to visualize connections between devices. You can click on nodes (representing devices) or edges (representing connections) to simulate disruptions."),
        html.P("Instructions:"),
        html.Ul([
            html.Li("Click on a node to simulate disabling/enabling a device."),
            html.Li("Click on an edge to simulate a network connection disruption."),
            html.Li("Use the dropdown and button below to trigger specific types of chaos.")
        ]),
    ], style={'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '5px', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='latency-graph', style={'width': '32%', 'display': 'inline-block'}),
        dcc.Graph(id='packet-loss-graph', style={'width': '32%', 'display': 'inline-block'}),
        dcc.Graph(id='traffic-graph', style={'width': '32%', 'display': 'inline-block'}),
    ]),
    
    cyto.Cytoscape(
        id='network-topology',
        layout={'name': 'preset'},
        style={'width': '80%', 'height': '400px', 'margin': 'auto', 'border': '1px solid #ccc', 'padding': '10px'},
        elements=[],
        zoomingEnabled=False,
        userPanningEnabled=False,
    ),
    
    html.Div([
        dcc.Slider(
            id='device-count-slider',
            min=2,
            max=10,
            value=3,
            marks={i: str(i) for i in range(2, 11)},
            step=1,
        ),
        html.P("Select the number of devices:", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='chaos-type',
            options=[
                {'label': 'Disable/Enable Random Interface', 'value': 'interface'},
                {'label': 'Inject Packet Loss', 'value': 'packet_loss'},
                {'label': 'Inject Latency', 'value': 'latency'},
            ],
            value='interface',
            style={'width': '50%', 'margin': 'auto', 'marginBottom': '20px'}
        ),
        html.Button('Trigger Chaos', id='trigger-chaos', n_clicks=0, style={
            'width': '50%', 'padding': '10px', 'fontSize': '18px', 
            'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
            'borderRadius': '5px', 'cursor': 'pointer', 'margin': 'auto', 'display': 'block',
            'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'
        }),
    ], style={'padding': '20px', 'textAlign': 'center'}),
    
    html.H2("Chaos Events Log", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Div(id='chaos-log', style={'whiteSpace': 'pre-line', 'padding': '10px', 'backgroundColor': '#ecf0f1', 'borderRadius': '5px'}),
    
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#bdc3c7', 'padding': '20px'})

def update_packet_data(packet):
    if packet.haslayer("IP"):
        if packet.haslayer("TCP"):
            packet_data['tcp'] += 1
        elif packet.haslayer("UDP"):
            packet_data['udp'] += 1
        else:
            packet_data['other'] += 1

def packet_callback(packet):
    update_packet_data(packet)

def start_sniffing():
    sniffer = AsyncSniffer(prn=packet_callback)
    sniffer.start()

class ChaosMonkeyNetwork:
    def __init__(self):
        self.interfaces = self.list_interfaces()

    def list_interfaces(self):
        interfaces = netifaces.interfaces()
        return [iface for iface in interfaces if self.has_ipv4(iface)]

    def has_ipv4(self, interface):
        addrs = netifaces.ifaddresses(interface)
        return netifaces.AF_INET in addrs

    def get_interface_name(self, interface):
        names = {
            'lo0': 'Loopback Interface (lo0)',
            'en0': 'Ethernet Interface (en0)',
            'en1': 'Ethernet Interface (en1)',
        }
        return names.get(interface, interface)

    def select_random_interface(self):
        return random.choice(self.interfaces)

    def disable_interface(self, interface):
        os.system(f"sudo ifconfig {interface} down")
        self.log_event(f"Disabled {self.get_interface_name(interface)}")

    def enable_interface(self, interface):
        os.system(f"sudo ifconfig {interface} up")
        self.log_event(f"Re-enabled {self.get_interface_name(interface)}")

    def inject_packet_loss(self):
        self.log_event("Injected packet loss.")
        packet_loss.append(random.uniform(1, 5))

    def inject_latency(self):
        self.log_event("Injected network latency.")
        network_latency.append(random.uniform(50, 200))

    def random_wait_time(self, min_seconds=1, max_seconds=10):
        return random.uniform(min_seconds, max_seconds)

    def log_event(self, event):
        chaos_log.append(event)
        if len(chaos_log) > 20:
            chaos_log.pop(0)

    def run_once(self, chaos_type):
        if chaos_type == 'interface':
            random_interface = self.select_random_interface()
            self.log_event(f"Selected {self.get_interface_name(random_interface)}")

            wait_time = self.random_wait_time(5, 15)
            time.sleep(wait_time)

            self.disable_interface(random_interface)

            wait_time = self.random_wait_time(5, 15)
            time.sleep(wait_time)

            self.enable_interface(random_interface)
        elif chaos_type == 'packet_loss':
            self.inject_packet_loss()
        elif chaos_type == 'latency':
            self.inject_latency()

def run_chaos(chaos_type):
    threading.Thread(target=chaos_monkey.run_once, args=(chaos_type,)).start()

@app.callback(
    [Output('latency-graph', 'figure'),
     Output('packet-loss-graph', 'figure'),
     Output('traffic-graph', 'figure'),
     Output('network-topology', 'elements'),
     Output('chaos-log', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('trigger-chaos', 'n_clicks'),
     Input('network-topology', 'tapNodeData'),
     Input('network-topology', 'tapEdgeData')],
    [State('chaos-type', 'value'),
     State('device-count-slider', 'value')]
)
def update_dashboard(n, n_clicks, node_data, edge_data, chaos_type, device_count):
    triggered = dash.callback_context.triggered

    # Generate network elements based on the number of devices
    elements = [{'data': {'id': 'Router', 'label': 'Router'}, 'position': {'x': 100, 'y': 100}}]
    for i in range(1, device_count + 1):
        device_id = f'Device{i}'
        position = {'x': 100 + i * 100, 'y': 100 + (i % 2) * 100}
        elements.append({'data': {'id': device_id, 'label': device_id}, 'position': position})
        elements.append({'data': {'source': 'Router', 'target': device_id}, 'classes': 'topology-edge'})

    if 'trigger-chaos' in triggered[0]['prop_id']:
        run_chaos(chaos_type)

    if node_data:
        for element in elements:
            if 'id' in element['data'] and element['data']['id'] == node_data['id']:
                element['classes'] = 'node-chaos'

    if edge_data:
        for element in elements:
            if element['data'].get('source') == edge_data['source'] and element['data'].get('target') == edge_data['target']:
                element['classes'] = 'edge-chaos'

    latency_fig = {
        'data': [go.Scatter(x=list(range(len(network_latency))), y=network_latency, mode='lines+markers')],
        'layout': go.Layout(
            title='Network Latency Over Time',
            yaxis={'title': 'Latency (ms)'},
            plot_bgcolor='#ecf0f1',
            paper_bgcolor='#bdc3c7',
            font={'color': '#2c3e50'}
        )
    }

    packet_loss_fig = {
        'data': [go.Scatter(x=list(range(len(packet_loss))), y=packet_loss, mode='lines+markers')],
        'layout': go.Layout(
            title='Packet Loss Over Time',
            yaxis={'title': 'Packet Loss (%)'},
            plot_bgcolor='#ecf0f1',
            paper_bgcolor='#bdc3c7',
            font={'color': '#2c3e50'}
        )
    }

    trace_tcp = go.Bar(
        x=['TCP'], y=[packet_data['tcp']],
        name='TCP', marker={'color': '#3498db'}
    )
    trace_udp = go.Bar(
        x=['UDP'], y=[packet_data['udp']],
        name='UDP', marker={'color': '#2ecc71'}
    )
    trace_other = go.Bar(
        x=['Other'], y=[packet_data['other']],
        name='Other', marker={'color': '#e74c3c'}
    )

    traffic_fig = {
        'data': [trace_tcp, trace_udp, trace_other],
        'layout': go.Layout(
            title='Network Traffic (Packet Types)',
            barmode='group',
            yaxis={'title': 'Packet Count'},
            plot_bgcolor='#ecf0f1',
            paper_bgcolor='#bdc3c7',
            font={'color': '#2c3e50'}
        )
    }

    log_output = "\n".join(chaos_log)

    return latency_fig, packet_loss_fig, traffic_fig, elements, log_output

if __name__ == '__main__':
    chaos_monkey = ChaosMonkeyNetwork()
    threading.Thread(target=start_sniffing).start()
    app.run_server(debug=True, port=5001)
