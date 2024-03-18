import stripe
import os

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

def check_intent(request):
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    endpoint_secret_key = stripe_keys["endpoint_secret_key"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret_key
        )
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            user_uuid = payment_intent['metadata']['consumer']
            print(f"User {user_uuid} completed a payment.")

        else:
            print("Unhandled event type {}".format(event['type']))
    except ValueError as e:
        raise e
    except stripe.error.SignatureVerificationError as e:
        raise e
    
    return event

def create_subscription(user):
    stripe.api_key = stripe_keys["secret_key"]
    result = stripe.Customer.search(query=f"email: '{user.email}'")
    if len(result.data) != 0:
        customer = result.data[0]
    else:
        customer = stripe.Customer.create(email=user.email, name=user.name)
    
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{ 'price': PRICE_ID }],
        payment_behavior='default_incomplete',
        payment_settings={'save_default_payment_method': 'on_subscription'},
        expand=['latest_invoice.payment_intent'],
    )
    return subscription