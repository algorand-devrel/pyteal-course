from pyteal import *
from pyteal.ast.bytes import Bytes
from pyteal_helpers import program


def approval():
    # locals
    local_opponent = Bytes("opponent")  # byteslice
    local_wager = Bytes("wager")  # uint64
    local_commitment = Bytes("commitment")  # byteslice
    local_reveal = Bytes("reveal")  # byteslice

    op_challenge = Bytes("challenge")
    op_accept = Bytes("accept")
    op_reveal = Bytes("reveal")

    @Subroutine(TealType.none)
    def reset(account: Expr):
        return Seq(
            App.localPut(account, local_opponent, Bytes("")),
            App.localPut(account, local_wager, Int(0)),
            App.localPut(account, local_commitment, Bytes("")),
            App.localPut(account, local_reveal, Bytes("")),
        )

    @Subroutine(TealType.uint64)
    def is_empty(account: Expr):
        return Return(
            And(
                App.localGet(account, local_opponent) == Bytes(""),
                App.localGet(account, local_wager) == Int(0),
                App.localGet(account, local_commitment) == Bytes(""),
                App.localGet(account, local_reveal) == Bytes(""),
            )
        )

    @Subroutine(TealType.uint64)
    def is_valid_play(p: Expr):
        first_letter = ScratchVar()
        return Seq(
            first_letter.store(Substring(p, Int(0), Int(1))),
            Return(
                Or(
                    first_letter.load() == Bytes("r"),
                    first_letter.load() == Bytes("p"),
                    first_letter.load() == Bytes("s"),
                )
            ),
        )

    @Subroutine(TealType.none)
    def create_challenge():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(2),
                group_index=Int(0),
            ),
            program.check_rekey_zero(2),
            Assert(
                And(
                    # second transaction is wager payment
                    Gtxn[1].type_enum() == TxnType.Payment,
                    Gtxn[1].receiver() == Global.current_application_address(),
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    # second account has opted-in
                    App.optedIn(Int(1), Int(0)),
                    is_empty(Int(1)),
                    # commitment
                    Txn.application_args.length() == Int(2),
                )
            ),
            App.localPut(Txn.sender(), local_opponent, Txn.accounts[1]),
            App.localPut(Txn.sender(), local_wager, Gtxn[1].amount()),
            App.localPut(
                Txn.sender(),
                local_commitment,
                Txn.application_args[1],
            ),
            Approve(),
        )

    @Subroutine(TealType.none)
    def accept_challenge():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(2),
                group_index=Int(0),
            ),
            program.check_rekey_zero(2),
            Assert(
                And(
                    # second (opponent) account has opted-in
                    App.optedIn(Int(1), Int(0)),
                    # second account has challenged this account
                    App.localGet(Int(1), local_opponent) == Txn.sender(),
                    # second transaction is wager match
                    Gtxn[1].type_enum() == TxnType.Payment,
                    Gtxn[1].receiver() == Global.current_application_address(),
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    Gtxn[1].amount() == App.localGet(Int(1), local_wager),
                    # no commitment on accept, just instant reveal
                    Txn.application_args.length() == Int(2),
                    is_valid_play(Txn.application_args[1]),
                )
            ),
            App.localPut(Int(0), local_opponent, Txn.accounts[1]),
            App.localPut(Int(0), local_wager, Gtxn[1].amount()),
            App.localPut(Int(0), local_reveal, Txn.application_args[1]),
            Approve(),
        )

    @Subroutine(TealType.uint64)
    def play_value(p: Expr):
        first_letter = ScratchVar()
        return Seq(
            first_letter.store(Substring(p, Int(0), Int(1))),
            Return(
                Cond(
                    [first_letter.load() == Bytes("r"), Int(0)],
                    [first_letter.load() == Bytes("p"), Int(1)],
                    [first_letter.load() == Bytes("s"), Int(2)],
                )
            ),
        )

    @Subroutine(TealType.uint64)
    def winner_account_index(play: Expr, opponent_play: Expr):
        return Return(
            Cond(
                [play == opponent_play, Int(2)],  # tie
                [(play + Int(1)) % Int(3) == opponent_play, Int(1)],  # opponent wins
                [
                    (opponent_play + Int(1)) % Int(3) == play,
                    Int(0),
                ],  # current account win
            )
        )

    @Subroutine(TealType.none)
    def send_reward(account_index: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[account_index],
                    TxnField.amount: amount,
                    TxnField.fee: Int(0),  # use fee pooling
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    @Subroutine(TealType.none)
    def reveal():
        winner = ScratchVar()
        wager = ScratchVar()
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(1),
                group_index=Int(0),
            ),
            program.check_rekey_zero(1),
            Assert(
                And(
                    # verify game data matches
                    App.localGet(Int(0), local_opponent) == Txn.accounts[1],
                    App.localGet(Int(1), local_opponent) == Txn.sender(),
                    App.localGet(Int(0), local_wager)
                    == App.localGet(Int(1), local_wager),
                    # this account has commitment
                    App.localGet(Int(0), local_commitment) != Bytes(""),
                    # opponent account has a reveal
                    App.localGet(Int(1), local_reveal) != Bytes(""),
                    # require reveal argument
                    Txn.application_args.length() == Int(2),
                    # validate reveal
                    Sha256(Txn.application_args[1])
                    == App.localGet(Int(0), local_commitment),
                )
            ),
            wager.store(App.localGet(Int(0), local_wager)),
            winner.store(
                winner_account_index(
                    play_value(Txn.application_args[1]),
                    play_value(App.localGet(Int(1), local_reveal)),
                )
            ),
            If(winner.load() == Int(2))
            .Then(
                # tie: refund wager to each party
                Seq(
                    # require first transaction fee to cover:
                    # - own transaction fee
                    # - each reward transaction fee
                    Assert(Txn.fee() >= Global.min_txn_fee() * Int(3)),
                    send_reward(Int(0), wager.load()),
                    send_reward(Int(1), wager.load()),
                )
            )
            .Else(
                # send double wager to winner
                Seq(
                    # require first transaction fee to cover:
                    # - own transaction fee
                    # - reward transaction fee
                    Assert(Txn.fee() >= Global.min_txn_fee() * Int(2)),
                    send_reward(winner.load(), wager.load() * Int(2)),
                )
            ),
            reset(Int(0)),
            reset(Int(1)),
            Approve(),
        )

    return program.event(
        init=Approve(),
        opt_in=Seq(
            reset(Int(0)),
            Approve(),
        ),
        no_op=Seq(
            Cond(
                [
                    Txn.application_args[0] == op_challenge,
                    create_challenge(),
                ],
                [
                    Txn.application_args[0] == op_accept,
                    accept_challenge(),
                ],
                [
                    Txn.application_args[0] == op_reveal,
                    reveal(),
                ],
            ),
            Reject(),
        ),
    )


def clear():
    return Approve()
