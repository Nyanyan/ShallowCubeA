#pragma GCC target("avx2")
#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")
#pragma GCC target("sse,sse2,sse3,ssse3,sse4,popcnt,abm,mmx")

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

#define c_h 1.1
#define table_weight 0.0
#define threshold 1.75

#define n_stickers 54
#define n_moves 18

#define n_in 328
#define n_dense0 256
#define n_dense1 128
#define n_dense_residual 128
#define n_residual 4

#define n_idxes 5
#define n_colors 6
#define n_corners 8
#define n_edges 12
#define n_co 2187
#define n_cp 40320
#define n_ep 19958400
#define n_eo 1024
#define n_dr 24

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

const int sticker_moves[6][8][4] = {
    {{5, 30, 50, 14},  {19, 23, 25, 21}, {2, 33, 47, 11},  {27, 53, 17, 8},  {20, 26, 24, 18}, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {-1, -1, -1, -1}}, // R
    {{3, 12, 48, 32},  {37, 41, 43, 39}, {0, 9, 45, 35},   {6, 15, 51, 29},  {36, 38, 44, 42}, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {-1, -1, -1, -1}}, // L
    {{16, 25, 34, 43}, {46, 50, 52, 48}, {15, 24, 33, 42}, {17, 26, 35, 44}, {45, 47, 53, 51}, {12, 21, 30, 39}, {13, 22, 31, 40}, {14, 23, 32, 41}}, // Dw
    {{16, 25, 34, 43}, {46, 50, 52, 48}, {15, 24, 33, 42}, {17, 26, 35, 44}, {45, 47, 53, 51}, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {-1, -1, -1, -1}}, // D
    {{7, 21, 46, 41},  {10, 14, 16, 12}, {6, 18, 47, 44},  {8, 24, 45, 38},  {9, 11, 17, 15} , {-1, -1, -1, -1}, {-1, -1, -1, -1}, {-1, -1, -1, -1}}, // F
    {{7, 21, 46, 41},  {10, 14, 16, 12}, {6, 18, 47, 44},  {8, 24, 45, 38},  {9, 11, 17, 15} , {3, 19, 50, 43}, {4, 22, 49, 40}, {5, 25, 48, 37}}     // Fw
};
const int sticker_move_nums[6] = {5, 5, 8, 5, 5, 8};
const string notation[18] = {"R", "R2", "R'", "L", "L2", "L'", "Dw", "Dw2", "Dw'", "D", "D2", "D'", "F", "F2", "F'", "Fw", "Fw2", "Fw'"};
const int corner_places[n_corners][3] = {{0, 36, 29}, {2, 27, 20}, {8, 18, 11}, {6, 9, 38}, {45, 44, 15}, {47, 17, 24}, {53, 26, 33}, {51, 35, 42}};
const int corner_colors[n_corners][3] = {{0, 4, 3},   {0, 3, 2},   {0, 2, 1},   {0, 1, 4},  {5, 4, 1},    {5, 1, 2},    {5, 2, 3},    {5, 3, 4}   };
const int edge_places[n_edges][2] = {{1, 28}, {5, 19}, {7, 10}, {3, 37}, {46, 16}, {50, 25}, {52, 34}, {48, 43}, {12, 41}, {14, 21}, {30, 23}, {32, 39}};
const int edge_colors[n_edges][2] = {{0, 3},  {0, 2},  {0, 1},  {0, 4},  {5, 1},   {5, 2},   {5, 3},   {5, 4},   {1, 4},   {1, 2},   {3, 2},   {3, 4}  };
const int drs[6][6] = {{-1, 0, 4, 8, 12, -1}, {18, -1, 5, -1, 15, 20}, {19, 3, -1, 9, -1, 23}, {16, -1, 7, -1, 13, 22}, {17, 1, -1, 11, -1, 21}, {-1, 2, 6, 10, 14, -1}};

double dense0[n_dense0][n_in];
double bias0[n_dense0];
double dense1[n_dense1][n_dense0];
double bias1[n_dense1];
double dense_residual[n_residual][n_dense_residual][n_dense_residual];
double bias_residual[n_residual][n_dense_residual];
double dense2[n_dense_residual];
double bias2;

double prune_cp_eo[n_cp][n_eo];
double prune_co_eo_dr[n_co][n_eo][n_dr];
double prune_ep[n_ep];
double prune_cp_dr[n_cp][n_dr];

