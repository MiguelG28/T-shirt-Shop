import requests
from store.models import Order
from django.contrib.auth.models import User

def send_simple_message(request):
    user = User.objects.get(id=request.user.id)
    order_id = Order.objects.filter(user=user).last().id
    print ('order')
    user_email = user.email
    return requests.post(
        "https://api.mailgun.net/v3/sandboxe3c453f8f4ff4ce7a3c0f3b450c31af1.mailgun.org/messages",
        auth=("api", "de1d34a461584c85f12cb1ee77c680f4-bd350f28-b35ebfb9"),
        data={"from": "Django Store <mailgun@sandboxe3c453f8f4ff4ce7a3c0f3b450c31af1.mailgun.org>",
              "to": user_email,
              "subject": "Order " + str(order_id),
              "text": "Your order was successfully paid !"})