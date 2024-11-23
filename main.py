import blocks
from flask import Flask, request
import json
import time

app = Flask(__name__)
blockchain = blocks.Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

@app.route('/mine_block', methods=['GET'])
def mine():
    success = blockchain.mine_block()
    if success:
        save_blockchain_to_file(blockchain)
        return json.dumps({"message": "Block mined",
                        "chain": [block.__dict__ for block in blockchain.chain]}), 200
    else:
        return json.dumps({"message": "Unable to mine block"}), 500

@app.route('/addBlock', methods=['POST'])
def add_block():
    data = request.get_json()
    if not data or "transaction" not in data:
        return json.dumps({"message": "Invalid transaction data"}), 400

    # Add transaction to unconfirmed transactions
    blockchain.add_new_transaction(data["transaction"])
    return json.dumps({"message": "Block added"}), 200

def save_blockchain_to_file(blockchain, filename="blockchain_data.json"):
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    
    with open(filename, 'w') as file:
        json.dump(chain_data, file, indent=4)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

    