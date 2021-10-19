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
#include <queue>

using namespace std;

#define n_stickers 54
#define n_edge_stickers 24
#define n_phase0_moves 18
#define n_phase1_moves 10

#define n_phase0_in 78
#define n_phase0_dense0 64
#define n_phase0_dense1 32
#define n_phase0_dense_residual 32
#define n_phase0_n_residual 2

#define n_phase1_in 180
#define n_phase1_dense0 32
#define n_phase1_dense1 32
#define n_phase1_dense_residual 32
#define n_phase1_n_residual 2

/*
sticker numbering
              U
           0  1  2
           3  4  5
           6  7  8
    L         F         R         B
36 37 38   9 10 11  18 19 20  27 28 29
39 40 41  12 13 14  21 22 23  30 31 32
42 43 44  15 16 17  24 25 26  33 34 35
              D
          45 46 47
          48 49 50
          51 52 53
*/

const int edges[n_edge_stickers] = {1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52};
const int sticker_moves[6][5][4] = {
    {{5, 30, 50, 14},  {19, 23, 25, 21}, {2, 33, 47, 11},  {27, 53, 17, 8},  {20, 26, 24, 18}}, // R
    {{3, 12, 48, 32},  {37, 41, 43, 39}, {0, 9, 45, 35},   {6, 15, 51, 29},  {36, 38, 44, 42}}, // L
    {{28, 19, 10, 37}, {1, 5, 7, 3},     {29, 20, 11, 38}, {27, 18, 9, 36},  {0, 2, 8, 6}    }, // U
    {{16, 25, 34, 43}, {46, 50, 52, 48}, {15, 24, 33, 42}, {17, 26, 35, 44}, {45, 47, 53, 51}}, // D
    {{7, 21, 46, 41},  {10, 14, 16, 12}, {6, 18, 47, 44},  {8, 24, 45, 38},  {9, 11, 17, 15} }, // F
    {{1, 39, 52, 23},  {28, 32, 34, 30}, {2, 36, 51, 26},  {0, 42, 53, 20},  {27, 29, 35, 33}}  // B
};
string notation[18] = {"R", "R2", "R'", "L", "L2", "L'", "U", "U2", "U'", "D", "D2", "D'", "F", "F2", "F'", "B", "B2", "B'"};

double phase0_dense0[n_phase0_dense0][n_phase0_in];
double phase0_bias0[n_phase0_dense0];
double phase0_dense1[n_phase0_dense1][n_phase0_dense0];
double phase0_bias1[n_phase0_dense1];
double phase0_dense_residual[n_phase0_n_residual][n_phase0_dense_residual][n_phase0_dense_residual];
double phase0_bias_residual[n_phase0_n_residual][n_phase0_dense_residual];
double phase0_dense2[n_phase0_dense_residual];
double phase0_bias2;
const double solved_phase0[n_phase0_in] = {
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
    1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 
    1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
const int edge_pair[n_stickers] = {-1, 28, -1, 37, -1, 19, -1, 10, -1, -1, 7, -1, 41, -1, 21, -1, 46, -1, -1, 5, -1, 14, -1, 30, -1, 50, -1, -1, 1, -1, 23, -1, 39, -1, 52, -1, -1, 3, -1, 32, -1, 12, -1, 48, -1, -1, 16, -1, 43, -1, 25, -1, 34, -1};

double phase1_dense0[n_phase1_dense0][n_phase1_in];
double phase1_bias0[n_phase1_dense0];
double phase1_dense1[n_phase1_dense1][n_phase1_dense0];
double phase1_bias1[n_phase1_dense1];
double phase1_dense_residual[n_phase1_n_residual][n_phase1_dense_residual][n_phase1_dense_residual];
double phase1_bias_residual[n_phase1_n_residual][n_phase1_dense_residual];
double phase1_dense2[n_phase1_dense_residual];
double phase1_bias2;
const double solved_phase1[n_phase1_in] = {
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
    1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 
    1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
    0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
};
int phase1_move_candidate[10] = {1, 4, 6, 7, 8, 9, 10, 11, 13, 16};


inline long long tim(){
    return chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now().time_since_epoch()).count();
}

