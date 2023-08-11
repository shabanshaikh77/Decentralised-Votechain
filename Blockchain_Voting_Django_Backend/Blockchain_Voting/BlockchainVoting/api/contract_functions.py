from web3 import Web3
from solcx import compile_standard, install_solc
from hexbytes import HexBytes

chain_id = 11155111
my_address = "0xb7A2E79FD29106f03C17b6aD2E03e520ABEf6A20"
contract_address = "0xDAED0AA4DA3433DFb7fe1b9cf4C1181b52bbbF68"
abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "election_id", "type": "uint256"},
            {"internalType": "uint256", "name": "choices_count", "type": "uint256"},
        ],
        "name": "createNewElection",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "election_id", "type": "uint256"},
            {"internalType": "int256", "name": "choice_id", "type": "int256"},
            {"internalType": "string", "name": "hash", "type": "string"},
        ],
        "name": "hashVote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "election_id", "type": "uint256"},
            {"internalType": "uint256", "name": "choice_id", "type": "uint256"},
        ],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "election_id", "type": "uint256"}
        ],
        "name": "getElectionResult",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "election_id", "type": "uint256"},
            {"internalType": "string", "name": "hash", "type": "string"},
        ],
        "name": "verifyVote",
        "outputs": [{"internalType": "int256", "name": "", "type": "int256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def createNewElection(election_id, number_of_choices):
    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d6b8e95a5bd6495e9ade9d45c5ba1778"))

    my_contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(my_address)

    call_function = my_contract.functions.createNewElection(
        election_id,
        number_of_choices,
    ).build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
        }
    )

    signed_tx = w3.eth.account.sign_transaction(call_function, private_key="0xd1bdfc5831558a8c212cba587a1749f0bf22871933bacd3eacfebe9b936c0e76")

    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    hash = str(tx_receipt["transactionHash"].hex())
    return hash


def getElectionResult(election_id):
    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d6b8e95a5bd6495e9ade9d45c5ba1778"))
    my_contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(my_address)
    result = my_contract.functions.getElectionResult(election_id).call()
    return result


def vote(election_id, choice_id):
    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d6b8e95a5bd6495e9ade9d45c5ba1778"))

    my_contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(my_address)

    call_function = my_contract.functions.vote(
        election_id,
        choice_id,
    ).build_transaction({"chainId": chain_id, "from": my_address, "nonce": nonce})

    signed_tx = w3.eth.account.sign_transaction(call_function, private_key="0xd1bdfc5831558a8c212cba587a1749f0bf22871933bacd3eacfebe9b936c0e76")

    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    hash = str(tx_receipt["transactionHash"].hex())
    hashVote(election_id=election_id, choice_id=choice_id, hash=hash)
    return hash


def hashVote(election_id, choice_id, hash):
    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d6b8e95a5bd6495e9ade9d45c5ba1778"))

    my_contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(my_address)

    call_function = my_contract.functions.hashVote(
        election_id,
        choice_id,
        hash,
    ).build_transaction({"chainId": chain_id, "from": my_address, "nonce": nonce})

    signed_tx = w3.eth.account.sign_transaction(call_function, private_key="0xd1bdfc5831558a8c212cba587a1749f0bf22871933bacd3eacfebe9b936c0e76")

    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    hash = str(tx_receipt["transactionHash"].hex())
    print(hash)


def verifyVote(election_id, hash):
    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d6b8e95a5bd6495e9ade9d45c5ba1778"))
    my_contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(my_address)
    result = my_contract.functions.verifyVote(
        election_id,
        hash,
    ).call()
    return result
