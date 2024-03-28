import sys, os
import boto3

## Find path of the script then find the path of parent folder and add it to system path ##
path_script = os.path.abspath(__file__)
path_app_run = os.path.dirname(os.path.dirname(path_script))
sys.path.append(path_app_run)

## use common functions to initalize global variable and set logger ##
import utilities.common_functions as cf

cf.init(path_app_run)
cf.get_config()
cf.get_current_datetime()

loggername = 'hw_dynamodb'
logfile_name = f'{loggername}_{cf.gvar.current_date_pst}.log'
logger = cf.set_logger(loggername, logfile_name)


## write to dynamoDB ##
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('message_tracker')

try:
    response = table.put_item(
        Item={
            'year': cf.gvar.current_year_pst,
            'datetime': cf.gvar.current_datetime_pst,
            'message': 'Hello World on ' + cf.gvar.current_datetime_pst
        }
    )
except:
    logger.exception('Exception occured while puting item in DynamoDB table')
else:
    request_http_status = response['ResponseMetadata']['HTTPStatusCode']
    logger.info(f'Request to put item in DynamoDB table returned with HTTPStatusCode {request_http_status}')

## upload log file to s3 ##
cf.upload_log_s3(log_path=cf.gvar.path_logfile, s3_bucket_name=cf.gvar.aws_s3_bucket_name, file_name=logfile_name)