import gurobipy as gp
from gurobipy import GRB
from math import log

# SOLUTION FROM GUROBI

if __name__ == "__main__":
    R, T, delta_t, C = 1, 1, 0.1, 1

    model = gp.Model("")

    c_rate = model.addVar(name="c_rate")
    y = model.addVar(name="y")
    z = model.addVar(lb=-GRB.INFINITY, name="z")
    u = model.addVar(name="u")

    # Minimize ln(Q_loss)
    model.setObjective(y + (-31700 + 370.3 * c_rate) / (R * T) + 0.55 * z, sense=GRB.MINIMIZE)
    
    # u = delta_t * c_rate
    model.addConstr(u == delta_t * c_rate)
    # z = ln(u) = ln(delta_t * c_rate)
    model.addGenConstrLog(u, z)

    # y = ln(31630) if 0   <= c_rate <= c/2;
    #     ln(21681) if c/2 <= c_rate <= 2c;
    #     ln(12934) if 2c  <= c_rate <= 6c;
    #     ln(15512) if 6c  <= c_rate <= 10c;
    model.addGenConstrPWL(
        c_rate,
        y,
        [0, C / 2, C / 2, 2 * C, 2 * C, 6 * C, 6 * C, 10 * C],
        [
            log(31630),
            log(31630),
            log(21681),
            log(21681),
            log(12934),
            log(12934),
            log(15512),
            log(15512),
        ],
    )

model.optimize()
for var in model.getVars():
    print(f"{var.VarName}: {var.X}")

    