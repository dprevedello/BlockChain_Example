import hashlib
import json
import ntplib
from Crypto.PublicKey import RSA
from datetime import datetime


class User:
	def __init__(self, file=None):
		if file is None:
			keyPair = RSA.generate(bits=1024)
			self._public = {'e': keyPair.e, 'n': keyPair.n}
			self._private = {'d': keyPair.d, 'n': keyPair.n}
			self._account_balance = 0.0
		else:
			with open(file, 'r') as f:
				self.__dict__.update(json.load(f))

	def __str__(self):
		return f"{self.public()} [ammount={self._account_balance}]"
	
	def __repr__(self):
		return "%s(%r)" % (self.__class__, self.__dict__)

	def write_to_file(self, file):
		with open(file, 'w') as f:
			json.dump(self.__dict__, f)
	
	def public(self):
		return "%s-%s" % (hex(self._public['e'])[2:], hex(self._public['n'])[2:])

	def private(self):
		return "%s-%s" % (hex(self._private['d'])[2:], hex(self._private['n'])[2:])

	def sign(self, message):
		hash = int.from_bytes(hashlib.sha512(str(message).encode()).digest(), byteorder='big')
		signature = pow(hash, self._private['d'], self._private['n'])
		return str(hex(signature)[2:])

	def build_transaction(self, ammount, receiver):
		try:
			trans_time = datetime.utcfromtimestamp(ntplib.NTPClient().request('pool.ntp.org', version=3, timeout=1).tx_time)
		except:
			trans_time = datetime.now()
		recv = receiver.public() if isinstance(receiver, User) else str(receiver)
		transaction = "%s %s %.2f %s" % (self.public(), recv, float(ammount), trans_time)
		self._account_balance -= float(ammount)
		return "%s %s" % (transaction, self.sign(transaction))
	
	def update_balance(self, blockchain):
		self._account_balance = blockchain.get_account_balance(self.public())
		return self


def verify_transaction(transaction):
	t = str(transaction).split()
	message = ' '.join(t[:-1]).encode()
	hash = int.from_bytes(hashlib.sha512(message).digest(), byteorder='big')
	signature = int(t[-1], 16)
	key_e, key_n = map(lambda i: int(i, 16), t[0].split('-'))
	hashFromSignature = pow(signature, key_e, key_n)
	return hash == hashFromSignature


class Blockchain:
	def __init__(self, genesis_transaction=None, file=None, pow_hardness=5):
		assert not(genesis_transaction is None and file is None)
		if file is None:
			assert(verify_transaction(genesis_transaction))
			self._pending = [genesis_transaction]
			self._chain = []
			self._hardness = pow_hardness
			self.build_block()
		else:
			with open(file, 'r') as f:
				self.__dict__.update(json.load(f))

	def __str__(self):
		blocks = '\n'.join(["Block %i:\n%s\n" % (i, block) for i, block in enumerate(self._chain)])
		pending = '\nPending:\n' + '\n'.join([t for t in self._pending]) if len(self._pending) else ''
		return blocks + pending

	def write_to_file(self, file):
		with open(file, 'w') as f:
			json.dump(self.__dict__, f)
	
	def submit_transaction(self, transaction):
		assert(verify_transaction(transaction))
		t = transaction.split()
		if self.get_account_balance(t[0]) >= float(t[2]):
			self._pending.append(transaction)
			return True
		return False
	
	def get_account_balance(self, user_id=None):
		if user_id is None or len(user_id) == 0:
			return None
		balance = 0
		for chains in [self._chain, self._pending]:
			for block in chains:
				for transaction in block.split("\n"):
					t = transaction.split()
					if len(t) > 3:
						if user_id in t[1]:
							balance += float(t[2])
						elif user_id in t[0]:
							balance -= float(t[2])
		return balance
	
	def build_block(self):
		if len(self._pending) > 0:
			prev_hash = 'genesis' if len(self._chain) == 0 else hashlib.sha512(self._chain[-1].encode()).hexdigest()
			transactions = '\n'.join(self._pending)
			block = "%s\n%s\n" % (prev_hash, transactions)
			pow_n = 0
			while True:
				if hashlib.sha512((block+str(pow_n)).encode()).hexdigest().startswith('0'*self._hardness):
					break
				else:
					pow_n += 1
			block = "%s%i\n%s" % (block, pow_n, hashlib.sha512((block+str(pow_n)).encode()).hexdigest())
			self._pending.clear()
			self._chain.append(block)

	def check_chain(self):
		for i, block in enumerate(self._chain):
			b = block.split('\n')
			if b[-1] != hashlib.sha512('\n'.join(b[:-1]).encode()).hexdigest():
				return False
			if i != 0 and b[0] != hashlib.sha512(self._chain[i-1].encode()).hexdigest():
				return False
		return True
