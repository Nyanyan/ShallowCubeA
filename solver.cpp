#pragma GCC target("avx2")
#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")

/*
corner numbering
  0 1
   U
0 3 2 1
 L F R
7 4 5 6
   D
  7 6

edge numbering
       0
     3 U 1
       2
11 L 8 F 9 R 10
       4
     7 D 5
       6

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

color numbering
white: 0
green: 1
red: 2
blue: 3
orange: 4
yellow: 5

rotation:
U F number
w g 0
o g 1
y g 2
r g 3
w r 4
g r 5
y r 6
b r 7
w b 8
r b 9
y b 10
o b 11
w o 12
b o 13
y o 14
g o 15
b w 16
o w 17
g w 18
r w 19
g y 20
o y 21
b y 22
r y 23

rotated face
R 0 (0-2)
L 1 (3-5)
U 2 (6-8)
D 3 (9-11)
F 4 (12-14)
B 5 (15-17)
*/

#include <iostream>
#include <algorithm>
#include <vector>
#include <chrono>

using namespace std;

#define fac_max 12

int fac[fac_max];

vector<int> phase_solution;
double strt_search;

int trans_co[2187][14];
int trans_cp[40320][10];
int trans_eo[2048][14];
int trans_ep_phase0[495][14];
int trans_ep_phase1_1[40320][10];
int trans_ep_phase1_2[24][10];
int prun_phase0_co_ep[495][2187];
int prun_phase0_eo_ep[495][2048];
int prun_phase1_cp_ep[24][40320];
int prun_phase1_ep_ep[24][40320];

void init(){
    int i;
    fac[0] = 1;
    for (i = 1; i < fac_max; ++i)
        fac[i] = fac[i - 1] * i;
}

int cmb(int n, int r){
    return fac[n] / fac[r] / fac[n - r];
}


int cp2idx(int *cp){
    int res = 0, i, j, cnt;
    for (i = 0; i < 8; ++i){
        cnt = cp[i];
        for (j = 0; j < i; ++j){
            if (cp[j] < cp[i])
                --cnt;
        }
        res += fac[7 - i] * cnt;
    }
    return res;
}

int co2idx(int *co){
    int res = 0, i;
    for (i = 0; i < 7; ++i){
        res *= 3;
        res += co[i];
    }
    return res;
}

int ep2idx_phase0(int *ep){
    int res = 0, cnt = 4,, i;
    for (i = 11; i >= 0; --i){
        if (ep[i] >= 8){
            res += cmb(i, cnt);
            --cnt;
        }
    }
    return res;
}

int ep2idx_phase1_1(int *ep){
    int res = 0, i, j, cnt;
    for (i = 0; i < 8; ++i){
        cnt = ep[i];
        for (j = 0; j < i; ++j){
            if (ep[j] < ep[i])
                --cnt;
        }
        res += fac[7  - i] * cnt;
    }
    return res;
}

int ep2idx_phase1_2(int *ep){
    int res = 0, i, j, cnt;
    for (i = 0; i < 4; ++i){
        cnt = ep[8 + i] - 8;
        for (j = 8; j < 8 + i; ++j){
            if (ep[j] < ep[8 + i])
                --cnt;
        }
        res += fac[3 - i] * cnt;
    }
    return res;
}

int eo2idx(int *eo){
    int res = 0, i;
    for (i = 0; i < 11; ++i){
        res *= 2;
        res += eo[i];
    }
    return res;
}

