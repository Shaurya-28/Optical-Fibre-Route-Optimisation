#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <fstream>

using namespace std;

const int INF = numeric_limits<int>::max();

vector<vector<pair<int, int>>> adj;  // Adjacency list

int primMST(int n, vector<pair<int, int>> &mstEdges) {
    vector<bool> inMST(n, false);
    vector<int> key(n, INF);
    vector<int> parent(n, -1);
    int totalWeight = 0;

    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> pq;
    key[0] = 0;
    pq.push({0, 0}); // {weight, node}

    while (!pq.empty()) {
        int u = pq.top().second;
        pq.pop();

        if (inMST[u]) continue;
        inMST[u] = true;
        totalWeight += key[u];

        if (parent[u] != -1) {
            mstEdges.push_back({parent[u], u});
        }

        for (auto &[v, weight] : adj[u]) {
            if (!inMST[v] && weight < key[v]) {
                key[v] = weight;
                pq.push({key[v], v});
                parent[v] = u;
            }
        }
    }

    return totalWeight;
}

int main() {
    int n, m;
    ifstream infile("data/graph.txt");
    infile >> n >> m;

    adj.resize(n);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        infile >> u >> v >> w;
        adj[u].emplace_back(v, w);
        adj[v].emplace_back(u, w);  // Undirected graph
    }

    vector<pair<int, int>> mstEdges;
    int totalWeight = primMST(n, mstEdges);

    ofstream outfile("data/output.txt");
    for (auto &[u, v] : mstEdges) {
        outfile << u << " - " << v << "\n";
    }

    return 0;
}