from scripts.helpful_scripts import fund_with_link, getAccount, getContract
from brownie import Lottery, network, config
import time

def deploy_lottery():
    account = getAccount()

    lottery = Lottery.deploy(
        getContract("eth_usd_price_feed").address,
        getContract("vrf_coordinator").address,
        getContract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source = config["networks"][network.show_active()].get("verify", False)
        )
    print("Deployed lottery")
    return lottery


def start_lottery():
    account = getAccount()
    lottery = Lottery[-1]
    
    starting_tx = lottery.startLottery({"from":account})
    starting_tx.wait(1)

    print("The lottery is started")

def enter_lottery():
    account = getAccount()
    lottery = Lottery[-1]

    value = lottery.getEntranceFee() + 10000000

    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)

    print("You entered the lottery")

def end_lottery():
    account = getAccount()
    lottery = Lottery[-1]
    print(lottery)
    # first fund the contract and then end the lottery
    tx = fund_with_link(lottery)
    print(tx)
    tx.wait(1)

    ending_trasaction = lottery.endLottery({"from":account})
    ending_trasaction.wait(1)

    time.sleep(20)
    
    print(f"{lottery.recentWinner()} is the new winner")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()