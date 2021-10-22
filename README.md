# ShallowCubeA



## Abstract

ShallowCubeA project targets at solving rubik's cubes with deep learning with a small model.

[DeepCubeA](http://deepcube.igb.uci.edu/) project is very near to this project, but it uses a large model. If we can solve rubik's cubes with much smaller model than DeepCubeA's, this technology can be used in a lot of environment.

## Algorithms

There are two directories, ```one_phase```  and ```two_phase```.

In ```two_phase``` directory, there are files for modified two-phase algorithm.

In ```one_phase``` directory, there are files for ShallowCubeA algorithm.

### Modified Two-phase Algorithm

The major algorithm of solving rubik's cubes is called [two-phase algorithm](http://kociemba.org/math/imptwophase.htm). I improved this algorithm with neural networks.

When searching each phase with A* algorithm, I used a trained neural network for its heuristic function. This improved the algorithm by decreasing the number of visited nodes.

### ShallowCubeA Algorithm

As of 2021, it is very difficult to solve rubik's cubes in one phase.

There are two previous researches, [Finding Optimal Solutions to Rubik's Cube Using Pattern Databases](https://www.semanticscholar.org/paper/Finding-Optimal-Solutions-to-Rubik%27s-Cube-Using-Korf/e6ab7d5d5d38a659fd2ffa53d72ab67e6abc61af) and [Solving the Rubik's Cube with Deep Reinforcement Learning and Search](http://deepcube.igb.uci.edu/static/files/SolvingTheRubiksCubeWithDeepReinforcementLearningAndSearch_Final.pdf). Both require high-spec computers.

This algorithm, ShallowCubeA algorithm, can be run in your computers.

This algorithm also uses a trained neural network for A*'s heuristic function.



## How to use

### Modified Two-phase Algorithm

Clone this repository and go to the directory, then

```
$ cd two_phase
$ python compile.py solver.cpp solver.out
$ ./solver.out
initializing
initialized
```

Write the state of a rubik's cube by inputting the color of each sticker into stdin.

For example, scrambling ```L B2 L2 D2 B L2 F' U2 R2 U2 F2 R2 U' F L2 B' D U2 R U2``` is written:

```
5 2 2 4 0 5 0 5 1 4 1 5 3 1 0 1 5 1 2 3 5 3 2 4 0 5 2 3 1 1 1 3 0 0 2 3 4 3 3 4 4 2 4 1 0 4 4 2 0 5 2 5 0 3
```

You can use numbers to express the rubik's cube. The numbers are:

```
U(upper face) : 0
F(front face) : 1
R(right face) : 2
B(back face)  : 3
L(left face)  : 4
D(bottom face): 5
```

After you input the state of your rubik's cube, you see some outputs like this:

```
start!
 phase0 112 solutions found
 length 21
solved in 1515 ms
length 21
D' F2 U L' U F' U' R2 D B R2 U F2 U L2 U' L2 F2 R2 F2 D'
```

The last line is outputted in stdout and this is the very solution, others are outputted in stderr.

The solution is written in Singmaster notation.

### ShallowCubeA Algorithm

