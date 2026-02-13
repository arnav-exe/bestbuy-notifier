# TODO
 - RETRIES + EXPONENTIAL BACKOFF WILL HAVE TO BE A FUNCTION DECORATOR OR SMTN GLOBAL - DO NOT IMPLEMENT THIS PER DATASOURCE
 - PASS LOGGER TO EACH DATASOURCE INSTANTIATION, FOR GRANULAR, PER-DATASOURCE LOGGING. FORMAT SHOUDL LOOKE LIKE THIS:
 "{timestamp} [{error_severity} - {data_source}]: {log_message}"
 CAN POTENTIALLY DEFINE THIS IN THE FORMATTER



# FLOW:
 1. for each product:
    1. for each identifier inside a product:
        1. if we have a matching data source for that particular identiifer, run 'fetch_product()' which will return data in Product obj format
        1. check in stock and sale keys against user specification
        1. if any condition is met, fire appropriate ntfy



# SOURCES TO ADD:
 - amazon - amazon product api
 - lenovo website - crawl4ai
 - costco - crawl4ai
 - bhvideo - crawl4ai
