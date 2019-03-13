# Easy Pay

Easy Pay is a full-stack web-application that holds money on behalf of transacting parties who have met over the internet. 

Its mission is to help consumers avoid scammers who ask for payment before the consumer has had the chance to verify the product. Both consumer and seller can view and agree to a contract which will determine the date and amount of payment to the seller providing he/she adheres to the terms outlined. Once agreed, the consumer will then send the money to Easy Pay, who will hold the funds until payment day when it will be automatically sent to the seller (providing the terms of the contract have not been broken).


##Contents
* [Tech Stack](#technologies)
* [Features](#features)
* [About Me](#aboutme)

## <a name="technologies"></a>Technologies
Backend: Python, Flask, PostgreSQL, SQLAlchemy<br/>
Frontend: JavaScript, jQuery, AJAX, Jinja2, Bootstrap, HTML5, CSS3, D3<br/>
APIs: Stripe, Mailgun<br/>

## <a name="features"></a>Features

<img width="1271" alt="screen shot 2017-03-08 at 12 54 01" src="https://cloud.githubusercontent.com/assets/24640757/23724006/194bc728-0400-11e7-827f-b0ae2e60449d.png">

Users can sign in and log in to Easy Pay to get started. 
<img width="1271" alt="screen shot 2017-03-08 at 12 54 23" src="https://cloud.githubusercontent.com/assets/24640757/23724008/194ce93c-0400-11e7-8a32-a1fde6d32c10.png">

When a payer goes to their dashboard they can see both past and present transactions.
<img width="1274" alt="screen shot 2017-03-08 at 12 55 05" src="https://cloud.githubusercontent.com/assets/24640757/23724007/194c4ec8-0400-11e7-9f7a-204978fb842f.png">

To create a new transaction they click on the 'Create a Transaction' button and will be shown a contract. The payer will enter the payment date and amount and also the recipients name and email address. An email prompt is sent using Mailgun to the seller who will be prompted to log into Easy Pay with their new details and view and approve the contract. 
<img width="1274" alt="screen shot 2017-03-08 at 12 55 27" src="https://cloud.githubusercontent.com/assets/24640757/23724005/194b7c14-0400-11e7-8bcc-d19383fb6caf.png">

When the seller goes onto their dashboard they are given the option to view and approve or decline the contract. 
<img width="1271" alt="screen shot 2017-03-08 at 12 56 57" src="https://cloud.githubusercontent.com/assets/24640757/23723974/ff5d532c-03ff-11e7-9d01-4bd457335f13.png">

The payer will then be prompted both by email and on their dashboard to pay the agreed amount to Easy Pay. This is enabled using the Stripe api which transfers the money into Easy Pay's stripe account. 
<img width="1274" alt="screen shot 2017-03-08 at 12 57 43" src="https://cloud.githubusercontent.com/assets/24640757/23723980/0319ce50-0400-11e7-9cb1-1f0266a4e487.png">

Once the payer has paid, the seller will then be prompted to put in their account details if they would eventually like to receive the money. 
<img width="1271" alt="screen shot 2017-03-08 at 12 59 20" src="https://cloud.githubusercontent.com/assets/24640757/23723984/044bab7c-0400-11e7-9c1e-fd09bd8d25f1.png">

Once all of this is done, the payment will be automatically transferred to the seller on the agreed payment date. This is automated using cron. 


## <a name="aboutme"></a>About Me
Originally from London, I moved to San Francisco at the start of 2017. I created this site because I wanted to solve a problem for people who feel like they are being scammed into paying for a product online before they have had the chance to verify the product. 
Visit me on [LinkedIn](https://www.linkedin.com/in/rayhana-ziai).