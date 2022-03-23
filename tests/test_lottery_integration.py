# Unit Test and Integration Test
import time
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (LOCAL_BLOCKCHAIN_ENVIRONMENTS, getAccount, fund_with_link, )
from brownie import network
import pytest



def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = getAccount()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)

    lottery.endLottery({"from": account})

    time.sleep(30)

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0