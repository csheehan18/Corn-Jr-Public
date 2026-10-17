"""Real backends for tools the corpus could only simulate.

`corn/tools.py` holds the tool functions the *generator* used: they answer out
of `FACTS`, `CONTACTS` and the rest, which is exactly right for manufacturing a
corpus with exact ground truth and useless to a person asking a question. This
package is the other half -- the same schemas with something real behind them.

**The contract is the payload, not the function.** A backend here may do
anything it likes internally and must return one of the shapes the model was
trained to read, because the reply Corn-Jr speaks is copied out of the
observation. A backend that invented a fifth shape would be handing 260M
parameters a structure they have never seen and asking them to improvise, which
is the one thing four findings taught him not to do. Every module in this
package states its shapes at the top and a guard asserts them.

This is also where the repo split earns itself. The generator tables stay
private with the training code; these backends go out with the weights, and a
person hosting their own Corn-Jr swaps a search provider here without ever
seeing the corpus that taught him to use one.
"""
