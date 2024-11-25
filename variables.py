
# can change any of these for testing purposes


# MAX_BATCH_SIZE is the number of ContentDocument records returned in a single query. If limit argument is > 
# this value, then multiple iterations of queries will happen
# default to 100 since too large a batch turns into too large an api call for deleting records
MAX_BATCH_SIZE = 100

# arbitrary value. Once the org gets below this number, stop running backup
# we normally have over 1m we don't use each day.
MIN_API_REQUESTS_REMAINING_TO_RUN = 70000