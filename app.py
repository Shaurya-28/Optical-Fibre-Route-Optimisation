from flask import Flask, render_template, request
import folium
import heapq
import os

app = Flask(__name__)

# Coordinates of the places
places = {
    'Dehradun': [30.3165, 78.0322],
    'Rishikesh': [30.0869, 78.2676],
    'Haridwar': [29.9457, 78.1642],
    'Mussoorie': [30.4583, 78.0700]
}

# Distance matrix (undirected graph)
distance_data = {
    ('Dehradun', 'Rishikesh'): 20,
    ('Dehradun', 'Haridwar'): 50,
    ('Dehradun', 'Mussoorie'): 35,
    ('Rishikesh', 'Haridwar'): 30,
    ('Rishikesh', 'Mussoorie'): 45,
    ('Haridwar', 'Mussoorie'): 60
}

# Add reverse edges
for (a, b), d in list(distance_data.items()):
    distance_data[(b, a)] = d

# Places for Prim's algorithm (Dehradun localities)
prim_places = {
    'Rajpur': [30.3265, 78.0722],          # North Dehradun
    'Mussoorie Diversion': [30.3165, 78.0322],  # Central Dehradun
    'Dalanwala': [30.2865, 78.0122],       # South Dehradun
    'Raipur': [30.3365, 78.0922]           # East Dehradun
}

# Distance matrix for Prim's algorithm (in kilometers)
prim_distance_data = {
    ('Rajpur', 'Mussoorie Diversion'): 4.5,    # North-Central route
    ('Rajpur', 'Dalanwala'): 6.7,              # North-South route
    ('Rajpur', 'Raipur'): 2.8,                 # North-East route
    ('Mussoorie Diversion', 'Dalanwala'): 3.8, # Central-South route
    ('Mussoorie Diversion', 'Raipur'): 5.2,    # Central-East route
    ('Dalanwala', 'Raipur'): 7.3               # South-East route
}

# Add reverse edges for Prim's algorithm
for (a, b), d in list(prim_distance_data.items()):
    prim_distance_data[(b, a)] = d

@app.route('/')
def index():
    return render_template('index.html', places=places.keys(), prim_places=prim_places.keys())


@app.route('/map')
def map_page():
    # Create map centered at Dehradun
    map_ = folium.Map(location=places['Dehradun'], zoom_start=11)

    # Add location markers
    for place, coords in places.items():
        folium.Marker(coords, popup=place).add_to(map_)

    # Save map HTML
    map_.save(os.path.join('templates', 'map.html'))

    # Render the saved map
    return render_template('map.html')

@app.route('/dijkstra', methods=['POST'])
def dijkstra_route():
    source = request.form['source']
    distances = {place: float('inf') for place in places}
    distances[source] = 0
    pq = [(0, source)]
    visited = set()
    # Track predecessors for path reconstruction
    predecessors = {place: None for place in places}

    while pq:
        current_distance, current_place = heapq.heappop(pq)
        if current_place in visited:
            continue
        visited.add(current_place)

        for neighbor in places:
            if (current_place, neighbor) in distance_data:
                new_dist = current_distance + distance_data[(current_place, neighbor)]
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current_place
                    heapq.heappush(pq, (new_dist, neighbor))

    # Reconstruct shortest paths
    shortest_paths = {}
    for dest in places:
        if dest != source:
            path = []
            current = dest
            while current is not None:
                path.append(current)
                current = predecessors[current]
            path.reverse()
            shortest_paths[dest] = path

    # Format location data for the map
    location_data = {place: {"lat": coords[0], "lng": coords[1]} for place, coords in places.items()}
    
    # Format distance data for JavaScript
    formatted_distance_data = {}
    for (place1, place2), dist in distance_data.items():
        formatted_distance_data[f"{place1},{place2}"] = dist
    
    result = {place: dist for place, dist in distances.items() if place != source}
    return render_template('dijkstra_result.html', 
                         source=source, 
                         distances=result,
                         location_data=location_data,
                         shortest_paths=shortest_paths,
                         distance_data=formatted_distance_data)

@app.route('/prim', methods=['POST'])
def prim_route():
    source = request.form['source']
    visited = set([source])
    edges = []
    mst = []
    total_weight = 0
    # Track predecessors for path reconstruction
    predecessors = {place: None for place in prim_places}
    # Track paths from source to each node
    paths = {place: [] for place in prim_places}
    paths[source] = [source]

    # Initialize edges from source
    for neighbor in prim_places:
        if (source, neighbor) in prim_distance_data:
            edges.append((prim_distance_data[(source, neighbor)], source, neighbor))

    heapq.heapify(edges)

    while edges and len(visited) < len(prim_places):
        weight, frm, to = heapq.heappop(edges)
        if to in visited:
            continue
        visited.add(to)
        mst.append((frm, to, weight))
        total_weight += weight
        predecessors[to] = frm
        # Update path for the new node
        paths[to] = paths[frm] + [to]

        for neighbor in prim_places:
            if neighbor not in visited and (to, neighbor) in prim_distance_data:
                heapq.heappush(edges, (prim_distance_data[(to, neighbor)], to, neighbor))

    # Format location data for the map
    location_data = {place: {"lat": coords[0], "lng": coords[1]} for place, coords in prim_places.items()}
    
    # Format distance data for JavaScript
    formatted_distance_data = {}
    for (place1, place2), dist in prim_distance_data.items():
        formatted_distance_data[f"{place1},{place2}"] = dist

    return render_template('prim_result.html', 
                         source=source,
                         mst=mst, 
                         total_weight=total_weight,
                         location_data=location_data,
                         paths=paths,
                         distance_data=formatted_distance_data)

if __name__ == '__main__':
    app.run(debug=True)
