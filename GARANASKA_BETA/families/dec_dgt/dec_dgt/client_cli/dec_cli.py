# Copyright 2022 DGT NETWORK INC © Stanislav Parsov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import argparse
import getpass
import logging
import os
import sys
import traceback
import pkg_resources
import cbor

from colorlog import ColoredFormatter

from dec_dgt.client_cli.generate import add_generate_parser
from dec_dgt.client_cli.generate import do_generate
from dec_dgt.client_cli.populate import add_populate_parser
from dec_dgt.client_cli.populate import do_populate
from dec_dgt.client_cli.create_batch import add_create_batch_parser
from dec_dgt.client_cli.create_batch import do_create_batch
from dec_dgt.client_cli.load import add_load_parser
from dec_dgt.client_cli.load import do_load
from dec_dgt.client_cli.dec_workload import add_workload_parser
from dec_dgt.client_cli.dec_workload import do_workload

from dec_dgt.client_cli.dec_client import DecClient
from dec_dgt.client_cli.exceptions import DecCliException
from dec_dgt.client_cli.exceptions import DecClientException
from dec_common.protobuf.dec_dgt_token_pb2 import DecTokenInfo
from dec_dgt.client_cli.dec_attr import *



DISTRIBUTION_NAME = 'dec-dgt'


DEFAULT_URL = 'http://127.0.0.1:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (DGT) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    add_emission_parser(subparsers, parent_parser)
    add_wallet_parser(subparsers, parent_parser)
    add_birth_parser(subparsers, parent_parser)
    add_total_supply_parser(subparsers, parent_parser)
    add_token_info_parser(subparsers, parent_parser)
    add_burn_parser(subparsers, parent_parser)
    add_change_mint_parser(subparsers, parent_parser)
    add_distribute_parser(subparsers, parent_parser)
    add_faucet_parser(subparsers, parent_parser)
    # 
    add_mint_parser(subparsers, parent_parser)
    add_heart_beat_parser(subparsers, parent_parser)
    add_seal_count_parser(subparsers, parent_parser)
    #
    add_balance_of_parser(subparsers, parent_parser)
    add_send_parser(subparsers, parent_parser)
    add_pay_parser(subparsers, parent_parser)
    add_invoice_parser(subparsers, parent_parser)
    add_bank_list_parser(subparsers, parent_parser)

    #
    add_set_parser(subparsers, parent_parser)
    add_inc_parser(subparsers, parent_parser)
    add_dec_parser(subparsers, parent_parser)
    add_trans_parser(subparsers, parent_parser)
    add_show_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)

    add_generate_parser(subparsers, parent_parser)
    add_load_parser(subparsers, parent_parser)
    add_populate_parser(subparsers, parent_parser)
    add_create_batch_parser(subparsers, parent_parser)
    add_workload_parser(subparsers, parent_parser)

    return parser