inline int calc_face(int mov){
    return mov / 3;
}

inline int calc_axis(int mov){
    return mov / 6;
}

inline double get_element(char *cbuf, FILE *fp){
    if (!fgets(cbuf, 1024, fp)){
        cerr << "param file broken" << endl;
        exit(1);
    }
    return atof(cbuf);
}

inline void init(){
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

    if ((fp = fopen("param/phase1.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_phase1_in; ++i){
        for (j = 0; j < n_phase1_dense0; ++j){
            phase1_dense0[j][i] = get_element(cbuf, fp);
        }
    }
    for (i = 0; i < n_phase1_dense0; ++i)
        phase1_bias0[i] = get_element(cbuf, fp);
    for (i = 0; i < n_phase1_dense0; ++i){
        for (j = 0; j < n_phase1_dense1; ++j){
            phase1_dense1[j][i] = get_element(cbuf, fp);
        }
    }
    for (i = 0; i < n_phase1_dense1; ++i)
        phase1_bias1[i] = get_element(cbuf, fp);
    for (ri = 0; ri < n_phase1_n_residual; ++ri){
        for (i = 0; i < n_phase1_dense_residual; ++i){
            for (j = 0; j < n_phase1_dense_residual; ++j){
                phase1_dense_residual[ri][j][i] = get_element(cbuf, fp);
            }
        }
        for (i = 0; i < n_phase1_dense_residual; ++i)
            phase1_bias_residual[ri][i] = get_element(cbuf, fp);
    }
    for (i = 0; i < n_phase1_dense_residual; ++i)
        phase1_dense2[i] = get_element(cbuf, fp);
    phase1_bias2 = get_element(cbuf, fp);
}

inline void move_sticker(const int stickers[n_stickers], int res[n_stickers], int mov){
    int face, amount, i, j, k;
    int tmp_stickers[n_stickers];
    face = calc_face(mov);
    amount = mov % 3 + 1;
    for (i = 0; i < n_stickers; ++i){
        tmp_stickers[i] = stickers[i];
        res[i] = stickers[i];
    }
    for (i = 0; i < amount; ++i){
        for (j = 0; j < 5; ++j){
            for (k = 0; k < 4; ++k)
                tmp_stickers[sticker_moves[face][j][(k + 1) % 4]] = res[sticker_moves[face][j][k]];
        }
        for (j = 0; j < n_stickers; ++j)
            res[j] = tmp_stickers[j];
    }
}

inline double leaky_relu(double x){
    return max(x, 0.01 * x);
}

inline double predict_phase0(const int stickers[n_stickers]){
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
        if (stickers[edges[i]] == 1 || stickers[edges[i]] == 3){
            if (stickers[edge_pair[edges[i]]] == 0 || stickers[edge_pair[edges[i]]] == 5)
                in_arr[n_stickers + i] = 0.0;
            else
                in_arr[n_stickers + i] = 1.0;
        } else
            in_arr[n_stickers + i] = 0.0;
    }
    bool solved = true;
    for (i = 0; i < n_phase0_in; ++i)
        solved = solved && (in_arr[i] == solved_phase0[i]);
    if (solved)
        return 0.0;

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

inline double predict_phase1(const int stickers[n_stickers]){
    double in_arr[n_phase1_in];
    double hidden0[32], hidden1[32];
    double res;
    int i, j, ri, idx, color;

    // create input array
    idx = 0;
    for (color = 0; color < 6; color += 5){
        for (i = 0; i < 9; ++i){
            if (stickers[i] == color)
                in_arr[idx++] = 1.0;
            else
                in_arr[idx++] = 0.0;
        }
        for (i = 45; i < 54; ++i){
            if (stickers[i] == color)
                in_arr[idx++] = 1.0;
            else
                in_arr[idx++] = 0.0;
        }
    }
    for (color = 1; color < 5; ++color){
        for (i = 9; i < 45; ++i){
            if (stickers[i] == color)
                in_arr[idx++] = 1.0;
            else
                in_arr[idx++] = 0.0;
        }
    }
    bool solved = true;
    for (i = 0; i < n_phase1_in; ++i)
        solved = solved && (in_arr[i] == solved_phase1[i]);
    if (solved)
        return 0.0;

    // dense0
    for (i = 0; i < n_phase1_dense0; ++i){
        hidden0[i] = phase1_bias0[i];
        for (j = 0; j < n_phase1_in; ++j)
            hidden0[i] += phase1_dense0[i][j] * in_arr[j];
        hidden0[i] = leaky_relu(hidden0[i]);
    }

    // dense1
    for (i = 0; i < n_phase1_dense1; ++i){
        hidden1[i] = phase1_bias1[i];
        for (j = 0; j < n_phase1_dense0; ++j)
            hidden1[i] += phase1_dense1[i][j] * hidden0[j];
        hidden1[i] = leaky_relu(hidden1[i]);
    }

    // residual bloock
    for (ri = 0; ri < n_phase1_n_residual; ++ri){
        for (i = 0; i < n_phase1_dense_residual; ++i){
            hidden0[i] = phase1_bias_residual[ri][i] + hidden1[i];
            for (j = 0; j < n_phase1_dense_residual; ++j)
                hidden0[i] += phase1_dense_residual[ri][i][j] * hidden1[j];
            hidden0[i] = leaky_relu(hidden0[i]);
        }
        swap(hidden0, hidden1);
    }

    // dense2
    res = phase1_bias2;
    for (j = 0; j < n_phase1_dense_residual; ++j)
        res += phase1_dense2[j] * hidden1[j];
    return res;
}


struct a_star_elem{
    double f;
    int stickers[n_stickers];
    vector<int> solution;
};

bool operator< (const a_star_elem &a, const a_star_elem &b){
    return a.f > b.f;
};

vector<int> phase0(int stickers[n_stickers]){
    int i, mov, sol_size;
    double dis;
    priority_queue<a_star_elem> que;
    a_star_elem first_elem, elem;
    vector<int> res;
    for (i = 0; i < n_stickers; ++i)
        first_elem.stickers[i] = stickers[i];
    first_elem.f = predict_phase0(first_elem.stickers);
    if (first_elem.f == 0.0)
        return res;
    first_elem.solution.push_back(-1000);
    que.push(first_elem);
    while (que.size()){
        elem = que.top();
        que.pop();
        sol_size = elem.solution.size();
        for (mov = 0; mov < n_phase0_moves; ++mov){
            if (calc_face(mov) == calc_face(elem.solution[sol_size - 1]))
                continue;
            if (calc_axis(mov) == calc_axis(elem.solution[sol_size - 1]) && mov < elem.solution[sol_size - 1])
                continue;
            a_star_elem n_elem;
            move_sticker(elem.stickers, n_elem.stickers, mov);
            dis = predict_phase0(n_elem.stickers);
            n_elem.f = sol_size + dis;
            for (i = 0; i < sol_size; ++i)
                n_elem.solution.push_back(elem.solution[i]);
            n_elem.solution.push_back(mov);
            if (dis == 0){
                for (i = 1; i < (int)n_elem.solution.size(); ++i)
                    res.push_back(n_elem.solution[i]);
                return res;
            }
            que.push(n_elem);
        }
    }
    res.push_back(-1);
    return res;
}

vector<int> phase1(int stickers[n_stickers]){
    int i, mov, mov_idx, sol_size;
    double dis;
    priority_queue<a_star_elem> que;
    a_star_elem first_elem, elem;
    vector<int> res;
    for (i = 0; i < n_stickers; ++i)
        first_elem.stickers[i] = stickers[i];
    first_elem.f = predict_phase1(first_elem.stickers);
    if (first_elem.f == 0.0)
        return res;
    first_elem.solution.push_back(-1000);
    que.push(first_elem);
    while (que.size()){
        elem = que.top();
        que.pop();
        sol_size = elem.solution.size();
        for (mov_idx = 0; mov_idx < n_phase1_moves; ++mov_idx){
            mov = phase1_move_candidate[mov_idx];
            if (calc_face(mov) == calc_face(elem.solution[sol_size - 1]))
                continue;
            if (calc_axis(mov) == calc_axis(elem.solution[sol_size - 1]) && mov < elem.solution[sol_size - 1])
                continue;
            a_star_elem n_elem;
            move_sticker(elem.stickers, n_elem.stickers, mov);
            dis = predict_phase1(n_elem.stickers);
            n_elem.f = sol_size + dis;
            for (i = 0; i < sol_size; ++i)
                n_elem.solution.push_back(elem.solution[i]);
            n_elem.solution.push_back(mov);
            if (dis == 0){
                for (i = 1; i < (int)n_elem.solution.size(); ++i)
                    res.push_back(n_elem.solution[i]);
                return res;
            }
            que.push(n_elem);
        }
    }
    res.push_back(-1);
    return res;
}

vector<int> solver(const int stickers[n_stickers]){
    int tmp_stickers0[n_stickers], tmp_stickers1[n_stickers];
    int i, j;
    
    for (i = 0; i < n_stickers; ++i)
        tmp_stickers0[i] = stickers[i];
    vector<int> solution0 = phase0(tmp_stickers0);
    
    cerr << " phase0 ";
    for (i = 0; i < (int)solution0.size(); ++i){
        cerr << notation[solution0[i]] << " ";
    }
    cerr << endl;

    for (i = 0; i < (int)solution0.size(); ++i){
        move_sticker(tmp_stickers0, tmp_stickers1, solution0[i]);
        //swap(tmp_stickers0, tmp_stickers1);
        for (j = 0; j < n_stickers; ++j)
            tmp_stickers0[j] = tmp_stickers1[j];
    }
    vector<int> solution1 = phase1(tmp_stickers0);
    
    cerr << " phase1 ";
    for (i = 0; i < (int)solution1.size(); ++i){
        cerr << notation[solution1[i]] << " ";
    }
    cerr << endl;
    
    for (i = 0; i < (int)solution1.size(); ++i)
        solution0.push_back(solution1[i]);
    return solution0;
}

int main(){
    init();
    int stickers[n_stickers] = {5, 2, 2, 4, 0, 5, 0, 5, 1, 4, 1, 5, 3, 1, 0, 1, 5, 1, 2, 3, 5, 3, 2, 4, 0, 5, 2, 3, 1, 1, 1, 3, 0, 0, 2, 3, 4, 3, 3, 4, 4, 2, 4, 1, 0, 4, 4, 2, 0, 5, 2, 5, 0, 3};
    string scramble = "L B2 L2 D2 B L2 F' U2 R2 U2 F2 R2 U' F L2 B' D U2 R U2";
    //int stickers[n_stickers] = {4, 5, 1, 5, 0, 0, 5, 3, 4, 1, 5, 0, 2, 1, 1, 1, 3, 3, 3, 3, 2, 4, 2, 2, 4, 1, 2, 0, 4, 5, 1, 3, 0, 0, 1, 5, 1, 2, 2, 4, 4, 3, 2, 0, 0, 4, 4, 5, 2, 5, 0, 3, 5, 3};
    //string scramble = "L U2 F2 R' U2 B2 R' D2 L2 F2 U2 D R' F' D' F2 R B2 U";
    //cerr << predict_phase0(stickers) << endl;
    cerr << "scramble: " << scramble << endl;
    cerr << "start!" << endl;
    long long strt = tim();
    vector<int> solution = solver(stickers);
    cerr << "solved! in " << tim() - strt << " ms" << endl;
    cerr << "length " << solution.size() << endl;
    for (int i = 0; i < (int)solution.size(); ++i){
        cerr << notation[solution[i]] << " ";
    }
    cerr << endl;
    return 0;
}
