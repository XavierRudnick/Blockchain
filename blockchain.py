import hashlib #hashfunction
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.transaction = []
        self.new_block(proof = 100,previous_hash = 1)
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        """
        Creates new block containing necessary information 
        :param proof: <int> Proof from proof of work algorithm
        :param previous_hash: <str> (Optional) Most recent hash
        :return: <dic> New block
        """
        block = {
            'index': len(self.chain) +1,
            'time' : time(),
            'transaction' : self.transaction,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }

        self.chain.append(block)
        self.transaction = []
        return block


    def new_transaction(self, sender, recipient, amount):
        """
        Creates new transaction information that is input into block
        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.transaction.append({
            "sender":sender,
            "recipient":recipient,
            "amount":amount})
        
        return self.last_block['index'] + 1

    @staticmethod #static method says this hash function dosent need any creation or changing of class variables
    def hash(block): 
        """
        Creates a SHA-256 hash of a block
        :param block: <dict> block used to create hash
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode() #creates a string of bytes from a json string
        return hashlib.sha256(block_string).hexdigest() #bytes get turned into a hash object then turned into hexidecimal string

    @property  #sets last_block to be a getter while also being backwards compatible with simple accesing elements
    def last_block(self):
        """
        :return: <dic> mot recent block
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Proof of Work Algorithm:
         - Find a number x such that hash(xy) contains leading 4 zeroes, where y is the previous x
         - y is the previous proof, and x is the new proof
        :param last_proof: <int> Old proof
        :return: <int> New proof
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof so it follows the set rules of proof of work
        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if correct valid, false if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        """
        Add a new node to the list of nodes to create a decentrilized system.
        :param address: <str> Address of node (server)
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1
        n = len(chain)
        while current_index < n:
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash and proof of work of the block is correct
            if block['previous_hash'] != self.hash(last_block) or not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Consensus algorithm for resolving conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False