def add_emission_parser(subparsers, parent_parser):
    message = 'Run emission DEC .'

    parser = subparsers.add_parser(
        DEC_EMISSION_OP,
        parents=[parent_parser],
        description=message,
        help='Emission an dec')


    parser.add_argument(           
        '--proto',                  
        type=str,                  
        default=DEC_PROTO_FILE_NM,      
        help='Proto file with emission params or json directly')        

    parser.add_argument(
        '--name',
        type=str,
        #default=DEC_NAME_DEF,
        help='name of DEC')

    parser.add_argument(
        '--total_sum','-ts',
        type=int,
        #default=DEC_TOTAL_SUM_DEF,
        help='Total amount of DEC tokens')

    parser.add_argument(             
        '--granularity','-gran',                 
        type=float,                    
        #default=DEC_GRANULARITY_DEF,       
        help='Granularity of DEC token') 

    parser.add_argument(     
        '--passkey','-pk',              
        type=str,            
        help='passkey for special operation')  
    parser.add_argument(                    
        '--link',                            
        type=str,                           
        help='URL description'     
        ) 
    parser.add_argument(                      
        '--nominal','-nom',              
        type=float,                           
        #default=DEC_NОMINAL_DEF,              
        help='Nominal of DEC token') 
    parser.add_argument(                
        '--nominal-name','-nnm',             
        type=str,                     
        #default=DEC_NОMINAL_DEF,       
        help='Nominal name')    
     
    parser.add_argument(                   
        '--corporate_share','-cs',                    
        type=int,                        
        #default=DEC_СORPORATE_SHARE_DEF,           
        help='DGT corporate share ') 
    
    parser.add_argument(                    
        '--minting_share','-ms',          
        type=int,                           
        #default=DEC_MINTING_SHARE_DEF,    
        help='Nodes minting share ') 
    parser.add_argument(       
        '--mint','-m',         
        type=str,           # json as string   
        help='mint params')    
    parser.add_argument(                             
        '--mint-umax','-mmax',                               
        type=str,           # json as string         
        help='mint Umax param')                          
    parser.add_argument(                          
        '--mint-t1','-mt1',                    
        type=str,           # json as string      
        help='mint T1 param')
    parser.add_argument(                                             
        '--mint-b2','-mb2',                    
        type=str,           # json as string      
        help='mint B2 param')                   

    parser.add_argument(                 
       '--num_burn','-nb',         
       type=int,                               
       #default=DEC_NBURN_DEF,  
       help='total burn ')  
    parser.add_argument(            
       '--fee',         
       type=float,                   
       #default=DEC_FEE_DEF,      
       help='transaction fee')   
   
    parser.add_argument(              
       '--corporate_account','-ca',                     
       type=str,                     
       help='DGT account'        
       )  
    parser.add_argument(               
      '--corporate_pub_key','-ck',    
      type=str,                       
      help='Corporate public key for managing corporate account'              
      )                                                          
    parser.add_argument(        
       '--wait_to_date','-wtd',                
       type=int,               
       help='Wait to date for actualization of cmd: birth, mint, changemint')       

           
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_emission(args):
    client = _get_client(args)                                
    response = client.emission(args, args.wait)                  
    print(response)                                           

def add_wallet_parser(subparsers, parent_parser):                                                  
    message = 'Create wallet for  DEC token.'                                                                 
                                                                                                 
    parser = subparsers.add_parser(                                                              
        DEC_WALLET_OP,                                                                             
        parents=[parent_parser],                                                                 
        description=message,                                                                     
        help='Create wallet')                                                                   
    
    parser.add_argument(                  
        '--did','-d',                     
        type=str,                         
        help="DID - {'sign' : 'notary sign for did structure','did' :{'val' : 'did value','nkey' : 'notary public key'} }")                       

                                                                                                   
    parser.add_argument(                                                                         
        '--url',                                                                                 
        type=str,                                                                                
        help='specify URL of REST API',                                                          
        default='http://api-dgt-c1-1:8108')                                                      
                                                                                                 
    parser.add_argument(                                                                         
        '--keyfile',                                                                             
        type=str, 
        default="/project/peer/keys/validator.priv",                                                                               
        help="Identify file containing user's private key (by default - validator key)")                                      
                                                                                                 
    parser.add_argument(                                                                         
        '--wait',                                                                                
        nargs='?',                                                                               
        const=sys.maxsize,                                                                       
        type=int,                                                                                
        help='set time, in seconds, to wait for transaction to commit')                          
                                                                                                 
def do_wallet(args):                                                                               
    client = _get_client(args)                                                                   
    response = client.wallet(args, args.wait)                                                      
    print(response)                                                                              


def add_birth_parser(subparsers, parent_parser):
    message = 'Info about  DEC birth.'

    parser = subparsers.add_parser(
        DEC_BIRTH_OP,
        parents=[parent_parser],
        description=message,
        help='Info about dec birth')
    
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_birth(args):
    client = _get_client(args)                                
    response = client.birth(args, args.wait)                  
    print(response)                                           


def add_total_supply_parser(subparsers, parent_parser):
    message = 'Info about  total DEC.'

    parser = subparsers.add_parser(
        DEC_TOTAL_SUPPLY_OP,
        parents=[parent_parser],
        description=message,
        help='Info about dec supply')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_total_supply(args):
    client = _get_client(args)                                
    response = client.total_supply(args, args.wait)                  
    print(response)                                           

def add_token_info_parser(subparsers, parent_parser):
    message = 'Info about  token DEC.'

    parser = subparsers.add_parser(
        DEC_TOKEN_INFO_OP,
        parents=[parent_parser],
        description=message,
        help='Info about dec token')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_token_info(args):
    client = _get_client(args)                                
    response = client.token_info(args, args.wait)                  
    print(response)                                           

