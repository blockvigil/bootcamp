from eth_account.messages import defunct_hash_message
from eth_account.account import Account
from eth_abi import is_encodable
from eth_abi.packed import encode_abi_packed, encode_single_packed
import eth_utils
from ethvigil.EVCore import EVCore
import sys


def solidityKeccak(abi_types, values, validity_check=False):
    """
    Executes keccak256 exactly as Solidity does.
    Takes list of abi_types as inputs -- `[uint24, int8[], bool]`
    and list of corresponding values  -- `[20, [-1, 5, 0], True]`
    Adapted from web3.py
    """
    if len(abi_types) != len(values):
        raise ValueError(
            "Length mismatch between provided abi types and values.  Got "
            "{0} types and {1} values.".format(len(abi_types), len(values))
        )
    if validity_check:
        for t, v in zip(abi_types, values):
            if not is_encodable(t, v):
                print(f'Value {v} is not encodable for ABI type {t}')
                return False
    hex_string = eth_utils.add_0x_prefix(''.join(
        encode_single_packed(abi_type, value).hex()
        for abi_type, value
        in zip(abi_types, values)
    ))
    # hex_string = encode_abi_packed(abi_types, values).hex()
    return eth_utils.keccak(hexstr=hex_string)


def confirm_request_with_sig(request_id, contract_address, privatekey):
    constructed_sig_obj = sign_confirmation(request_id, contract_address, privatekey)
    evc = EVCore(verbose=False)
    contract_instance = evc.generate_contract_sdk(
        contract_address=sys.argv[2],
        app_name='KidMultiSig'
    )
    tx = contract_instance.confirmRequestWithSignature(
        _requestId=request_id,
        signatureObject=constructed_sig_obj
    )
    print(tx)


def sign_confirmation(request_id, contractaddr, private_key):
    print('Signing data with settlementid, contractaddr...')
    print(request_id)
    print(contractaddr)
    pre_hash = solidityKeccak(abi_types=['uint256', 'address'], values=[request_id, contractaddr], validity_check=True)
    msg_hash = defunct_hash_message(hexstr=pre_hash.hex())
    signed_msg_hash = Account.signHash(msg_hash, private_key)
    print(f'Signed message hash: {signed_msg_hash.signature.hex()}')
    # return bytes.fromhex(s=signed_msg_hash.signature.hex())
    return signed_msg_hash.signature.hex()


if __name__ == '__main__':
    confirm_request_with_sig(
        request_id=int(sys.argv[1]),
        contract_address=sys.argv[2],
        privatekey=''  # private key, 0xHexadecimalString
    )