int fac[13];

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
    int i, j, k, ri;
    FILE *fp;
    char cbuf[1024];
    if ((fp = fopen("param/model.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_in; ++i){
        for (j = 0; j < n_dense0; ++j){
            dense0[j][i] = get_element(cbuf, fp);
        }
    }
    for (i = 0; i < n_dense0; ++i)
        bias0[i] = get_element(cbuf, fp);
    for (i = 0; i < n_dense0; ++i){
        for (j = 0; j < n_dense1; ++j){
            dense1[j][i] = get_element(cbuf, fp);
        }
    }
    for (i = 0; i < n_dense1; ++i)
        bias1[i] = get_element(cbuf, fp);
    for (ri = 0; ri < n_residual; ++ri){
        for (i = 0; i < n_dense_residual; ++i){
            for (j = 0; j < n_dense_residual; ++j){
                dense_residual[ri][j][i] = get_element(cbuf, fp);
            }
        }
        for (i = 0; i < n_dense_residual; ++i)
            bias_residual[ri][i] = get_element(cbuf, fp);
    }
    for (i = 0; i < n_dense_residual; ++i)
        dense2[i] = get_element(cbuf, fp);
    bias2 = get_element(cbuf, fp);

    if ((fp = fopen("param/prune_cp_eo.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_cp; ++i){
        if ((i & 0b1111111111) == 0b1111111111)
            cerr << "\rreading 1/4 " << 100.0 * (double)i / n_cp << " persent        ";
        for (j = 0; j < n_eo; ++j)
            prune_cp_eo[i][j] = get_element(cbuf, fp);
    }
    cerr << endl;
    if ((fp = fopen("param/prune_co_eo_dr.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_co; ++i){
        if ((i & 0b11111) == 0b11111)
            cerr << "\rreading 2/4 " << 100.0 * (double)i / n_co << " persent        ";
        for (j = 0; j < n_eo; ++j){
            for (k = 0; k < n_dr; ++k)
                prune_co_eo_dr[i][j][k] = get_element(cbuf, fp);
        }
    }
    cerr << endl;
    if ((fp = fopen("param/prune_ep.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_ep; ++i){
        if ((i & 0b111111111111) == 0b111111111111)
            cerr << "\rreading 3/4 " << 100.0 * (double)i / n_ep << " persent        ";
        prune_ep[i] = get_element(cbuf, fp);
    }
    cerr << endl;
    if ((fp = fopen("param/prune_cp_dr.txt", "r")) == NULL){
        printf("param file not exist");
        exit(1);
    }
    for (i = 0; i < n_cp; ++i){
        if ((i & 0b1111111111) == 0b1111111111)
            cerr << "\rreading 4/4 " << 100.0 * (double)i / n_cp << " persent        ";
        for (j = 0; j < n_dr; ++j)
            prune_cp_dr[i][j] = get_element(cbuf, fp);
    }
    cerr << endl;
    fac[0] = 1;
    for (i = 1; i < 13; ++i)
        fac[i] = fac[i - 1] * i;
}

inline void sticker2arr(const int stickers[n_stickers], int co[n_corners], int cp[n_corners], int eo[n_edges], int ep[n_edges], int *res_dr){
    int i, place, part, dr, sticker;
    bool flag;
    int part_color_corner[3];
    int part_color_edge[2];
    for (place = 0; place < n_corners; ++place){
        for (i = 0; i < 3; ++i)
            part_color_corner[i] = stickers[corner_places[place][i]];
        for (part = 0; part < n_corners; ++part){
            for (dr = 0; dr < 3; ++dr){
                flag = true;
                for (sticker = 0; sticker < 3; ++sticker)
                    flag = flag && part_color_corner[sticker] == corner_colors[part][(sticker - dr + 3) % 3];
                if (flag){
                    cp[place] = part;
                    co[place] = dr;
                }
            }
        }
    }
    for (place = 0; place < n_edges; ++place){
        for (i = 0; i < 2; ++i)
            part_color_edge[i] = stickers[edge_places[place][i]];
        for (part = 0; part < n_edges; ++part){
            for (dr = 0; dr < 2; ++dr){
                flag = true;
                for (sticker = 0; sticker < 2; ++sticker)
                    flag = flag && part_color_edge[sticker] == edge_colors[part][(sticker - dr + 2) % 2];
                if (flag){
                    ep[place] = part;
                    eo[place] = dr;
                }
            }
        }
    }
    *res_dr = drs[stickers[4]][stickers[13]];
}

inline int cmb(int n, int r){
    if (n < r)
        return 0;
    return fac[n] / fac[r] / fac[n - r];
}

inline void sticker2idx(const int stickers[n_stickers], int idxes[n_idxes]){
    int i, j, cnt, cnt2;
    int co[n_corners], cp[n_corners], eo[n_edges], ep[n_edges], dr;
    sticker2arr(stickers, co, cp, eo, ep, &dr);
    idxes[0] = 0;
    for (i = 0; i < n_corners - 1; ++i){
        idxes[0] *= 3;
        idxes[0] += co[i];
    }
    idxes[1] = 0;
    for (i = 0; i < n_corners; ++i){
        cnt = cp[i];
        for (j = 0; j < i; ++j){
            if (cp[j] < cp[i])
                --cnt;
        }
        idxes[1] += fac[7 - i] * cnt;
    }
    idxes[2] = 0;
    for (i = 1; i < n_edges - 1; ++i){
        idxes[2] *= 2;
        idxes[2] += eo[i];
    }
    idxes[3] = 0;
    cnt2 = 0;
    for (i = 1; i < n_edges; ++i){
        if (1 <= ep[i] && ep[i] < 10){
            cnt = ep[i] - 1;
            for (j = 1; j < i; ++j){
                if (ep[j] < ep[i])
                    --cnt;
            }
            idxes[3] += fac[8 - (cnt2++)] * cnt;
        }
    }
    idxes[3] *= 55;
    cnt = 9;
    for (i = 1; i < n_edges; ++i){
        if (1 <= ep[i] && ep[i] < 10)
            idxes[3] += cmb(11 - i, cnt--);
    }
    idxes[4] = dr;
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
    if (amount <= 2){
        for (i = 0; i < amount; ++i){
            for (j = 0; j < sticker_move_nums[face]; ++j){
                for (k = 0; k < 4; ++k)
                    tmp_stickers[sticker_moves[face][j][(k + 1) % 4]] = res[sticker_moves[face][j][k]];
            }
            for (j = 0; j < n_stickers; ++j)
                res[j] = tmp_stickers[j];
        }
    } else{
        for (j = 0; j < sticker_move_nums[face]; ++j){
            for (k = 0; k < 4; ++k)
                tmp_stickers[sticker_moves[face][j][k]] = res[sticker_moves[face][j][(k + 1) % 4]];
        }
        for (j = 0; j < n_stickers; ++j)
            res[j] = tmp_stickers[j];
    }
}

inline double leaky_relu(double x){
    return max(x, 0.01 * x);
}

inline double predict(const int stickers[n_stickers]){
    double in_arr[n_in];
    double hidden0[256], hidden1[256];
    double res;
    int i, j, ri, idx;
    int idxes[n_idxes];
    double min_res;

    sticker2idx(stickers, idxes);
    min_res = 0;
    min_res = max(min_res, prune_cp_eo[idxes[1]][idxes[2]]);
    min_res = max(min_res, prune_co_eo_dr[idxes[0]][idxes[2]][idxes[4]]);
    min_res = max(min_res, prune_ep[idxes[3]]);
    min_res = max(min_res, prune_cp_dr[idxes[1]][idxes[4]]);
    //return c_h * min_res;
    /*
    cerr << min_res << endl;
    for (i = 0; i < 5; ++i)
        cerr << idxes[i] << endl;
    */
    if (min_res <= 8.0)
        return min_res;

    // create input array
    idx = 0;
    for (i = 0; i < n_colors; ++i){
        for (j = 0; j < n_stickers; ++j){
            if (stickers[j] == i)
                in_arr[idx++] = 1.0;
            else
                in_arr[idx++] = 0.0;
        }
    }
    in_arr[idx++] = prune_cp_eo[idxes[1]][idxes[2]];
    in_arr[idx++] = prune_co_eo_dr[idxes[0]][idxes[2]][idxes[4]];
    in_arr[idx++] = prune_ep[idxes[3]];
    in_arr[idx++] = prune_cp_dr[idxes[1]][idxes[4]];

    // dense0
    for (i = 0; i < n_dense0; ++i){
        hidden0[i] = bias0[i];
        for (j = 0; j < n_in; ++j)
            hidden0[i] += dense0[i][j] * in_arr[j];
        hidden0[i] = leaky_relu(hidden0[i]);
    }

    // dense1
    for (i = 0; i < n_dense1; ++i){
        hidden1[i] = bias1[i];
        for (j = 0; j < n_dense0; ++j)
            hidden1[i] += dense1[i][j] * hidden0[j];
        hidden1[i] = leaky_relu(hidden1[i]);
    }

    // residual bloock
    for (ri = 0; ri < n_residual; ++ri){
        for (i = 0; i < n_dense_residual; ++i){
            hidden0[i] = bias_residual[ri][i] + hidden1[i];
            for (j = 0; j < n_dense_residual; ++j)
                hidden0[i] += dense_residual[ri][i][j] * hidden1[j];
            hidden0[i] = leaky_relu(hidden0[i]);
        }
        swap(hidden0, hidden1);
    }

    // dense2
    res = bias2;
    for (j = 0; j < n_dense_residual; ++j)
        res += dense2[j] * hidden1[j];
    res = max(min_res, min(20.0, res));
    return c_h * (res + table_weight * min_res) / (1.0 + table_weight);
}

struct a_star_elem{
    double f;
    int stickers[n_stickers];
    vector<int> solution;
};

bool operator< (const a_star_elem &a, const a_star_elem &b){
    return a.f > b.f;
};

int visited_nodes;

vector<int> search(const int stickers[n_stickers], long long tl){
    int i, mov, sol_size, len_res = 1000;
    double dis;
    priority_queue<a_star_elem> que;
    a_star_elem first_elem, elem;
    vector<int> res;
    for (i = 0; i < n_stickers; ++i)
        first_elem.stickers[i] = stickers[i];
    first_elem.f = predict(first_elem.stickers);
    if (first_elem.f == 0.0)
        return res;
    res.push_back(-1);
    first_elem.solution.push_back(-1000);
    que.push(first_elem);
    long long strt = tim();
    while (que.size() && tim() - strt < tl){
        ++visited_nodes;
        elem = que.top();
        que.pop();
        sol_size = elem.solution.size();
        if (sol_size <= len_res){
            for (mov = 0; mov < n_moves; ++mov){
                if (calc_face(mov) == calc_face(elem.solution[sol_size - 1]))
                    continue;
                if (calc_axis(mov) == calc_axis(elem.solution[sol_size - 1]) && mov < elem.solution[sol_size - 1])
                    continue;
                a_star_elem n_elem;
                move_sticker(elem.stickers, n_elem.stickers, mov);
                dis = predict(n_elem.stickers);
                n_elem.f = sol_size + dis;
                for (i = 0; i < sol_size; ++i)
                    n_elem.solution.push_back(elem.solution[i]);
                n_elem.solution.push_back(mov);
                if (dis == 0.0){
                    if ((int)n_elem.solution.size() < len_res){
                        res.clear();
                        for (i = 1; i < (int)n_elem.solution.size(); ++i)
                            res.push_back(n_elem.solution[i]);
                        cerr << " solution found length: " << res.size() << "; " << visited_nodes << " nodes searched" << endl;
                        len_res = (int)res.size();
                        break;
                    }
                } else if (n_elem.f < elem.f + threshold)
                    que.push(n_elem);
            }
        }
    }
    return res;
}

vector<int> solver(const int stickers[n_stickers]){
    visited_nodes = 0;
    vector<int> solution = search(stickers, 5000);
    cerr << visited_nodes << " nodes searched" << endl;
    if (solution.size()){
        if (solution[0] == -1){
            cerr << " no solution found" << endl;
            vector<int> empty_res;
            return empty_res;
        }
    }
    return solution;
}

int main(){
    cerr << "initializing" << endl;
    init();
    cerr << "initialized" << endl;

    int stickers[n_stickers] = {
        4, 0, 0, 2, 5, 0, 0, 2, 5, 2, 3, 3, 4, 2, 4, 5, 3, 4, 2, 4, 2, 5, 1, 1, 5, 0, 1, 3, 3, 0, 5, 4, 2, 4, 4, 4, 3, 1, 1, 5, 3, 3, 1, 2, 2, 1, 5, 3, 0, 0, 1, 5, 1, 0
    };
    /*
    int moved_stickers[n_stickers];
    move_sticker(stickers, moved_stickers, 2);
    for (int j = 0; j < n_stickers; ++j)
        cerr << moved_stickers[j] << " ";
    cerr << endl;
    return 0;
    */
    string scramble = "R Dw R' Fw F D L' Dw2 F2 R2 Fw' L2";
    //int stickers[n_stickers] = {4, 5, 1, 5, 0, 0, 5, 3, 4, 1, 5, 0, 2, 1, 1, 1, 3, 3, 3, 3, 2, 4, 2, 2, 4, 1, 2, 0, 4, 5, 1, 3, 0, 0, 1, 5, 1, 2, 2, 4, 4, 3, 2, 0, 0, 4, 4, 5, 2, 5, 0, 3, 5, 3};
    //string scramble = "L U2 F2 R' U2 B2 R' D2 L2 F2 U2 D R' F' D' F2 R B2 U";
    cerr << "scramble: " << scramble << endl;
    //int stickers[n_stickers];
    int i;
    long long strt;
    while (true){
        //for (i = 0; i < n_stickers; ++i)
        //    cin >> stickers[i];
        cerr << "start!" << endl;
        strt = tim();
        vector<int> solution = solver(stickers);
        cerr << "solved in " << tim() - strt << " ms" << endl;
        cerr << "length " << solution.size() << endl;
        for (i = 0; i < (int)solution.size(); ++i)
            cerr << notation[solution[i]] << " ";
        cerr << endl;
        cout << solution.size() << endl;
        return 0;
    }
    return 0;
}
