import solitaire

import threading

import pickle as pkl

def run_experiment(N, n0=0, solver="gecode", timeout=60):
    """
    Creates N random instances and tries to solve them with the given solder. Returns array
    of results. Allows caching the results in a file so they do not have to be recomputed
    (in some cases this can take a lot of time).
    """
    solved = []
    timeouts = []
    unsatisfiable = []
    for i in range(n0,n0+N):
        problem = solitaire.generate(rng_seed=i)
        result = solitaire.solve(problem, solver_name=solver,
                                 exec_args={"timeout": timeout})
        if result["stack"]:
            solved.append(result)
        elif result["timeout"]:
            timeouts.append(result)
        else:
            unsatisfiable.append(result)
        # print('#Solved: {}\t#Timeouts: {}\t#Unsatisfiable: {}'.format(
            # len(solved), len(timeouts), len(unsatisfiable)), end='\r')
    results = {
        "solved": solved,
        "timeouts": timeouts,
        "unsatisfiable": unsatisfiable
    }
    return results

def doit(N, n0):
    print("Thread started")
    results = run_experiment(N, n0)
    t = threading.current_thread()
    t.results = results
    print("Thread finished")

if __name__ == "__main__":
    threads = [threading.Thread(target=doit, args=(25,25*i)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    results = {
            "solved": [],
            "unsatisfiable": [],
            "timeouts": [],
    }
    for t in threads:
        for k in results:
            results[k] += t.results[k]

    print(len(results["solved"]))

    with open("results_gecode_french.pkl", "wb") as f:
        pkl.dump(results, f)

