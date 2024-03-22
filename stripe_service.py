import stripe
import os
from db_service import update_subscription_status, update_user

stripe_keys = {
        "secret_key": os.getenv("STRIPE_SECRET_KEY"),
        "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
        "endpoint_secret_key": os.getenv("STRIPE_ENDPOINT_KEY")
    }

PRICE_ID = 'price_1OvUGz07NdmpHOylRC2zHUCZ'

def create_intent(amount, customer):
    print(stripe_keys["publishable_key"])
    stripe.api_key = stripe_keys["secret_key"]
    print("Call strip paymentIntent.create")
    intent = stripe.PaymentIntent.create(
        amount,
        currency = "usd",
        automatic_payment_methods={
            "enabled": True,
        },
    
      metadata = {
          'customer': customer
      }
    )
    return intent

def handle_webhooks(request):
    event = None
    payload = request.data
    sig_header = request.headers.get('stripe_signature')
    print(f"sig_header: {sig_header}")
    endpoint_secret_key = stripe_keys["endpoint_secret_key"]

    #print (f"payload: {payload}")
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret_key
        )
        #print(f"event:{event}")
        data = event['data']
    except ValueError as e:
        raise e
    except stripe.error.SignatureVerificationError as e:
        raise e
    
    event_type = event['type']
    
    if event_type == 'payment_intent.succeeded':
        print("event:payment_intent.succeed")
        payment_intent = event['data']['object']
        user_uuid = payment_intent['metadata']['consumer']
        print(f"Event: payment_intent.succeeded, User {user_uuid} completed a payment.")
    elif event_type == 'payment_intent.payment_failed':
        print(f"Event:payment_intent.payment_failed")
        #print(data)
    elif event_type == 'payment_intent.canceled':
        print(f"Event:payment_intent.canceled")
        #print(data)
    elif event_type == 'payment_created':
        print(f"Event:payment_created")
        #print(data)
    elif event_type == 'invoice.paid':
        print(f"Event:invoice.paid")
        print(data['object'])
        if 'object' in data and 'customer' in data['object']:
            customer = data['object']['customer']
            print(f"customer:{customer}")
            update_subscription_status(customer=customer, status='active')
            print(data)
        else:
            print(f"no customer in event data: {data}")
    elif event_type == 'invoice.payment_failed':
        print(f"Event:invoice.payment_failed")
        #print(data)
    else:
        print("Unhandled event type {}".format(event['type']))

    return event

def create_subscription(user):
    stripe.api_key = stripe_keys["secret_key"]
    result = stripe.Customer.search(query=f"email: '{user.email}'")
    if len(result.data) != 0:
        customer = result.data[0]
    else:
        customer = stripe.Customer.create(email=user.email, name=user.name, metadata={user: user.id})
        user.customer = customer.id
        update_user(user)
    
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{ 'price': PRICE_ID }],
        payment_behavior='default_incomplete',
        payment_settings={'save_default_payment_method': 'on_subscription'},
        expand=['latest_invoice.payment_intent'],
    )
    return subscription