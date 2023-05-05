import logging

import ndn.types
from ndn.app import NDNApp

logger = logging.getLogger()
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = NDNApp()


async def main():
    try:
        data_name, meta_info, content = await app.express_interest(
            # Interest Name
            '/example/Ping2',
            must_be_fresh=True,
            can_be_prefix=False,
            # Interest lifetime in ms
            lifetime=6000)
        # Print out Data Name, MetaInfo and its content.
        logger.info(f'Received Data Name: { data_name}')
        logger.info(f'MEtadata Information {meta_info}')
        print(bytes(content) if content else None)
    except ndn.types.InterestNack as e:
        # A NACK is received
        print(f'Nacked with reason={e.reason}')
    except ndn.types.InterestTimeout:
        # Interest times out
        logger.error(f'Timeout')
    except ndn.types.InterestCanceled:
        # Connection to NFD is broken
        logger.error(f'Canceled')
    except ndn.types.ValidationFailure:
        # Validation failure
        logger.error(f'Data failed to validate')
    finally:
        app.shutdown()

app.run_forever(after_start=main())