import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, transactions, timestamp, nounce=0, hash=""):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.nounce = nounce        
        self.hash = hash if hash else self.calculate_hash()
    
    def calculate_hash(self):

        keys = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'nounce': self.nounce
        }

        value = json.dumps(keys, sort_keys=True)
        return hashlib.sha256(value.encode()).hexdigest()


class Blockchain:
    def __init__(self, filename="blockchain_data.json"):
        self.filename = filename
        self.unconfirmed_transactions = []
        self.chain = self.get_blockchain_from_file()  # Load the blockchain from the file
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        # Create the first block (genesis block)
        genesis_block = Block(0, "0", [], int(time.time()), 0)
        self.chain.append(genesis_block)
        self.save_blockchain_to_file()  # Save the blockchain to file

    @property
    def last_block(self):
        return self.chain[-1]

    difficulty = 1

    def proof_of_work(self, block):
        block.nounce = 0
        computed_hash = block.calculate_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nounce += 1
            computed_hash = block.calculate_hash()
            if block.nounce % 10000 == 0:  # Check every 10000th attempt
                print(f"Nounce: {block.nounce}")
        return computed_hash

    def add_new_block(self, block, proof):
        # Check if previous block hash matches
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False
        
        block.hash = proof
        self.chain.append(block)
        self.save_blockchain_to_file()  # Save to file after adding the block
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.calculate_hash())

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine_block(self):
        if not self.unconfirmed_transactions:
            return False
        
        last_block = self.last_block
        lb_hash = last_block.calculate_hash()        
        new_block = Block(len(self.chain) + 1, lb_hash, self.unconfirmed_transactions, int(time.time()))

        proof = self.proof_of_work(new_block)

        self.unconfirmed_transactions = []  # Clear unconfirmed transactions after mining
        self.add_new_block(new_block, proof)
        
        return True

    def get_blockchain_from_file(self):
        try:
            with open(self.filename, 'r') as file:
                blockchain_data = json.load(file)
                return [Block(**data) for data in blockchain_data]
        except FileNotFoundError:
            return []

    def save_blockchain_to_file(self):
        # Save the blockchain to the file
        with open(self.filename, 'w') as file:
            blockchain_data = [block.__dict__ for block in self.chain]
            json.dump(blockchain_data, file, indent=4)