def add_burn_parser(subparsers, parent_parser):
    message = 'Burn  DEC token.'

    parser = subparsers.add_parser(
        DEC_BURN_OP,
        parents=[parent_parser],
        description=message,
        help='Burn dec token')
    parser.add_argument(                                       
        '--passkey','-pk',                                     
        type=str,                                              
        help='passkey for special operation')                  
                                                               
    parser.add_argument(                                       
        '--sum','-s',                                          
        type=int,                                              
        help='burn sum')                                       
                                                               
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_burn(args):
    client = _get_client(args)                                
    response = client.burn(args, args.wait)                  
    print(response)                                           


def add_change_mint_parser(subparsers, parent_parser):
    message = 'Change mint  DEC token.'

    parser = subparsers.add_parser(
        DEC_CHANGE_MINT_OP,
        parents=[parent_parser],
        description=message,
        help='Change mint token')
    parser.add_argument(                                       
        '--passkey','-pk',                                     
        type=str,                                              
        help='passkey for special operation')                  

    parser.add_argument(                                       
        '--mint','-m',                                          
        type=str,                                              
        help='mint params')                                       
    parser.add_argument(                                        
        '--mint-umax','-mmax',                                  
        type=str,           # json as string                    
        help='mint Umax param')                                 
    parser.add_argument(                                        
        '--mint-t1','-mt1',                                     
        type=str,           # json as string                    
        help='mint T1 param')                                   
    parser.add_argument(                                        
        '--mint-b2','-mb2',                                     
        type=str,           # json as string                    
        help='mint B2 param')                                   

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_change_mint(args):
    client = _get_client(args)                                
    response = client.change_mint(args, args.wait)                  
    print(response)                                           

def add_distribute_parser(subparsers, parent_parser):
    message = 'Info about distribute token DEC.'

    parser = subparsers.add_parser(
        DEC_DISTRIBUTE_OP,
        parents=[parent_parser],
        description=message,
        help='Info about distribute dec token')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_distribute(args):
    client = _get_client(args)                                
    response = client.distribute(args, args.wait)                  
    print(response)                                           

def add_faucet_parser(subparsers, parent_parser):
    message = 'Faucet an DEC to <pubkey> by <value>.'

    parser = subparsers.add_parser(
        DEC_FAUCET_OP,
        parents=[parent_parser],
        description=message,
        help='faucet  DEC token')
    parser.add_argument(                              
        'pubkey',                                       
        type=str,                                     
        help='identify name of key to increment')     
                                                      
    parser.add_argument(                              
        'value',                                      
        type=int,                                     
        help='specify amount to send')           

    parser.add_argument(                                       
        '--passkey','-pk',                                     
        type=str,                                              
        help='passkey for special operation')                  

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_faucet(args):
    client = _get_client(args)                                
    response = client.faucet(args, args.wait)                  
    print(response)                                           

def add_mint_parser(subparsers, parent_parser):
    message = 'Mint  DEC token.'

    parser = subparsers.add_parser(
        DEC_MINT_OP,
        parents=[parent_parser],
        description=message,
        help='Mint DEC token')

    parser.add_argument(                                       
        '--corporate_wallet','-cw',                                     
        type=str,                                              
        help='corporate wallet')                  

    parser.add_argument(                                       
        '--sum','-s',                                          
        type=int,                                              
        help='Sum ')  
    parser.add_argument(          
        '--pub_key','-pub',       
        type=str,                                                      
        help='pub key')   
    parser.add_argument(      
        '--did','-d',   
        type=str,             
        help='DID')       
            
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        default="/project/peer/keys/validator.priv",
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_mint(args):
    client = _get_client(args)                                
    response = client.mint(args, args.wait)                  
    print(response) 
    
def add_heart_beat_parser(subparsers, parent_parser):
    message = 'Heartbeat  DEC token.'

    parser = subparsers.add_parser(
        DEC_HEART_BEAT_OP,
        parents=[parent_parser],
        description=message,
        help='Heart beat dec network')

    parser.add_argument(                                       
        '--passkey','-pk',                                     
        type=str,                                              
        help='passkey or Dag position ')                  

    parser.add_argument(                                       
        '--period','-p',                                          
        type=int,
        default=DEC_HEART_BEAT_PERIOD_DEF,                                              
        help='Period of heartbeat cmd ')
      
    parser.add_argument(          
        '--pub_keys','-ps',       
        type=str,                                                      
        help='pub keys')   
          
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_heart_beat(args):
    client = _get_client(args)                                
    response = client.heart_beat(args, args.wait)                  
    print(response)                                           

