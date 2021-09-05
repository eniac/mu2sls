#!/usr/bin/env python3
import argparse
import logging
import os

from compiler import compiler

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="the input file to be compiled (must contain a service)")
    parser.add_argument("output", help="the output file that will contain a serverless handler")
    parser.add_argument("-l", "--log_level",
                        help="the logging level",
                        choices=['debug', 'info', 'warn', 'error'],
                        default='info')
    parser.add_argument("-s", "--sls_backend",
                        help="the serverless backend",
                        choices=['openfaas'],
                        default='openfaas')
    args = parser.parse_args()

    ## Print all the arguments before they are modified below
    logging.debug("Arguments:")
    for arg_name, arg_val in vars(args).items():
        logging.debug(arg_name + str(arg_val))
    logging.debug("-" * 40)
    return args


def main():
    args = parse_args()
    source_file = args.input
    out_file = args.output

    ## TODO: Do something with the -s and -l args

    compiler.compile_service_module(source_file, out_file)

if __name__ == "__main__":
    main()