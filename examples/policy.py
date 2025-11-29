from mead import Model, Stock, Flow, Policy, Function

# An example of using the Policy element as
# save 100 every 30d

with Model(name="Savings", dt=1) as model:
    balance = Stock("Balance", 150)  # initial balance 150
    interest = Flow("Interest", balance * 0.01)  # generous 0.01 a day interest
    balance.add_inflow(interest)

    # function to apply policy, every 30 in time, return True
    every_30d = Function("apply_policy", lambda ctx: ctx["time"] % 30 == 0)
    # savings policy is to save 100, apply=-1 means apply every time
    set_appart = Policy("savings", every_30d, 100, apply=-1)
    # flow of additional funds
    additional = Flow("additional", set_appart)
    # add as an inflow into the account
    balance.add_inflow(additional)


results = model.run(duration=180)
model.plot(results, columns=["Balance"])
