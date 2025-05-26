#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <fstream>

using namespace std;

const int INF = numeric_limits<int>::max();

vector<vector<pair<int, int>>> adj;
vector<int> dist;

void dijkstra(int source, int n) {
    dist.assign(n, INF);
    dist[source] = 0;
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> pq;
    pq.push({0, source});

    while (!pq.empty()) {
        int d = pq.top().first;
        int u = pq.top().second;
        pq.pop();

        if (d > dist[u]) continue;

        for (auto &edge : adj[u]) {
            int v = edge.first;
            int weight = edge.second;

            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                pq.push({dist[v], v});
            }
        }
    }
}

int main() {
    int n, m, source;
    ifstream infile("data/graph.txt");
    infile >> n >> m >> source;

    adj.resize(n);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        infile >> u >> v >> w;
        adj[u].emplace_back(v, w);
        adj[v].emplace_back(u, w);  // Assuming undirected graph
    }

    dijkstra(source, n);

    ofstream outfile("data/output.txt");
    for (int i = 0; i < n; ++i) {
        outfile << dist[i] << " ";
    }
    return 0;
}
