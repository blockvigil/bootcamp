## Summary of Session 05

Primer reading:

* [Blog post: Signing and verifying messages on Ethereum](https://programtheblockchain.com/posts/2018/02/17/signing-and-verifying-messages-in-ethereum/)

* EthVigil API usage example on `eth_sign`
	* [Github](https://github.com/blockvigil/api-usage-examples/tree/master/eth_sign)
	* [EthVigil docs](https://ethvigil.com/docs/eth_sign_example_code/)

* [ECDSA](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)

The broad agenda was to explore offline message signing using only the cryptographic functions offered by Ethereum.

Basically the most widespread usage of public-key cryptography (also known as asymmetric cryptography).

* One party signs a message (technically, a collection of bytes) with their private key, securely, offline.

* In our example, this is the party that wishes to confirm a withdrawal ID
	* not by sending a transaction from their Ethereum account
	* but by signing a certain expected message format with their private key which generates a signed object (65 bytes in length)
	*  and sending the resulting signed object to the smart contract with the context of a `_requestId`

* The expected message format is known by mutual agreement to the receiver: in this case: the `KidMultiSig` contract. The message is agreed upon both by the prover and the receiver to be `a concatenation of request ID and the current contract address of KidMultiSig`.

* Based on this information, the public Ethereum address of the party that signed the known message format is revealed. Think of it as a seal identifying a certain institution or authority. Very close to the concept of how a notary functions. Authorized notes from such parties open up doors in different processes.

_This folder contains the smart contract along with python and JS code to interact with it._

[](INSTALL.md)


### Constructing the message in solidity

Taking the relevant bit of source code from the contract

```
function confirmRequestWithSignature(
	uint256 _requestId,
	bytes memory signatureObject
)
public {

[...]

	bytes memory expectedFormat = abi.encodePacked(_requestId, address(this));

    // bind the expected format within 32 bytes by hashing
    bytes32 message = prefixed(keccak256(expectedFormat));

	// run the same signing algorithm on the hashed 32-byte message, and recover the public key from the Signed Object
    address signer = recoverSigner(message, signatureObject);

[...]

}
```

### Constructing the message in Python

Taking relevant bits of source code from [`multisig_interaction.py`](https://gitlab.com/blockvigil/bootcamp-cohort2/-/blob/master/session05/multisig_interaction.py)


```py
def sign_confirmation(request_id, contractaddr, private_key):  
  print('Signing data with requestId, contractaddr...')  
  print(request_id)  
  print(contractaddr)  
  pre_hash = solidityKeccak(abi_types=['uint256', 'address'], values=[request_id, contractaddr], validity_check=True)  
  msg_hash = defunct_hash_message(hexstr=pre_hash.hex())  
  signed_msg_hash = Account.signHash(msg_hash, private_key)  
  print(f'Signed message hash: {signed_msg_hash.signature.hex()}')  
  # return bytes.fromhex(s=signed_msg_hash.signature.hex())  
  return signed_msg_hash.signature.hex()
```

### Recovering the message in Solidity

Once the above Python code sends out the signed message object to the smart contract as a hex string that represents a series of bytes, `recoverSigner()` does the work of splitting this 65 byte signed message object into three parts `(v, r, s)`

With these three values of `(v, r, s)` and the final `bytes memory signatureObject`,
* we can run the ECDSA primitive offered in Ethereum as well as the Solidity programming language, `ecrecover`
* and finally recover the public Ethereum account address that signed the `signatureObject`

Ensure you have created at least one open Withdrawal request on the smart contract.

## Instructions for Python

* Install Python SDK with a single command if you already initialized `ev-cli`. The Python SDK automatically picks up your credentials from `~/.ethvigil/settings.json` in that case.

`pip install git+https://github.com/blockvigil/ethvigil-python-sdk.git`

Detailed installation instructions on [EthVigil Docs](https://ethvigil.com/docs/python_sdk/) in case you need to reinstall from scratch.

* `pip install -r requirements.txt`

*  Change the very last line in the python file to assign the private key of one of the participants used in the contract constructor arguments

```python
if __name__ == '__main__':  
  confirm_request_with_sig(  
  request_id=int(sys.argv[1]),  
  contract_address=sys.argv[2],  
  # ensure this is a 0x-prefixed hexadecimal string
  privatekey='0xHexadecimalStringGoesHere'
  )
```

* Run the python script with the request ID as the first argument and the contract address as the second

	`python multisig_interaction.py <request_id_integer> <contract_address_KidMultiSig>`

	For eg.

	`python multisig_interaction.py 1 0x2f57f5748d988e6cf46cf3d8a9ce60ea420ba6b4`

## Instructions for NodeJS

* Run `npm install`

* copy `config.example.js` to `config.js` and fill up the values.

* Run `node .`



## Tasks

* Attempt to understand the `function splitSignature(bytes memory sig)` and report on it

* Emit a new event `NewDeposit(uint256 amount, address depositor)` after updating the `balances` in the following function

```solidity
function deposit() public onlyParticipant  {

}
```

* In the function `confirmRequestWithSignature`  ensure that when the withdrawal is confirmed, individual balances in `balances` also gets updated just like `totalBalance` below

```
if (isRequestConfirmed(_requestId)) {
     emit WithdrawalConfirmed(_requestId, requestedWithdrawals[_requestId]);
     emit ConfirmationSigRecieved(_requestId, signer);
     totalBalance -= requestedWithdrawals[_requestId];
}
```

* Introduce a function to get the status of confirmation on requests for a specific participant.

```
function getRequestConfirmationStatus(uint256 _requestId, address participant)
public view
returns (bool)
{

}
```

* How can you use the above function to get the confirmation status of all participants in the contract against a specific request ID?

* Attempt to modify the `confirmRequestWithSignature` function so that once a `WithdrawalConfirmed` event has been emitted for a specific `_requestId`, no more participants should be allowed to call this function.

Hint: add a new function modifier `requestIsNotConfirmed` that will `revert()` when it finds that

`number of approving parties >= total participants÷2`
