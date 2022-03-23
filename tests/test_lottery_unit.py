# 50USD = 0.019ETH
# which implies 190000000000000000 wei
from sklearn import exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, getAccount, fund_with_link, getContract
from brownie import Lottery, accounts, config, network, exceptions
import pytest
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2000 = eth/usd and usdentryfee = 50 -- > 0.025ETH
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee

def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": getAccount(), "value": lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip() 
    lottery = deploy_lottery()
    account = getAccount()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account

def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip() 
    lottery = deploy_lottery()
    account = getAccount()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = getAccount()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": getAccount(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": getAccount(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)

    tx = lottery.endLottery({"from": account})
    request_Id = tx.events["RequestedRandomness"]["requestId"]
    STATIC_NO = 777
    getContract("vrf_coordinator").callBackWithRandomness(
        request_Id, STATIC_NO, lottery.address, {"from": account}
    )

    starting_balance = account.balance()
    balance_of_lottery = lottery.balance()
    # Winner is 777%3 = 0

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

    assert account.balance() == starting_balance + balance_of_lottery
