import random
import pymzn
import time


def generate(s=4, m=13, heap_size=3, bottom=1, rng_seed=None):
    """
    Generate random solitaire problem. Parameters:
        - s: number of suits (default 4 as in French deck)
        - m: cards per suit (default 13 as in French deck)
        - heap_size: size of initial heaps (default 3)
        - bottom: first card of the stack
        - rng_seed: seed of the random generator (default None->current time)
    """
    n = s*m
    assert (n-1) % heap_size == 0, "n-1 must be multiple of heap_size"
    rng = random.Random(rng_seed)
    cards = [i for i in range(1,n+1) if i != bottom]
    rng.shuffle(cards)
    n_heaps = (n-1) // heap_size
    layout = [list(cards[i*heap_size:(i+1)*heap_size])
              for i in range(n_heaps)]
    data = {
            "s": s,
            "m": m,
            "heap_size": heap_size,
            "bottom": bottom,
            "layout": layout,
    }
    return data


def suit_and_rank(card, m=13):
    """
    Retrieves the suit and the rank of the given card. Assumes that the card
    number is calculated as (i-1)*m + j where i,j are the suit and the rank,
    respectively. Parameters:
        - card: card number
        - m: cards per suit (default 13 as in French deck)
    """
    suit = (card-1) // m + 1
    rank = (card-1) % m + 1
    return suit, rank


SOLVER_CLS = {
        "gecode": pymzn.Gecode,
        "chuffed": pymzn.Chuffed,
        "g12fd": pymzn.G12Fd,
}


def solve(data, solver_name="gecode", solver_args={}, exec_args={}):
    solver = SOLVER_CLS[solver_name](**solver_args)
    start = time.time()
    out = pymzn.minizinc("./mzn/solitaire_alt.mzn", data=data,
            solver=solver, **exec_args)
    try:
        solution = out[0]
        ret = {
                "stack": solution["stack"],
                "timeout": False,
        }
    except pymzn.MiniZincUnsatisfiableError:
        ret = {
                "stack": None,
                "timeout": False
        }
    except (pymzn.MiniZincUnknownError, IndexError):
        ret = {
                "stack": None,
                "timeout": True,
        }
    elapsed = time.time() - start
    ret["elapsed"] = elapsed
    return ret


def pty_card(card, m=13):
    """
    Returns a pleasant unicode character for the given card. Parameters:
        - card: card number
        - m: cards per suit (default 13 as in French deck)
    """
    suit, rank = suit_and_rank(card, m)
    return chr((0x1f0<<8)+(0x9+suit<<4)+rank)


def pty_layout(data):
    """
    Returns a pleasant unicode string for visualizing the initial heap layout.
    Parameters:
        - data: data of the problem, as returned by generate method.
    """
    m = data["m"]
    heap_size = data["heap_size"]
    pty_str = ""
    for idx, layer in enumerate(zip(*data["layout"])):
        pty_str += "  ".join(map(lambda c: pty_card(c, m), layer))
        if idx != heap_size - 1:
            pty_str += "\n"
    return pty_str


def pty_problem(data):
    """
    Returns a pleasant unicode string for visualizing a problem. Parameters:
        - data: data of the problem, as returned by generate method.
    """
    pty_str = "bottom: " + pty_card(data["bottom"]) + "\n"
    pty_str += "initial layout:\n"
    pty_str += pty_layout(data)
    return pty_str


def pty_stack(stack, m=13):
    return "  ".join(map(lambda c: pty_card(c, m), stack))


def pty_result(result, m=13):
    if result["timeout"]:
        ret = "timeout after {:.02f}s".format(result["elapsed"])
    elif result["stack"]:
        ret = "stack: " + pty_stack(result["stack"])
        ret += ", elapsed: {:.02f}s".format(result["elapsed"])
    else:
        ret = "Unsatisfiable, elapsed: {:.02f}s".format(result["elapsed"])
    return ret


if __name__ == "__main__":
    # Quick test
    data = generate(rng_seed=43)
    print(pty_problem(data))
    result = solve(data, solver_name="gecode",
            exec_args={"timeout": 300})
    print(pty_result(result))

