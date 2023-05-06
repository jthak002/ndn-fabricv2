import logging
import sys
import re
from ndn import utils, appv2, types
from ndn import encoding as enc


logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    style='{')

# accept and check the cli args
date_pattern = '^[0-9]{4}\\-[0-9]{1,2}\\-[0-9]{1,2}$$'
if len(sys.argv) != 2:
    print('Insufficient arguments - please run the program with the date in the following format: '
          '\'python huffpost_consumer.py YYYY-MM-DD\'')
    sys.exit(-1)

requester_date = sys.argv[1]
check_date = re.findall(date_pattern, requester_date)
if len(check_date) == 0:
    print('Insufficient arguments - please run the program with the date in the following format: '
          '\'python huffpost_consumer.py YYYY-MM-DD\'')
    sys.exit(-1)

interest_date = requester_date.replace('-', '/')
# initialize the NDNApp

app = appv2.NDNApp()


async def main():
    global requester_date
    try:
        name = enc.Name.from_str(f'/huffpost/archives/{interest_date}')
        print(f'Sending Interest {enc.Name.to_str(name)}, {enc.InterestParam(must_be_fresh=True, lifetime=60000)}')
        # TODO: Write a better validator
        data_name, content, pkt_context = await app.express(
            name, validator=appv2.pass_all,
            must_be_fresh=True, can_be_prefix=False, lifetime=60000, no_signature=True)

        print(f'Received Data Name: {enc.Name.to_str(data_name)}')
        print(pkt_context['meta_info'])
        print(bytes(content).decode() if content else None)
    except types.InterestNack as e:
        print(f'Nacked with reason={e.reason}')
    except types.InterestTimeout:
        print(f'Timeout')
    except types.InterestCanceled:
        print(f'Canceled')
    except types.ValidationFailure:
        print(f'Data failed to validate')
    finally:
        app.shutdown()


if __name__ == '__main__':
    app.run_forever(after_start=main())