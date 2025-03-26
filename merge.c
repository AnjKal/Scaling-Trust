#include <stdio.h>
#include <stdlib.h>

#define MAX 100

// Function to perform Topological Sort using Vertex Deletion
void topologicalSort(int n, int graph[MAX][MAX]) {
    int in_degree[MAX] = {0};
    int sorted[MAX], index = 0;

    // Calculate in-degree of each vertex
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (graph[j][i] == 1) {
                in_degree[i]++;
            }
        }
    }

    int count = 0;  // Count of visited vertices

    while (count < n) {
        int found = 0;

        for (int i = 0; i < n; i++) {
            if (in_degree[i] == 0) {
                sorted[index++] = i;  // Add to sorted list
                in_degree[i] = -1;    // Mark vertex as visited

                // Reduce in-degree of neighbors
                for (int j = 0; j < n; j++) {
                    if (graph[i][j] == 1) {
                        in_degree[j]--;
                    }
                }

                found = 1;
                count++;
                break;
            }
        }

        // If no vertex with in-degree 0 is found, a cycle is present
        if (!found) {
            printf("\nCycle detected! Topological sort not possible.\n");
            return;
        }
    }

    // Print the topological order
    printf("\nTopological Sort Order: ");
    for (int i = 0; i < index; i++) {
        printf("%d ", sorted[i]);
    }
    printf("\n");
}

int main() {
    int n, e;
    int graph[MAX][MAX] = {0};

    printf("Enter the number of vertices: ");
    scanf("%d", &n);

    printf("Enter the number of edges: ");
    scanf("%d", &e);

    printf("Enter the edges (from -> to):\n");
    for (int i = 0; i < e; i++) {
        int from, to;
        scanf("%d %d", &from, &to);
        graph[from][to] = 1;
    }

    topologicalSort(n, graph);

    return 0;
}
