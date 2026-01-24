# conditions to send emails:
 1. onSale = true (regardless of price)
    * send email saying product is on sale, and state salePrice
 1. regularPrice <= desired price
    * does not matter if product is on sale or not

# Other factors to consider:
 1. if notifying about sale
    1. (str) orderable = Available
    1. (float) dollarSavings
    1. (str) percentSavings
    1. (str) url

 1. if notifying about regular price coming down
    1. (str) orderable = Available
    1. (str) url

NOTE: keys with missing values are either `empty` or `null`



# Other considerations:
1. how to handle products with really long names?
1. what happens if http status_code != 200? - do i notify user?




# TODO
 1. replace smtp sending with gmail API (smtp is auto rejecting emails since they contain hyperlinks)
 1. 
