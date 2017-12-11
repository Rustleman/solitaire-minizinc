% Solitaire
% Author: Alejandro Suarez Hernandez
% MiniZinc model for solving the solitaire game.

include "increasing.mzn";
include "inverse.mzn";

% PARAMETERS

int: s; % number of suits (4 in French/Spanish deck)
int: m; % cards per suit (13 in French deck, 12-2=10 for Spanish deck)
int: heap_size; % stack size of the initial layout (3 for standard Solitaire)

int: n = s*m; % total number of cards (52 for French deck, 48-8=40 for Spanish deck)
int: heaps = (n-1) div heap_size; % total number of heaps (17 for French deck, 13 for Spanish deck)

set of int: SUIT = 1..s;
set of int: CARD = 1..n;
set of int: POSITION = 1..n;
set of int: RANK = 1..m;
set of int: HEAP_CARD = 1..heap_size;
set of int: HEAP = 1..heaps;

% The following is an auxiliary set to express gracefully the +-1 rank constraint.
% IMPORTANT: Ranks are like a ring, i.e., after a card of rank m one can put a card with
% rank 1 and vice versa.
set of int: VALID_DIFFERENCE = {m*i - 1 | i in -s+1..s-1} union
                               {m*i + 1 | i in -s+1..s-1} union
                               {m*i + m-1 | i in -s+1..s-1} union
                               {m*i + 1-m | i in -s+1..s-1};

CARD: bottom;
array[HEAP,HEAP_CARD] of CARD: layout;

% SANITY CHECK:

% n-1 should be divisible by heap_size
constraint assert((n-1) mod heap_size = 0,
 "n-1 (" ++ show(n-1) ++ ") should be multiple of heap_size (" ++ show(heap_size) ++ ")");

% VARIABLES

% We have two views of the problem. The first represents the problem as an array of n cards. The
% ith element of the array is the card at the ith position of the stack (being 1 the bottom card).
% With this view, expressing the +-1 rank constraint is much easier:
array[POSITION] of var CARD: stack;

% The second view of the problem is an array of size n in which the ith element is the position in
% the stack of the ith card. With this view, it is quite easy to enforce the correct order of the
% cards according to their initial layout:
array[CARD] of var POSITION: positions;

% array of successive differences
array[1..n-1] of var VALID_DIFFERENCE: d;

% CONSTRAINTS

% force d[i] = stack[i]-stack[i]
constraint forall(i in 1..n-1)(d[i] = stack[i+1] - stack[i]);

% positions[i] = j <-> stack[j] = i
constraint inverse(stack, positions);

% Enforce correct order (cards on top of the heaps go first)
constraint forall(i in HEAP)(increasing([positions[layout[i,j]] | j in HEAP_CARD]));

% First card should always be the bottom card of the stack
constraint stack[1] = bottom;

%solve :: int_search(stack, input_order, indomain_random, complete) satisfy;
solve satisfy;

% Pretty print result
output ["(suit,rank): "] ++ ["(" ++ show((stack[i]-1) div m + 1) ++ "," ++
  show((stack[i]-1) mod m + 1) ++ ")" ++ if i = n then "\n" else ", " endif | i in POSITION];
output ["stack: ", show(stack), "\n"];
output ["VALID DIFFERENCES: ", show(VALID_DIFFERENCE)];
