from bs4 import BeautifulSoup
import datetime
import requests
import schedule
import time
from twilio.rest import Client


account_sid = 'AC4c195802a6bcf042dcefac3c5943f1cf'
auth_token = ''
client = Client(account_sid, auth_token)


def send_sms_msg(msg):
    """
    Send an SMS message from your Twilio number to your personal number

    msg - (str) the text message to send
    """
    message = client.messages \
        .create(
            body=msg,
            from_='+12029309754',
            to='+15134199125'
        )

    print(message.sid)


def send_health_check():
    """
    Send a text to indicate a healthily-running process
    """
    send_sms_msg('Health check')


def basic_check_for_product(url, disclaimer_msg):
    """
    Given a URL and a disclaimer message to check for, check if the disclaimer message is
    present on the page (i.e. check if the product is in stock)

    url - (str) full url to the product page to check
    disclaimer_message - (str) the disclaimer message that indicates whether the product is
        in stock
    """
    response = requests.get(url)

    if response.status_code != 200:
        send_sms_msg('ATTENTION NEEDED! Response other than 200 OK received from Ironmaster website '
                     '(got a ' + str(response.status_code) + ')')
        return

    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    span_for_stock_current = soup.find('span', {'class': 'stock'})

    # One of the strongest indicators is if this is not present
    disclaimer_msg_present = disclaimer_msg in html

    # Check for "Add to Cart" button:
    add_to_cart_button_current = soup.find('button', {'class', 'single_add_to_cart_button button alt'})

    possible_in_stock = False
    if span_for_stock_current:
        possible_in_stock = span_for_stock_current.text != 'OUT OF STOCK'

    add_to_cart_button_present = add_to_cart_button_current is not None

    print('possible_in_stock: ' + str(possible_in_stock))
    print('disclaimer_msg_present: ' + str(disclaimer_msg_present))
    print('add_to_cart_button_present: ' + str(add_to_cart_button_present))

    if possible_in_stock or not disclaimer_msg_present or add_to_cart_button_present:
        send_sms_msg('\n\nATTENTION!! An Ironmaster product is possibly in stock. The following criteria have been '
                     'met:'
                     '\n\nStock span text not \'OUT OF STOCK\': ' + str(possible_in_stock) +
                     '\nDisclaimer message is present: ' + str(disclaimer_msg_present) +
                     '\nAdd to cart button is present: ' + str(add_to_cart_button_present))


def check_for_dumbbells():
    print('\nInfo for super bench pro:')
    basic_check_for_product('https://www.ironmaster.com/products/quick-lock-adjustable-dumbbells-75/',
                            'item is out of stock until approx')


def check_for_super_bench():
    print('\nInfo for super bench:')
    basic_check_for_product('https://www.ironmaster.com/products/super-bench-adjustable-weightlifting-bench/',
                            'item is out of stock until approx')


def check_for_super_bench_pro():
    print('\nInfo for super bench pro:')
    basic_check_for_product('https://www.ironmaster.com/products/super-bench-pro/',
                            'item is out of stock until approx')


def main():
    send_sms_msg('Test message')
    start_time = time.time()
    schedule.every().day.at("08:00").do(send_health_check)
    schedule.every().day.at("15:00").do(send_health_check)
    schedule.every().day.at("23:00").do(send_health_check)

    while True:
        schedule.run_pending()
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print('\n---------------------------------------------\n')
        print(st + ' EST\n')
        check_for_dumbbells()
        check_for_super_bench()
        check_for_super_bench_pro()
        time.sleep(600.0 - ((time.time() - start_time) % 600.0))  # Checking every 10 minutes is plenty


if __name__ == '__main__':
    main()
