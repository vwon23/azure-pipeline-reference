import sys, os
import datetime
import configparser
import logging, logging.config
import boto3

import datetime as dt
import pytz
from pytz import timezone


def init(path_app_run):
    '''
    creates global variable class to handle the variables across scripts and functions. Sets the provided application run path as gvar.dname

    Parameters
    ---------------
    path_app_run: path
        Directory path of app_run (e.g. app/app_run) returned from os.path.dir() function
    '''
    ## create a class to hold global variables ##
    class global_variables:
        variable_1 = 'value'

    global gvar
    gvar = global_variables()
    gvar.dname = path_app_run
    print(f'Application run path set as: {path_app_run}')


def get_config():
    '''
    Sets gvar with various configuration values that are required to run. Require cf.init() to run first

    Parameters
    ---------------
    None
    '''
    if os.environ['env'].upper() == 'DEV':
        gvar.env = 'dev'
    elif os.environ['env'].upper() == 'TEST':
        gvar.env = 'test'
    elif os.environ['env'].upper() == 'STAGE':
        gvar.env = 'stage'
    elif os.environ['env'].upper() == 'PROD':
        gvar.env = 'prod'

    config = configparser.ConfigParser()
    config.read(os.path.join(gvar.dname, 'config', 'config.cfg'))

    ## path variables ##
    gvar.path_app = os.path.dirname(gvar.dname)
    #gvar.path_app = config.get('Paths', 'HOME_DIR')
    gvar.path_log = os.path.join(gvar.path_app, 'logs')
    gvar.path_logconfig = os.path.join(gvar.dname, 'config', 'logging.cfg')
    gvar.path_data = os.path.join(gvar.path_app, 'data')

    ## create directories during run time
    if not os.path.exists(gvar.path_log):
        os.makedirs(gvar.path_log)
    if not os.path.exists(gvar.path_data):
        os.makedirs(gvar.path_data)

    ## AWS Variables
    #gvar.aws_rgn = config.get('AWS_INFO', 'REGION')
    gvar.aws_rgn = os.environ['aws_rgn']
    gvar.aws_s3_bucket = config.get('AWS_INFO', 'S3_BUCKET').format(env = gvar.env, aws_rgn = gvar.aws_rgn)
    gvar.aws_s3_bucket_name = gvar.aws_s3_bucket.split('//')[1]


def set_logger(loggername, filename):
    '''
    Sets logger based on selected loggername & Outputs to provided filename

    Parameters
    ---------------
    loggername: str
        The name of logger to set as. (The log name will be searched in logging.cfg to check config setting)
    filename: str
        the name to store logfile as

    Returns
    ---------------
    logger
        logger derived from logging.getLogger(loggername)
    '''
    
    # if not os.path.exists(gvar.path_log):
    #     os.makedirs(gvar.path_log)

    gvar.path_logfile = os.path.join(gvar.path_log, filename)
    logging.config.fileConfig(gvar.path_logconfig, defaults={'logfilename': gvar.path_logfile})

    gvar.logger = logging.getLogger(loggername)
    global logger
    logger = logging.getLogger(__name__)
    logger.info(f'logs being written to {gvar.path_logfile}')
    return gvar.logger


def upload_log_s3(log_path, s3_bucket_name, file_name):
    '''
    Uploads log file in provided path to s3 bucket

    Parameters
    ---------------
    log_path: path
        path of a log file
    s3_bucket_name: str
        the name of s3 bucket to upload to
    filename: str
        name to store log file as

    Returns
    ---------------
    None
    '''
    s3c = boto3.client('s3')
    folder_name = 'logs'
    file_key = f'{folder_name}/{file_name}'
    logfile = open(log_path, 'rb')
    s3c.put_object(Body=logfile, Bucket=s3_bucket_name, Key=file_key)
    logger.info(f'log {log_path} uploaded to s3 {s3_bucket_name} as {file_key}')


###  Datetime functions  ###
def get_current_datetime():
    '''
    Sets variables for current date/time values.

    Parameters
    ---------------
    None
    '''
    ## UTC Time variables ##
    gvar.current_utc = dt.datetime.now()
    gvar.current_datetime_utc = gvar.current_utc.strftime("%Y-%m-%d %H:%M:%S")

    ## PST Time variables
    gvar.current_pst = dt.datetime.now().astimezone(timezone('US/Pacific'))
    gvar.current_year_pst = gvar.current_pst.strftime("%Y")
    gvar.current_date_pst = gvar.current_pst.strftime("%Y-%m-%d")
    gvar.current_datetime_pst = gvar.current_pst.strftime("%Y-%m-%d %H:%M:%S")

    print(f'Current Time in PST: {gvar.current_datetime_pst}')

def convert_timestmp_int(timestmp_int):
    '''
    Converts timestamp value in integer to string.

    Parameters
    ---------------
    timestmp_int: int
        timestamp value in integer

    Returns
    ---------------
    timestmp_str: str
        timestamp value in str
    '''
    timestmp_pst_str = dt.datetime.fromtimestamp(timestmp_int).astimezone(timezone('US/Pacific')).strftime("%Y-%m-%d %H:%M:%S")
    return timestmp_pst_str