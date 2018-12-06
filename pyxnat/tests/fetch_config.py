#!/usr/bin/env python2
import argparse
import json
import logging as log
import os.path as op

if __name__ == '__main__':
    config_file = '.xnat.cfg'
    parser = argparse.ArgumentParser(description='Retrieve login info and store it in a temp file')
    parser.add_argument("host")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--jsessionid")
    parser.add_argument('--verify', action='store_true', default=False)

    args = parser.parse_args()
    log.basicConfig(level=log.INFO)
    j = {"server": args.host,
         "verify": args.verify}
    if args.password and args.user :
        j.update( { 'user'    : args.user,
                    'password': args.password })
        log.info('Mode USER/PASSWORD')
    elif args.jsessionid is not None:
        j['jsession_id'] = args.jsessionid
        log.info('Mode JSESSIONID')
    else:
        raise Exception('Missing arguments (JSESSIONID or USER/PASSWORD)')
    json.dump(j, open(op.abspath(config_file), 'w'), indent=2)
    log.info('Saved in %s'%op.abspath(config_file))
