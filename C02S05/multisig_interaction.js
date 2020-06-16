const Accounts = require('web3-eth-accounts');
const axios = require('axios');
const config = require('./config.js');
const { ethers } = require('ethers');

const args = process.argv.slice(2);
console.log('got arguments: ', args);

if (!config.apiKey || !config.multiSigAdress || !config.privateKey){
	console.error('Fill up all values in config.js');
	process.exit(0);
}

const multiSigInstance = axios.create({
	baseURL: config.apiPrefix + config.multiSigAdress,
	timeout: 5000,
	headers: {'X-API-KEY': config.apiKey}
});


const accounts = new Accounts('http://asasas:8545');

const sign_confirmation = async(request_id, contractaddr, private_key) => {
	console.log('Signing data with settlementid, contractaddr...', request_id, contractaddr);
	let pre_hash = ethers.utils.solidityKeccak256(['uint256', 'address'], [request_id, contractaddr])
	let msg_hash = accounts.hashMessage(pre_hash)
	let signingKey = new ethers.utils.SigningKey(private_key);
	let signed_msg = signingKey.signDigest(msg_hash);
	signed_msg = ethers.utils.joinSignature(signed_msg)
	console.log('Signed message hash', signed_msg)
	return signed_msg;
}

const confirm_request_with_sig = async(request_id, contract_address, privatekey) => {
	let constructed_sig_obj = await sign_confirmation(request_id, contract_address, privatekey)
	multiSigInstance.post('/confirmRequestWithSignature', {
		_requestId: request_id,
		signatureObject: constructed_sig_obj
	})
	.then(function (response) {
		console.log(response.data);
		if (!response.data.success){
			process.exit(0);
		}
	})
	.catch(function (error) {
		if (error.response.data){
			console.log(error.response.data);
			if (error.response.data.error == 'unknown contract'){
				console.error('You filled in the wrong contract address!');
			}
		} else {
			console.log(error.response);
		}
		process.exit(0);
	});
}

confirm_request_with_sig(parseInt(args[0]), args[1], config.privateKey);
