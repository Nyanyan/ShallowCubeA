#pragma GCC target("avx2")
#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")
#pragma GCC target("sse,sse2,sse3,ssse3,sse4,popcnt,abm,mmx")

// Egaroucid2

#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>
#include <chrono>
#include <string>
#include <unordered_map>
#include <random>

using namespace std;

#define n_stickers 54
#define n_edge_stickers 24

#define n_phase0_in 78
#define n_phase0_dense0 64
#define n_phase0_dense1 32
#define n_phase0_dense_residual 32
#define n_phase0_n_residual 2

const int edges[n_edge_stickers] = {1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52};

double phase0_dense0[n_phase0_dense0][n_phase0_in];
double phase0_bias0[n_phase0_dense0];
double phase0_dense1[n_phase0_dense1][n_phase0_dense0];
double phase0_bias1[n_phase0_dense1];
double phase0_dense_residual[n_phase0_n_residual][n_phase0_dense_residual][n_phase0_dense_residual];
double phase0_bias_residual[n_phase0_n_residual][n_phase0_dense_residual];
double phase0_dense2[n_phase0_dense_residual];
double phase0_bias2;


inline long long tim(){
    return chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now().time_since_epoch()).count();
}

inline double get_element(char *cbuf, FILE *fp){
    if (!fgets(cbuf, 1024, fp)){
        cerr << "param file broken" << endl;
        exit(1);
    }
    return atof(cbuf);
}

inline void init(){
    cerr << "initializing" << endl;
    int i, j, ri;
    FILE *fp;
    char cbuf[1024];
    if ((fp = fopen("param/phase0.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_phase0_in; ++i){
        for (j = 0; j < n_phase0_dense0; ++j){
            phase0_dense0[j][i] = get_element(cbuf, fp);
        }
    }
    for (i = 0; i < n_phase0_dense0; ++i)
        phase0_bias0[i] = get_element(cbuf, fp);
    for (i = 0; i < n_phase0_dense0; ++i){
        for (j = 0; j < n_phase0_dense1; ++j){
            phase0_dense1[j][i] = get_element(cbuf, fp);
        }
    }
    for (i = 0; i < n_phase0_dense1; ++i)
        phase0_bias1[i] = get_element(cbuf, fp);
    for (ri = 0; ri < n_phase0_n_residual; ++ri){
        for (i = 0; i < n_phase0_dense_residual; ++i){
            for (j = 0; j < n_phase0_dense_residual; ++j){
                phase0_dense_residual[ri][j][i] = get_element(cbuf, fp);
            }
        }
        for (i = 0; i < n_phase0_dense_residual; ++i)
            phase0_bias_residual[ri][i] = get_element(cbuf, fp);
    }
    for (i = 0; i < n_phase0_dense_residual; ++i)
        phase0_dense2[i] = get_element(cbuf, fp);
    phase0_bias2 = get_element(cbuf, fp);
}

inline double leaky_relu(double x){
    return max(x, 0.01 * x);
}

inline double predict_phase0(int stickers[n_stickers]){
    double in_arr[n_phase0_in];
    double hidden0[64], hidden1[64];
    double res;
    int i, j, ri;
    // create input array
    for (i = 0; i < n_stickers; ++i){
        if (stickers[i] == 0 || stickers[i] == 5)
            in_arr[i] = 1.0;
        else
            in_arr[i] = 0.0;
    }
    for (i = 0; i < n_edge_stickers; ++i){
        if (stickers[edges[i]] == 1 || stickers[edges[i]] == 3)
            in_arr[n_stickers + i] = 1.0;
        else
            in_arr[n_stickers + i] = 0.0;
    }

    for (i = 0; i < n_phase0_in; ++i){
        cerr << in_arr[i] << " ";
        if (i % 10 == 9)
            cerr << endl;
    }
    cerr << endl;

    // dense0
    for (i = 0; i < n_phase0_dense0; ++i){
        hidden0[i] = phase0_bias0[i];
        for (j = 0; j < n_phase0_in; ++j)
            hidden0[i] += phase0_dense0[i][j] * in_arr[j];
        hidden0[i] = leaky_relu(hidden0[i]);
    }

    // dense1
    for (i = 0; i < n_phase0_dense1; ++i){
        hidden1[i] = phase0_bias1[i];
        for (j = 0; j < n_phase0_dense0; ++j)
            hidden1[i] += phase0_dense1[i][j] * hidden0[j];
        hidden1[i] = leaky_relu(hidden1[i]);
    }

    // residual bloock
    for (ri = 0; ri < n_phase0_n_residual; ++ri){
        for (i = 0; i < n_phase0_dense_residual; ++i){
            hidden0[i] = phase0_bias_residual[ri][i] + hidden1[i];
            for (j = 0; j < n_phase0_dense_residual; ++j)
                hidden0[i] += phase0_dense_residual[ri][i][j] * hidden1[j];
            hidden0[i] = leaky_relu(hidden0[i]);
        }
        swap(hidden0, hidden1);
    }

    // dense2
    res = phase0_bias2;
    for (j = 0; j < n_phase0_dense_residual; ++j)
        res += phase0_dense2[j] * hidden1[j];
    return res;
}

int main(){
    init();
    int stickers[n_stickers] = {5, 2, 2, 4, 0, 5, 0, 5, 1, 4, 1, 5, 3, 1, 0, 1, 5, 1, 2, 3, 5, 3, 2, 4, 0, 5, 2, 3, 1, 1, 1, 3, 0, 0, 2, 3, 4, 3, 3, 4, 4, 2, 4, 1, 0, 4, 4, 2, 0, 5, 2, 5, 0, 3};
    cerr << "start!" << endl;
    cerr << predict_phase0(stickers) << endl;
}
