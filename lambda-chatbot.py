"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
codepipeline = boto3.client('codepipeline')
pipeline = 'Octank-Prod-DeploymentPipeline-Y5H8NTER05SJ-Pipeline-17LNW3W15JBUC'


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def check_status(pipeline, stage):
    """Check the latest status of deployment
    
    Args:
        pipeline: The CodePipeline name
        stage: The stage to check the status
        
    """
    if 'all' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates']
    elif 'source' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates'][0]
    elif 'build' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates'][1]
    elif 'qa-deploy' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates'][2]
    elif 'testing' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates'][3]      
    elif 'approval' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates'][4]  
    elif 'prod-deploy' in stage:
        status = codepipeline.get_pipeline_state(name=pipeline)['stageStates'][5]
    return status

def release_change(pipeline):
    
    start_pipeline = codepipeline.start_pipeline_execution(name=pipeline)
    return start_pipeline


def octank_pipeline(intent_request):
    
    slots = get_slots(intent_request)
    if 'stage' in slots:
        stage = get_slots(intent_request)["stage"].lower()
        status_response = json.dumps(check_status(pipeline, stage), indent=4, sort_keys=True, default=str)
        return close(intent_request['sessionAttributes'],
                'Fulfilled',
                {'contentType': 'PlainText',
                  'content': 'Deployment status {}'.format(status_response)})
                  
    elif 'trigger' in slots:
        trigger = get_slots(intent_request)["trigger"].lower()
        trigger_response = json.dumps(release_change(pipeline), indent=4, sort_keys=True, default=str)
        return close(intent_request['sessionAttributes'],
                'Fulfilled',
                {'contentType': 'PlainText',
                  'content': 'Deployment status: {}'.format(trigger_response)})

    elif 'help' in slots:
        message = '----------------------\nBOTTANK HELP\n----------------------\n\
Bottank uses Amazon Lex to understand natural language, these are some of the options you can use:\n\
1) Check latest deployment status:\n\tExamples: "What is the status of the prod-deploy", "Status of the testing"\n\
\t Available options: all, source, build, qa-deploy, testing, approval, prod-deploy\n\
2) Trigger Deployment:\n\tExamples: "Start deployment", "Release change"\n'
        return close(intent_request['sessionAttributes'],
                'Fulfilled',
                {'contentType': 'PlainText',
                  'content': '{}'.format(message)})

""" --- Main handler --- """

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return octank_pipeline(event)
