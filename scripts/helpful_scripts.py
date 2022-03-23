from os import link
from brownie import (accounts, network, config, interface, Contract, MockV3Aggregator, VRFCoordinatorMock, LinkToken)
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIROMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def getAccount(index=None, id=None):

    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS 
    or network.show_active() in FORKED_LOCAL_ENVIROMENTS):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator, 
    "vrf_coordinator": VRFCoordinatorMock, 
    "link_token": LinkToken
}

def getContract(contract_name):
    """
    This function will grab the contract addresses from the brownie config 
    if defined, otherwise it will deploy a mock version of the contract, 
    and return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract

    
    """

    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1] 
        # This is basically MockV3Aggregator[-1]

    else:
        contract_address = config["networks"][network.show_active()][contract_name]

        # address
        # ABI

        contract = Contract.from_abi(
            contract_type._name, 
            contract_address,
            contract_type.abi
        )

    return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000

def deploy_mocks(decimals=DECIMALS, initial_value = INITIAL_VALUE):

    account = getAccount()
    MockV3Aggregator.deploy(decimals, initial_value, {"from":account})
    link_token = LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address, {"from":account})
    print("Deployed!!")

def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000): #0.1 Link
    account = account if account else getAccount()
    link_token = link_token if link_token else getContract("link_token")

    # tx = link_token.transfer(contract_address,amount, {"from":account})
    link_token_interface = interface.LinkTokenInterface(link_token.address)
    tx = link_token_interface.transfer(contract_address, amount, {"from":account})
    tx.wait(1)

    print("Fund Contract!")
    return tx