def add_seal_count_parser(subparsers, parent_parser):
    message = 'seal count  DEC token.'

    parser = subparsers.add_parser(
        DEC_SEAL_COUNT_OP,
        parents=[parent_parser],
        description=message,
        help='Seal count')

    parser.add_argument(          
        '--pub_key','-pub',       
        type=str,                                                      
        help='pub key')   

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_seal_count(args):
    client = _get_client(args)                                
    response = client.seal_count(args, args.wait)                  
    print(response)                                           

def add_balance_of_parser(subparsers, parent_parser):
    message = 'Balance of DEC token for <pubkey>.'

    parser = subparsers.add_parser(
        DEC_BALANCE_OF_OP,
        parents=[parent_parser],
        description=message,
        help='balance  DEC token')

    parser.add_argument(                             
        'pubkey',                                    
        type=str,                                    
        help='identify name of pubkey')    


    parser.add_argument(                                       
        '--asset_type','-at',                                     
        type=str,
        default=DEC_NAME_DEF,                                              
        help='passkey for special operation')                  

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_balance_of(args):
    client = _get_client(args)                                
    token = client.balance_of(args, args.wait) 
    if token:
        dec = cbor.loads(token.dec) if token.group_code  in DEC_TYPES else {}
        print("{}: {}={} : ".format(args.pubkey,args.asset_type,token.decimals if DEC_TOTAL_SUM not in dec else dec[DEC_TOTAL_SUM]))
    else:
        print("{} - undefined".format(args.pubkey))
    
def add_send_parser(subparsers, parent_parser):
    message = 'Send DEC <from> <to> <amount>.'
    parser = subparsers.add_parser(
        DEC_SEND_OP,
        parents=[parent_parser],
        description=message,
        help='Send token from to')
    parser.add_argument(                      
        'name',                 
        type=str,                             
        help='From wallet') 
    parser.add_argument(                      
        'to',                
        type=str,                             
        help='to wallet') 
    parser.add_argument(    
        'amount',        
        type=int,           
        help='number token for transfer')   
    parser.add_argument(           
        '--did','-d',              
        type=str,                  
        help='DID')                

    parser.add_argument(                                       
        '--asset_type','-at',                                     
        type=str,
        default=DEC_NAME_DEF,                                              
        help='Asset type (DEC as default)')                  
                                          
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')
    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")
    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_send(args):
    client = _get_client(args)                                
    response = client.send(args, args.wait)                  
    print(response) 

def add_pay_parser(subparsers, parent_parser):
    message = 'Pay DEC <from> <to> <amount> .'
    parser = subparsers.add_parser(
        DEC_PAY_OP,
        parents=[parent_parser],
        description=message,
        help='Pay token for')
    parser.add_argument(                     
        'name',                              
        type=str,                            
        help='From wallet')                  
    parser.add_argument(                     
        'to',                                
        type=str,                            
        help='to wallet')                    
    parser.add_argument(                     
        'amount',                            
        type=int,                            
        help='number token for transfer') 
       
    parser.add_argument(           
        '--did','-d',              
        type=str,                  
        help='DID')                
    parser.add_argument(            
        '--target','-tg',         
        type=str,                   
        help='Target specification')             
    parser.add_argument(                                       
        '--asset_type','-at',                                     
        type=str,                                              
        help='passkey for special operation')                  
    parser.add_argument(                                       
        '--pub_key','-pub',                                          
        type=str,                                              
        help='pub key')                                       
    parser.add_argument(     
        '--provement_key','-prov',  
        type=str,            
        help='Provement key refer to prov key from invoice')      
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')
    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")
    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_pay(args):                                  
    client = _get_client(args)                      
    response = client.pay(args, args.wait)   
    print(response)                                 


def add_invoice_parser(subparsers, parent_parser):
    message = 'invoice for PAY <prove_key> <pub_key> .'
    parser = subparsers.add_parser(
        DEC_INVOICE_OP,
        parents=[parent_parser],
        description=message,
        help='invoice for pay operation')
    parser.add_argument(         
        'prove_key', 
        type=str,                
        help='Prove key')          
    parser.add_argument(      
        'pub_key',   
        type=str,             
        help='Pub key')       

    parser.add_argument(                  
        'amount',                         
        type=int,                         
        help='number token for transfer')
       
    parser.add_argument(            
        '--target','-tg',         
        type=str,                   
        help='Target specification')             
    parser.add_argument(                                       
        '--available_till','-at',                                     
        type=str,
        default = AVAILABLE_TILL_DEF,                                              
        help='available_till')                  

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')
    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")
    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_invoice(args):
    client = _get_client(args)                                
    response = client.invoice(args, args.wait)                  
    print(response) 

