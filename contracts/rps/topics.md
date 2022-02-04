# Rock-Paper-Scissors

## Part 1

* Local storage
* Subroutines
* Basic security/sanity checks
* Determinism
* Inner transactions
* Transaction grouping
* App accounts
* Minimum app/account funding

## Part 2

* Fee pooling

## Homework

* Make a `rescind` method that allows a challenger to take back their challenge (so they could challenge another account). It should also refund their wager.
* Add a case to the `reveal` method that allows the opponent to resolve the game (and take all the winnings) if the challenger doesn't reveal within a certain period of time.
* Track the number of games and the amount of ALGO wagered on the smart contract.
