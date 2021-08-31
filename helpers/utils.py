import json
import helpers.constants as const


def wait_for_bundle_requests(driver, seq, increment):
    driver.wait_for_request(f'rs.fullstory.com/rec/bundle.*?Seq={int(seq) + increment}', 120)


def initial_wait_for_requests(driver):
    driver.wait_for_request(f'rs.fullstory.com/rec/bundle', 20)


def get_last_seq(driver):
    bundle_requests = [json.loads(request.body) for request in driver.requests if
                       "rs.fullstory.com/rec/bundle" in request.url]
    seq = bundle_requests[-1]['Seq']
    return seq


def validate_event(driver, operation, *args):
    bundle_requests = [json.loads(request.body) for request in driver.requests if
                       "rs.fullstory.com/rec/bundle" in request.url]

    for bundle_request in bundle_requests:
        for event in bundle_request['Evts']:
            if event['Kind'] == operation:
                if len(args) > 0:
                    if operation == const.CUSTOM_EVENT and args[0] in json.loads(event['Args'][1])['displayName_str']:
                        return True
                    elif operation == const.NAVIGATE_EVENT and event['Args'][0] == args[0]:
                        return True
                return True
    return False


def is_text_present_in_requests(driver, search_string):
    bundle_requests = "".join(
        [str(request.body) for request in driver.requests if "rs.fullstory.com/rec/bundle" in request.url])
    return const.CREDIT_CARD_NUMBER in bundle_requests