def add_bank_list_parser(subparsers, parent_parser):
    message = 'Bank list .'
    parser = subparsers.add_parser(
        DEC_BANK_LIST_OP,
        parents=[parent_parser],
        description=message,
        help='Bank list')

    parser.add_argument(           
        '--did','-d',              
        type=str,                  
        help='DID')                

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')
    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")
    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def do_bank_list(args):
    client = _get_client(args)                                
    response = client.bank_list(args, args.wait)                  
    print(response) 

def add_mint_parser(subparsers, parent_parser):                                            
    message = 'Mint DEC for <key>.'                                            
    parser = subparsers.add_parser(                                                       
        DEC_MINT_OP,                                                                       
        parents=[parent_parser],                                                          
        description=message,                                                              
        help='Mint token for peer')                                                             
    parser.add_argument(                                                                  
        'pubkey',                                                                           
        type=str,                                                                         
        help='Peer pub key')                                                               
                                                                                          
    parser.add_argument(                                                                  
        '--did','-d',                                                                     
        type=str,                                                                         
        help='DID')                                                                       
    parser.add_argument(                                                                  
        '--sum','-s',                                                                 
        type=str,                                                                         
        help='Token amount')
                                                          
    parser.add_argument(                                                                  
        '--url',                                                                          
        type=str,                                                                         
        help='specify URL of REST API',                                                   
        default='http://api-dgt-c1-1:8108')                                               
    parser.add_argument(                                                                  
        '--keyfile',                                                                      
        type=str,                                                                         
        help="identify file containing user's private key")                               
    parser.add_argument(                                                                  
        '--wait',                                                                         
        nargs='?',                                                                        
        const=sys.maxsize,                                                                
        type=int,                                                                         
        help='set time, in seconds, to wait for transaction to commit')   
                    
def do_mint(args):                                   
    client = _get_client(args)                            
    response = client.mint(args, args.wait)          
    print(response)                                       


def add_set_parser(subparsers, parent_parser):
    message = 'Sends an bgt transaction to set <name> to <value>.'

    parser = subparsers.add_parser(
        'set',
        parents=[parent_parser],
        description=message,
        help='Sets an dec value')

    parser.add_argument(
        'name',
        type=str,
        help='name of key to set')

    parser.add_argument(
        'value',
        type=int,
        help='amount to set')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')


def do_set(args):
    name, value, wait = args.name, args.value, args.wait
    client = _get_client(args)
    response = client.set(name, value, wait)
    print(response)


def add_inc_parser(subparsers, parent_parser):
    message = 'Sends an bgt transaction to increment <name> by <value>.'

    parser = subparsers.add_parser(
        'inc',
        parents=[parent_parser],
        description=message,
        help='Increments an bgt value')

    parser.add_argument(
        'name',
        type=str,
        help='identify name of key to increment')

    parser.add_argument(
        'value',
        type=int,
        help='specify amount to increment')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')


def do_inc(args):
    name, value, wait = args.name, args.value, args.wait
    client = _get_client(args)
    response = client.inc(name, value, wait)
    print(response)


def add_dec_parser(subparsers, parent_parser):
    message = 'Sends an bgt transaction to decrement <name> by <value>.'

    parser = subparsers.add_parser(
        'dec',
        parents=[parent_parser],
        description=message,
        help='Decrements an bgt value')

    parser.add_argument(
        'name',
        type=str,
        help='identify name of key to decrement')

    parser.add_argument(
        'value',
        type=int,
        help='amount to decrement')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')

def add_trans_parser(subparsers, parent_parser):
    message = 'Sends an bgt transaction from <name> to  <to> by <value>.'

    parser = subparsers.add_parser(
        'trans',
        parents=[parent_parser],
        description=message,
        help='transfer an bgt value from vallet to vallet')

    parser.add_argument(
        'name',
        type=str,
        help='identify name of key transfer from')

    parser.add_argument(
        'value',
        type=int,
        help='amount to transfer')

    parser.add_argument(
        'to',
        type=str,
        help='identify name of key transfer to')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
            help='set time, in seconds, to wait for transaction to commit')


def do_dec(args):
    name, value, wait = args.name, args.value, args.wait
    client = _get_client(args)
    response = client.dec(name, value, wait)
    print(response)

def do_trans(args):
    name, value,to, wait = args.name, args.value, args.to, args.wait
    client = _get_client(args)
    response = client.trans(name, value, to, wait)
    print(response)


def add_show_parser(subparsers, parent_parser):
    message = 'Shows the value of the key <name>.'

    parser = subparsers.add_parser(
        'show',
        parents=[parent_parser],
        description=message,
        help='Displays the specified bgt value')

    parser.add_argument(
        'name',
        type=str,
        help='name of key to show')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')


def do_show(args):
    name = args.name
    client = _get_client(args)
    token = client.show(name)
    dec = cbor.loads(token.dec) if token.group_code  in DEC_TYPES else {}
    print('{}: {}={} dec={}'.format(name,token.group_code,token.decimals,dec))


def add_list_parser(subparsers, parent_parser):
    message = 'Shows the values of all keys in bgt state.'

    parser = subparsers.add_parser(
        'list',
        parents=[parent_parser],
        description=message,
        help='Displays all bgt values')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API',
        default='http://api-dgt-c1-1:8108')


def do_list(args):
    client = _get_client(args)
    results = client.list()
    token = DecTokenInfo()
    for pair in results:
        for name, value in pair.items():
            token.ParseFromString(value)
            dec = cbor.loads(token.dec) if token.group_code in DEC_TYPES else {}

            print('{}: {}={} dec={}'.format(name,token.group_code,token.decimals,dec))


def _get_client(args):
    return DecClient(
        url=DEFAULT_URL if args.url is None else args.url,
        keyfile=_get_keyfile(args))


def _get_keyfile(args):
    try:
        if args.keyfile is not None:
            return args.keyfile
    except AttributeError:
        return None

    real_user = getpass.getuser()
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".dgt", "keys")

    return '{}/{}.priv'.format(key_dir, real_user)


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose
    setup_loggers(verbose_level=verbose_level)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == DEC_SET_OP:
        do_set(args)
    elif args.command == DEC_INC_OP:
        do_inc(args)
    elif args.command == DEC_DEC_OP:
        do_dec(args)
    elif args.command == DEC_TRANS_OP:
        do_trans(args)
    elif args.command == DEC_EMISSION_OP:          
        do_emission(args)                        
    elif args.command == DEC_WALLET_OP:         
        do_wallet(args)                               
    elif args.command == DEC_BIRTH_OP:             
        do_birth(args)                             
    elif args.command == DEC_TOTAL_SUPPLY_OP:      
        do_total_supply(args)                      
    elif args.command == DEC_TOKEN_INFO_OP:        
        do_token_info(args)                         
    elif args.command == DEC_BURN_OP:        
        do_burn(args) 
    elif args.command == DEC_CHANGE_MINT_OP:                             
        do_change_mint(args)                         
    elif args.command == DEC_DISTRIBUTE_OP:         
        do_distribute(args) 
    elif args.command == DEC_FAUCET_OP:                               
        do_faucet(args)                                               
    elif args.command == DEC_MINT_OP:                                 
        do_mint(args)                           
    elif args.command == DEC_HEART_BEAT_OP:            
        do_heart_beat(args)                            
    elif args.command == DEC_SEAL_COUNT_OP:                
        do_seal_count(args)                                
    elif args.command == DEC_BALANCE_OF_OP:                
        do_balance_of(args)                                
    elif args.command == DEC_SEND_OP:                      
        do_send(args)                                      
    elif args.command == DEC_PAY_OP:                       
        do_pay(args)                                
    elif args.command == DEC_INVOICE_OP:          
        do_invoice(args)                          
    elif args.command == DEC_BANK_LIST_OP:           
        do_bank_list(args)                          
        
    elif args.command == 'show':
        do_show(args)
    elif args.command == 'list':
        do_list(args)
    elif args.command == 'generate':
        do_generate(args)
    elif args.command == 'populate':
        do_populate(args)
    elif args.command == 'load':
        do_load(args)
    elif args.command == 'create_batch':
        do_create_batch(args)
    elif args.command == 'workload':
        do_workload(args)

    else:
        raise DecCliException("invalid command: {}".format(args.command))


def main_wrapper():
    # pylint: disable=bare-except
    sys.stdout = open(1, 'w', encoding='utf-8', closefd=False) #sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except (DecCliException, DecClientException) as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        raise e
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
